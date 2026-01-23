import os
import requests

API_KEY = os.getenv("GMI_API_KEY")
API_URL = os.getenv("GMI_API_URL", "https://api.gmi.cloud/v1/chat/completions")

SYSTEM_PROMPTS = {
    "analysis": "You are DeepShield AI, a forensic expert in deepfake detection. Provide detailed, professional analysis of detection results in clear, educational language.",
    "educational": "You are DeepShield AI, an expert educator in AI security and deepfake detection. Explain complex concepts clearly and adapt to the user's technical level.",
    "conversational": "You are DeepShield AI, a helpful AI security expert. Provide professional yet approachable responses about deepfakes, AI security, and digital forensics.",
    "threat_analysis": "You are DeepShield AI, a cybersecurity expert specializing in deepfake threats. Provide comprehensive threat landscape analysis."
}

FALLBACKS = {
    "analysis": "Based on multi-method forensic analysis, this content shows the indicated confidence level for authenticity assessment.",
    "educational": "Advanced computer vision and ML techniques were used, including facial landmarks, texture patterns, and frequency-based filters.",
    "threat_analysis": "Deepfakes pose threats to democracy, finance, and individual safety. Early detection is vital to protect digital ecosystems.",
    "conversational": "I'm DeepShield AI, your assistant in spotting and explaining deepfakes. Ask me anything about media security!"
}


def generate_response(prompt, intent="conversational", context=[]):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    messages = [
        {"role": "system", "content": SYSTEM_PROMPTS.get(intent, SYSTEM_PROMPTS["conversational"])}
    ] + context[-6:] + [{"role": "user", "content": prompt}]

    body = {
        "model": "gpt-3.5-turbo",
        "messages": messages,
        "max_tokens": 600,
        "temperature": 0.7
    }

    try:
        response = requests.post(API_URL, headers=headers, json=body)
        response.raise_for_status()
        data = response.json()
        return data.get("choices", [{}])[0].get("message", {}).get("content", FALLBACKS[intent])
    except Exception as e:
        print("LLM error:", e)
        return FALLBACKS[intent]


def generate_analysis_explanation(result, filename, technical_level="intermediate"):
    confidence = f"{result.get('confidence', 0) * 100:.1f}"
    is_deepfake = "DEEPFAKE DETECTED" if result.get("label", "").lower() == "fake" else "AUTHENTIC CONTENT"
    artifacts = result.get("artifacts", [])

    artifact_summary = ", ".join(a.get("type", "unknown") for a in artifacts) or "None detected"
    artifact_details = "; ".join(f"{a.get('type')}: {a.get('score', 0)*100:.1f}%" for a in artifacts) or "No artifacts to report."

    prompt = (
        f"Analysis Results for \"{filename}\":\n"
        f"- Classification: {is_deepfake}\n"
        f"- Confidence Score: {confidence}%\n"
        f"- Detection Methods: {artifact_summary}\n"
        f"- Key Findings: {artifact_details}\n\n"
        f"User Technical Level: {technical_level}\n\n"
        f"Generate a professional forensic analysis report explaining these findings. Include:\n"
        f"1. Executive summary\n"
        f"2. Explanation of detection methods used\n"
        f"3. Key evidence found\n"
        f"4. Confidence assessment\n"
        f"5. Recommendations\n\n"
        f"Adapt the technical depth to the user's level: {technical_level}."
    )

    return generate_response(prompt, "analysis")
