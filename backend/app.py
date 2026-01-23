from flask import Flask, request, jsonify
from flask_cors import CORS
from detector import detect_image, detect_video
from agent import deepfake_agent  # Includes LLM explanation

app = Flask(__name__)
CORS(app)

# Optional: limit upload size to 100MB
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB

# Basic detection without LLM explanation
@app.route("/api/detect", methods=["POST"])
def detect():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['file']
    file_type = file.content_type

    try:
        if file_type.startswith("image/"):
            result = detect_image(file)
        elif file_type.startswith("video/"):
            result = detect_video(file)
        else:
            return jsonify({"error": "Unsupported file type"}), 400

        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Enhanced detection with LLM explanation
@app.route("/api/agent-detect", methods=["POST"])
def agent_detect():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['file']
    file_type = file.content_type

    try:
        result = deepfake_agent(file, file_type)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5000)
