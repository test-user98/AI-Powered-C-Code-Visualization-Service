import React, { useState } from 'react';
import { api } from '../api';

function JobCreation({ onJobCreated }) {
  const [code, setCode] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!code.trim()) {
      setError('Please enter some C code');
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const result = await api.createJob(code);
      onJobCreated(result.job_id);
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  const handleFileUpload = (e) => {
    const file = e.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (event) => {
        setCode(event.target.result);
      };
      reader.readAsText(file);
    }
  };

  return (
    <div className="card">
      <h2 className="page-title">Analyze C Code</h2>

      <form onSubmit={handleSubmit}>
        <div className="file-input">
          <input
            type="file"
            accept=".c,.h"
            onChange={handleFileUpload}
            id="file-upload"
          />
          <label htmlFor="file-upload">Choose .c file</label>
          <span style={{ marginLeft: '10px', color: '#666' }}>or paste code below</span>
        </div>

        <textarea
          className="input"
          value={code}
          onChange={(e) => setCode(e.target.value)}
          placeholder="Paste your C code here..."
          disabled={isLoading}
        />

        {error && <div className="error">{error}</div>}

        <button
          type="submit"
          className="button"
          disabled={isLoading || !code.trim()}
        >
          {isLoading ? 'Analyzing...' : 'Analyze Code'}
        </button>
      </form>
    </div>
  );
}

export default JobCreation;
