import React, { useState } from 'react';
import axios from 'axios';

const UploadComponent: React.FC = () => {
  const [file, setFile] = useState<File | null>(null);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [technicalLevel, setTechnicalLevel] = useState("intermediate");

  const backendUrl = process.env.REACT_APP_BACKEND_URL || "http://localhost:5000/api/agent-detect";

  const handleUpload = async () => {
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);
    formData.append('technical_level', technicalLevel); // Send technical level
    setLoading(true);
    setResult(null);
    setError(null);

    try {
      const response = await axios.post(backendUrl, formData);
      setResult(response.data);
    } catch (err: any) {
      console.error(err);
      setError(err.response?.data?.error || 'Detection failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: '1rem', fontFamily: 'Arial' }}>
      <h2>🎯 Deepfake Detection Agent</h2>

      <input
        type="file"
        onChange={(e) => setFile(e.target.files?.[0] || null)}
        accept="image/*,video/*"
      />

      <select
        value={technicalLevel}
        onChange={(e) => setTechnicalLevel(e.target.value)}
        style={{ margin: '0 10px' }}
      >
        <option value="basic">Basic</option>
        <option value="intermediate">Intermediate</option>
        <option value="expert">Expert</option>
      </select>

      <button
        onClick={handleUpload}
        disabled={!file || loading}
        style={{ padding: '5px 15px' }}
      >
        {loading ? 'Detecting...' : 'Detect'}
      </button>

      {error && (
        <div style={{ marginTop: '1em', color: 'red' }}>
          <strong>Error:</strong> {error}
        </div>
      )}

      {result && (
        <div style={{ marginTop: '1em', backgroundColor: '#f0f0f0', padding: '1rem', borderRadius: '5px' }}>
          <p><strong>Type:</strong> {result.type}</p>
          <p><strong>Label:</strong> {result.label}</p>
          <p><strong>Confidence:</strong> {(result.confidence * 100).toFixed(2)}%</p>
          {result.explanation && (
            <p><strong>💡 LLM Explanation:</strong> {result.explanation}</p>
          )}
        </div>
      )}
    </div>
  );
};

export default UploadComponent;
