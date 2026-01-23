from detector import detect_image, detect_video
from llm_service import generate_analysis_explanation

def deepfake_agent(file, file_type, technical_level="intermediate"):
    """
    Perform deepfake detection and get a natural language explanation from LLM.

    Args:
        file: Uploaded image or video file
        file_type: MIME type (e.g., image/jpeg, video/mp4)
        technical_level: User's technical understanding (basic, intermediate, expert)

    Returns:
        dict with detection result + LLM explanation
    """

    # Step 1: Deepfake detection
    if file_type.startswith("image/"):
        detection_result = detect_image(file)
    elif file_type.startswith("video/"):
        detection_result = detect_video(file)
    else:
        return {"error": "Unsupported file type"}

    # Step 2: LLM Explanation
    filename = getattr(file, 'filename', 'uploaded_file')
    try:
        explanation = generate_analysis_explanation(detection_result, filename, technical_level)
    except Exception as e:
        print("LLM explanation failed:", str(e))
        explanation = "LLM explanation failed. Core detection succeeded."

    # Step 3: Combine results
    detection_result["explanation"] = explanation
    return detection_result
