from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
from datetime import datetime
import uuid
from supabase import create_client, Client
import jwt
from typing import Optional
import asyncio
import tempfile
from deepfake_image import load_model, predict_single_image, predict_batch_images

image_processor, model = load_model()

# Initialize FastAPI app
app = FastAPI(title="File Analysis API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration - Set these as environment variables
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")  # Service role key for storage operations
JWT_SECRET = os.getenv("JWT_SECRET", "your-secret-key")
STORAGE_BUCKET = os.getenv("STORAGE_BUCKET", "uploads")  # Supabase storage bucket name

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
# Service client for storage operations (has elevated permissions)
supabase_service: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

# Pydantic models
class UploadUrlRequest(BaseModel):
    filename: str
    content_type: str

class UploadUrlResponse(BaseModel):
    upload_url: str
    file_path: str

class UploadCompleteRequest(BaseModel):
    file_path: str
    user_token: str

class DetectionResult(BaseModel):
    detection_id: str
    result: dict
    confidence: float
    timestamp: datetime

class AnalysisResponse(BaseModel):
    success: bool
    detection_result: DetectionResult
    message: str

# JWT token verification
def verify_token(token: str) -> dict:
    """Verify JWT token and return user data"""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

async def run_analysis_model(file_path: str) -> dict:
    # Download the file from Supabase Storage temporarily
    download_response = supabase_service.storage.from_(STORAGE_BUCKET).download(file_path)
    if hasattr(download_response, 'error') and download_response.error:
        raise Exception(f"Download failed: {download_response.error}")

    # Save to a temporary local file
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file_path)[-1]) as tmp_file:
        tmp_file.write(download_response)
        tmp_file_path = tmp_file.name

    # Run prediction
    label, confidence = predict_batch_images(tmp_file_path, image_processor, model)

    # Optionally delete temp file
    os.remove(tmp_file_path)

    if label is None:
        raise Exception("Prediction failed")

    return {
        "result": {
            "label": label
        },
        "confidence": confidence
    }

@app.get("/")
async def root():
    return {"message": "File Analysis API is running"}

@app.post("/generate-upload-url", response_model=UploadUrlResponse)
async def generate_upload_url(request: UploadUrlRequest):
    """Generate a signed URL for Supabase Storage upload"""
    try:
        # Generate unique file path
        file_extension = request.filename.split('.')[-1] if '.' in request.filename else ''
        file_path = f"uploads/{uuid.uuid4()}.{file_extension}"
        
        # Create signed upload URL for Supabase Storage
        # Note: Supabase doesn't have pre-signed URLs like S3, so we'll use a different approach
        # We'll return the file path and handle upload through our endpoint
        
        upload_url = f"/upload-file"  # Our own upload endpoint
        
        return UploadUrlResponse(
            upload_url=upload_url,
            file_path=file_path
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating upload URL: {str(e)}")

@app.post("/upload-file")
async def upload_file(
    file: UploadFile = File(...),
    user_token: str = Form(...),
    file_path: str = Form(...)
):
    """Upload file directly to Supabase Storage"""
    try:
        # Verify user token
        user_data = verify_token(user_token)
        user_id = user_data.get("user_id")
        
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid user token")
        
        # Read file content
        file_content = await file.read()
        
        # Upload to Supabase Storage
        result = supabase_service.storage.from_(STORAGE_BUCKET).upload(
            path=file_path,
            file=file_content,
            file_options={
                "content-type": file.content_type,
                "upsert": True
            }
        )
        
        if hasattr(result, 'error') and result.error:
            raise HTTPException(status_code=500, detail=f"Upload failed: {result.error}")
        
        return {
            "success": True,
            "file_path": file_path,
            "message": "File uploaded successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading file: {str(e)}")

@app.post("/upload-complete", response_model=AnalysisResponse)
async def upload_complete(request: UploadCompleteRequest):
    """Process uploaded file and run analysis"""
    try:
        # Verify user token
        user_data = verify_token(request.user_token)
        user_id = user_data.get("user_id")
        
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid user token")
        
        # Verify file exists in Supabase Storage
        try:
            file_info = supabase_service.storage.from_(STORAGE_BUCKET).info(request.file_path)
            if hasattr(file_info, 'error') and file_info.error:
                raise HTTPException(status_code=404, detail="File not found in storage")
        except Exception:
            raise HTTPException(status_code=404, detail="File not found in storage")
        
        # Run analysis model
        analysis_result = await run_analysis_model(request.file_path)
        
        # Create detection result
        detection_id = str(uuid.uuid4())
        detection_result = DetectionResult(
            detection_id=detection_id,
            result=analysis_result["result"],
            confidence=analysis_result["confidence"],
            timestamp=datetime.utcnow()
        )
        
        # Store result in Supabase database
        detection_record = {
            "id": detection_id,
            "user_id": user_id,
            "file_path": request.file_path,
            "storage_bucket": STORAGE_BUCKET,
            "analysis_result": analysis_result["result"],
            "confidence": analysis_result["confidence"],
            "created_at": detection_result.timestamp.isoformat(),
            "status": "completed"
        }
        
        result = supabase.table("detections").insert(detection_record).execute()
        
        if not result.data:
            raise HTTPException(status_code=500, detail="Failed to save detection record")
        
        return AnalysisResponse(
            success=True,
            detection_result=detection_result,
            message="Analysis completed successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing upload: {str(e)}")

@app.post("/upload-and-analyze")
async def upload_and_analyze(
    file: UploadFile = File(...),
    user_token: str = Form(...)
):
    """Single endpoint to upload file and run analysis"""
    try:
        # Verify user token
        user_data = verify_token(user_token)
        user_id = user_data.get("user_id")
        
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid user token")
        
        # Generate unique file path
        file_extension = file.filename.split('.')[-1] if '.' in file.filename else ''
        file_path = f"uploads/{uuid.uuid4()}.{file_extension}"
        
        # Read file content
        file_content = await file.read()
        
        # Upload to Supabase Storage
        upload_result = supabase_service.storage.from_(STORAGE_BUCKET).upload(
            path=file_path,
            file=file_content,
            file_options={
                "content-type": file.content_type,
                "upsert": True
            }
        )
        
        if hasattr(upload_result, 'error') and upload_result.error:
            raise HTTPException(status_code=500, detail=f"Upload failed: {upload_result.error}")
        
        # Run analysis model
        analysis_result = await run_analysis_model(file_path)
        
        # Create detection result
        detection_id = str(uuid.uuid4())
        detection_result = DetectionResult(
            detection_id=detection_id,
            result=analysis_result["result"],
            confidence=analysis_result["confidence"],
            timestamp=datetime.utcnow()
        )
        
        # Store result in Supabase database
        detection_record = {
            "id": detection_id,
            "user_id": user_id,
            "file_path": file_path,
            "storage_bucket": STORAGE_BUCKET,
            "analysis_result": analysis_result["result"],
            "confidence": analysis_result["confidence"],
            "created_at": detection_result.timestamp.isoformat(),
            "status": "completed"
        }
        
        result = supabase.table("detections").insert(detection_record).execute()
        
        if not result.data:
            raise HTTPException(status_code=500, detail="Failed to save detection record")
        
        return AnalysisResponse(
            success=True,
            detection_result=detection_result,
            message="Upload and analysis completed successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in upload and analysis: {str(e)}")

@app.get("/detections/{user_id}")
async def get_user_detections(user_id: str, token: str):
    """Get all detections for a user"""
    try:
        # Verify token
        user_data = verify_token(token)
        if user_data.get("user_id") != user_id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Fetch detections from Supabase
        result = supabase.table("detections").select("*").eq("user_id", user_id).execute()
        
        return {
            "success": True,
            "detections": result.data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching detections: {str(e)}")

@app.get("/detection/{detection_id}")
async def get_detection_details(detection_id: str, token: str):
    """Get details of a specific detection"""
    try:
        # Verify token
        user_data = verify_token(token)
        user_id = user_data.get("user_id")
        
        # Fetch detection from Supabase
        result = supabase.table("detections").select("*").eq("id", detection_id).execute()
        
        if not result.data:
            raise HTTPException(status_code=404, detail="Detection not found")
        
        detection = result.data[0]
        
        # Verify user owns this detection
        if detection["user_id"] != user_id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        return {
            "success": True,
            "detection": detection
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching detection: {str(e)}")

@app.get("/file/{file_path}")
async def get_file_url(file_path: str, token: str):
    """Get signed URL to access file from Supabase Storage"""
    try:
        # Verify token
        user_data = verify_token(token)
        user_id = user_data.get("user_id")
        
        # Verify user has access to this file (check if they own a detection with this file)
        result = supabase.table("detections").select("*").eq("user_id", user_id).eq("file_path", file_path).execute()
        
        if not result.data:
            raise HTTPException(status_code=403, detail="Access denied to this file")
        
        # Create signed URL for file access
        signed_url = supabase_service.storage.from_(STORAGE_BUCKET).create_signed_url(
            path=file_path,
            expires_in=3600  # 1 hour
        )
        
        if hasattr(signed_url, 'error') and signed_url.error:
            raise HTTPException(status_code=500, detail="Failed to create signed URL")
        
        return {
            "success": True,
            "signed_url": signed_url['signedURL']
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting file URL: {str(e)}")

# Health check endpoint
@app.get("/health")
async def health_check():
    try:
        # Test Supabase connection
        supabase.table("detections").select("id").limit(1).execute()
        supabase_status = "connected"
    except:
        supabase_status = "disconnected"
    
    try:
        # Test Supabase Storage connection
        supabase_service.storage.list_buckets()
        storage_status = "connected"
    except:
        storage_status = "disconnected"
    
    return {
        "status": "healthy" if supabase_status == "connected" and storage_status == "connected" else "degraded",
        "timestamp": datetime.utcnow().isoformat(),
        "services": {
            "supabase_db": supabase_status,
            "supabase_storage": storage_status
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)