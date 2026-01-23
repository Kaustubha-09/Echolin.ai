import torch
from transformers import AutoImageProcessor, AutoModelForImageClassification
from PIL import Image
import os
import glob

def load_model():
    image_processor = AutoImageProcessor.from_pretrained('ashish-001/deepfake-detection-using-ViT')
    model = AutoModelForImageClassification.from_pretrained('ashish-001/deepfake-detection-using-ViT')
    return image_processor, model

def predict_single_image(image_path, image_processor, model):
    try:
        image = Image.open(image_path)
        inputs = image_processor(images=image, return_tensors="pt")
        with torch.no_grad():
            outputs = model(**inputs)
            logits = outputs.logits
            pred = torch.argmax(logits, dim=1).item()
            confidence = torch.nn.functional.softmax(logits, dim=1)[0][pred].item()
        label = 'Real' if pred == 1 else 'Fake'
        return label, confidence
    except Exception as e:
        print(f"Error processing {image_path}: {str(e)}")
        return None, None
    

def predict_batch_images(image_folder, image_processor, model, extensions=['jpg', 'jpeg', 'png', 'bmp']):
    """Predict multiple images from a folder"""
    results = []
    
    # Get all image files
    image_files = []
    for ext in extensions:
        image_files.extend(glob.glob(os.path.join(image_folder, f"*.{ext}"), recursive=False))
        image_files.extend(glob.glob(os.path.join(image_folder, f"*.{ext.upper()}"), recursive=False))
    
    # Remove duplicates that might occur on case-insensitive filesystems
    image_files = list(set(image_files))
    print(f"Found {len(image_files)} images to process")
    
    for i, image_path in enumerate(image_files, 1):
        print(f"Processing image {i}/{len(image_files)}: {os.path.basename(image_path)}")
        
        label, confidence = predict_single_image(image_path, image_processor, model)
        
        if label is not None:
            results.append({
                'image_path': image_path,
                'filename': os.path.basename(image_path),
                'prediction': label,
                'confidence': confidence
            })
            print(f"  Result: {label} (confidence: {confidence:.3f})")
        else:
            print(f"  Failed to process")
    
    return results

def save_results(results, output_file='deepfake_results.txt'):
    """Save results to a text file"""
    with open(output_file, 'w') as f:
        f.write("Deepfake Detection Results\n")
        f.write("=" * 50 + "\n\n")
        
        for result in results:
            f.write(f"File: {result['filename']}\n")
            f.write(f"Prediction: {result['prediction']}\n")
            f.write(f"Confidence: {result['confidence']:.3f}\n")
            f.write("-" * 30 + "\n")
    
    print(f"Results saved to {output_file}")

image_processor, model = load_model()
image_folder = "./self_test_images/Fake"

if os.path.exists(image_folder):
    print(f"\nTesting images from folder: {image_folder}")
    results = predict_batch_images(image_folder, image_processor, model)
    
    # Print summary
    if results:
        real_count = sum(1 for r in results if r['prediction'] == 'Real')
        fake_count = sum(1 for r in results if r['prediction'] == 'Fake')
        
        print(f"\nSummary:")
        print(f"Total images processed: {len(results)}")
        print(f"Real images: {real_count}")
        print(f"Fake images: {fake_count}")
        
        # Save results
        save_results(results)

