from PIL import Image
import torch
from transformers import AutoImageProcessor, AutoModelForImageClassification
import cv2
import tempfile

# Load pretrained image classification model
image_processor = AutoImageProcessor.from_pretrained('ashish-001/deepfake-detection-using-ViT')
model = AutoModelForImageClassification.from_pretrained('ashish-001/deepfake-detection-using-ViT')

def detect_image(file) -> dict:
    try:
        image = Image.open(file).convert("RGB")
        inputs = image_processor(images=image, return_tensors="pt")

        with torch.no_grad():
            outputs = model(**inputs)

        logits = outputs.logits
        predicted_class_idx = logits.argmax(-1).item()
        label = model.config.id2label[predicted_class_idx]
        confidence = torch.softmax(logits, dim=1).max().item()

        return {
            "type": "image",
            "label": label,
            "confidence": confidence,
            "artifacts": [{"type": "face_texture", "score": confidence * 100}]
        }
    except Exception as e:
        return {"error": f"Image detection failed: {str(e)}"}

def detect_video(file) -> dict:
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_video:
            temp_video.write(file.read())
            temp_video_path = temp_video.name

        cap = cv2.VideoCapture(temp_video_path)
        frames_analyzed = 0
        results = []

        while frames_analyzed < 10 and cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            inputs = image_processor(images=image, return_tensors="pt")

            with torch.no_grad():
                outputs = model(**inputs)

            logits = outputs.logits
            predicted_class_idx = logits.argmax(-1).item()
            label = model.config.id2label[predicted_class_idx]
            confidence = torch.softmax(logits, dim=1).max().item()
            results.append((label, confidence))
            frames_analyzed += 1

        cap.release()

        final_label = max(set([r[0] for r in results]), key=lambda l: sum(1 for r in results if r[0] == l))
        avg_confidence = sum([r[1] for r in results if r[0] == final_label]) / len(results)

        return {
            "type": "video",
            "label": final_label,
            "confidence": avg_confidence,
            "artifacts": [{"type": "frame_consistency", "score": avg_confidence * 100}]
        }
    except Exception as e:
        return {"error": f"Video detection failed: {str(e)}"}
