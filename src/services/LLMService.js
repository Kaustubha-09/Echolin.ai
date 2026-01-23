class LLMService {
  constructor() {
    this.apiKey = process.env.REACT_APP_GMI_API_KEY;
    this.apiUrl = process.env.REACT_APP_GMI_API_URL || 'https://api.gmi.cloud/v1/chat/completions';
  }

  async generateResponse(prompt, context = [], intent = 'general') {
    try {
      const systemPrompts = {
        analysis: 'You are DeepShield AI, a forensic expert in deepfake detection. Provide detailed, professional analysis of detection results in clear, educational language.',
        educational: 'You are DeepShield AI, an expert educator in AI security and deepfake detection. Explain complex concepts clearly and adapt to the user\'s technical level.',
        conversational: 'You are DeepShield AI, a helpful AI security expert. Provide professional yet approachable responses about deepfakes, AI security, and digital forensics.',
        threat_analysis: 'You are DeepShield AI, a cybersecurity expert specializing in deepfake threats. Provide comprehensive threat landscape analysis.'
      };

      const systemMessage = systemPrompts[intent] || systemPrompts.conversational;

      const response = await fetch(this.apiUrl, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${this.apiKey}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          model: 'gpt-3.5-turbo',
          messages: [
            {
              role: 'system',
              content: systemMessage
            },
            ...context.slice(-6),
            {
              role: 'user',
              content: prompt
            }
          ],
          max_tokens: 600,
          temperature: 0.7
        })
      });

      if (!response.ok) {
        throw new Error(`API Error: ${response.status}`);
      }

      const data = await response.json();
      return data.choices[0].message.content;

    } catch (error) {
      console.error('LLM API Error:', error);
      return this.getFallbackResponse(prompt, intent);
    }
  }

  getFallbackResponse(prompt, intent) {
    const fallbacks = {
      analysis: "Based on comprehensive multi-method analysis using facial geometry, edge artifacts, texture patterns, and frequency domain signatures, this content shows the indicated confidence level for authenticity assessment.",
      educational: "I use advanced computer vision and machine learning techniques to detect deepfakes. My multi-method approach analyzes facial landmarks, edge patterns, texture consistency, and frequency domain artifacts.",
      threat_analysis: "Deepfakes pose significant threats to democratic processes, financial security, and personal safety. Early detection and verification systems are critical for maintaining digital trust.",
      conversational: "I'm DeepShield AI, your intelligent deepfake detection specialist. I can analyze media files and educate you about AI security threats. How can I help you today?"
    };

    return fallbacks[intent] || fallbacks.conversational;
  }

  async generateAnalysisExplanation(results, fileName, technicalLevel = 'intermediate') {
    const { confidence, isDeepfake, artifacts } = results;
    
    const prompt = `
Analysis Results for "${fileName}":
- Classification: ${isDeepfake ? 'DEEPFAKE DETECTED' : 'AUTHENTIC CONTENT'}
- Confidence Score: ${confidence.toFixed(1)}%
- Detection Methods: ${artifacts.map(a => a.type).join(', ')}
- Key Findings: ${artifacts.map(a => `${a.type}: ${a.score.toFixed(1)}%`).join('; ')}

User Technical Level: ${technicalLevel}

Generate a professional forensic analysis report explaining these findings. Include:
1. Executive summary of the results
2. Explanation of detection methods used
3. Key evidence found
4. Confidence assessment
5. Recommendations

Adapt the technical depth to the user's level: ${technicalLevel}.
`;

    return await this.generateResponse(prompt, [], 'analysis');
  }
}

export default new LLMService();