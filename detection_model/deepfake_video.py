import torch
import numpy as np
from transformers import VideoMAEImageProcessor, VideoMAEForVideoClassification
import cv2
from torchvision import transforms
import os
from pathlib import Path
import json


class DeepfakeDetector:
    def __init__(self, model_name="shylhy/videomae-large-finetuned-deepfake-subset"):
        """
        Initialize the deepfake detector with the VideoMAE model
        """
        print("Loading model and processor...")
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        # Load the model and image processor
        self.model = VideoMAEForVideoClassification.from_pretrained(model_name)
        self.image_processor = VideoMAEImageProcessor.from_pretrained(model_name)
        
        self.model.to(self.device)
        self.model.eval()
        
        # Get model configuration
        self.num_frames = self.model.config.num_frames
        self.image_mean = torch.tensor(self.image_processor.image_mean)
        self.image_std = torch.tensor(self.image_processor.image_std)
        
        # Get image size
        if "shortest_edge" in self.image_processor.size:
            self.height = self.width = self.image_processor.size["shortest_edge"]
        else:
            self.height = self.image_processor.size["height"]
            self.width = self.image_processor.size["width"]
        
        print(f"Model loaded on {self.device}")
        print(f"Expected frames: {self.num_frames}")
        print(f"Expected resolution: {self.height}x{self.width}")

    def uniform_temporal_subsample(self, frames, num_samples):
        """
        Uniformly subsample frames from video
        """
        total_frames = len(frames)
        if total_frames <= num_samples:
            # If we have fewer frames than needed, repeat the last frame
            indices = list(range(total_frames))
            while len(indices) < num_samples:
                indices.append(total_frames - 1)
        else:
            # Uniformly sample frames
            indices = np.linspace(0, total_frames - 1, num_samples, dtype=int)
        
        return [frames[i] for i in indices]

    def preprocess_video(self, video_path):
        """
        Preprocess video for the model without PyTorchVideo dependency
        """
        # Read video
        cap = cv2.VideoCapture(video_path)
        frames = []
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            # Convert BGR to RGB
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frames.append(frame)
        
        cap.release()
        
        if len(frames) == 0:
            raise ValueError(f"Could not read any frames from {video_path}")
        
        print(f"Total frames in video: {len(frames)}")
        
        # Uniformly sample the required number of frames
        sampled_frames = self.uniform_temporal_subsample(frames, self.num_frames)
        
        # Convert to tensor and preprocess
        processed_frames = []
        
        # Define transforms
        resize_transform = transforms.Resize((self.height, self.width))
        
        for frame in sampled_frames:
            # Convert to tensor and normalize to [0, 1]
            frame_tensor = torch.from_numpy(frame).float() / 255.0
            
            # Rearrange from HWC to CHW
            frame_tensor = frame_tensor.permute(2, 0, 1)
            
            # Resize
            frame_tensor = resize_transform(frame_tensor)
            
            # Normalize with model's expected mean and std
            frame_tensor = transforms.functional.normalize(
                frame_tensor, 
                self.image_mean.tolist(), 
                self.image_std.tolist()
            )
            
            processed_frames.append(frame_tensor)
        
        # Stack frames: (num_frames, channels, height, width)
        video_tensor = torch.stack(processed_frames)
        
        return video_tensor.unsqueeze(0)  # Add batch dimension

    def predict_single_video(self, video_path):
        """
        Predict if a single video is deepfake or real
        """
        try:
            # Preprocess video
            pixel_values = self.preprocess_video(video_path)
            pixel_values = pixel_values.to(self.device)
            
            # Run inference
            with torch.no_grad():
                outputs = self.model(pixel_values=pixel_values)
                logits = outputs.logits
                probabilities = torch.nn.functional.softmax(logits, dim=-1)
            
            # Get prediction
            predicted_class_idx = logits.argmax(-1).item()
            confidence = probabilities.max().item()
            
            # Get all class probabilities
            all_probs = probabilities.cpu().numpy().flatten()
            
            # Map to labels - check model config for actual labels
            if hasattr(self.model.config, 'id2label') and self.model.config.id2label:
                label = self.model.config.id2label[predicted_class_idx]
            else:
                # Fallback assumption: 0=real, 1=fake
                label = "FAKE" if predicted_class_idx == 1 else "REAL"
            
            return {
                "video_path": video_path,
                "prediction": label,
                "confidence": confidence,
                "predicted_class_idx": predicted_class_idx,
                "all_probabilities": all_probs.tolist(),
                "raw_logits": logits.cpu().numpy().flatten().tolist()
            }
            
        except Exception as e:
            return {
                "video_path": video_path,
                "error": str(e)
            }

    def predict_batch(self, video_paths):
        """
        Predict multiple videos
        """
        results = []
        for i, video_path in enumerate(video_paths):
            print(f"Processing video {i+1}/{len(video_paths)}: {os.path.basename(video_path)}")
            result = self.predict_single_video(video_path)
            results.append(result)
            
            if "error" not in result:
                print(f"  -> {result['prediction']} (confidence: {result['confidence']:.3f})")
            else:
                print(f"  -> ERROR: {result['error']}")
        
        return results

    def predict_directory(self, directory_path, extensions=None):
        """
        Predict all videos in a directory
        """
        if extensions is None:
            extensions = ['.mp4']
        
        directory = Path(directory_path)
        video_files = []
        
        for ext in extensions:
            video_files.extend(directory.glob(f"*{ext}"))
            video_files.extend(directory.glob(f"*{ext.upper()}"))
        
        video_paths = [str(path) for path in video_files]
        print(f"Found {len(video_paths)} video files")
        
        if len(video_paths) == 0:
            print("No video files found in the directory!")
            return []
        
        return self.predict_batch(video_paths)

    def save_results(self, results, output_file="deepfake_results.json"):
        """
        Save results to JSON file
        """
        with open(output_file, "w") as f:
            json.dump(results, f, indent=2, default=str)
        print(f"Results saved to {output_file}")

    def print_summary(self, results):
        """
        Print summary of results
        """
        if not results:
            print("No results to summarize.")
            return
        
        total_videos = len(results)
        successful_predictions = len([r for r in results if "error" not in r])
        errors = total_videos - successful_predictions
        
        print(f"\n--- SUMMARY ---")
        print(f"Total videos processed: {total_videos}")
        print(f"Successful predictions: {successful_predictions}")
        print(f"Errors: {errors}")
        
        if successful_predictions > 0:
            successful_results = [r for r in results if "error" not in r]
            fake_count = len([r for r in successful_results if "FAKE" in r['prediction'].upper()])
            real_count = successful_predictions - fake_count
            
            print(f"Predicted as FAKE: {fake_count}")
            print(f"Predicted as REAL: {real_count}")
            
            avg_confidence = sum(r['confidence'] for r in successful_results) / len(successful_results)
            print(f"Average confidence: {avg_confidence:.3f}")


detector = DeepfakeDetector()

print("\n=== Example 3: Directory Prediction ===")
results = detector.predict_directory("./videos")
detector.print_summary(results)
detector.save_results(results, "directory_results.json")

print("\nModel configuration:")
print(f"- Number of classes: {detector.model.config.num_labels}")
if hasattr(detector.model.config, 'id2label') and detector.model.config.id2label:
    print(f"- Labels: {detector.model.config.id2label}")

