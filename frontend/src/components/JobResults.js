import React, { useState, useEffect, useCallback } from 'react';
import { api } from '../api';
import MermaidDiagram from './MermaidDiagram';

function JobResults({ jobId }) {
  const [job, setJob] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchJobDetails = useCallback(async () => {
    try {
      const jobData = await api.getJob(jobId);
      setJob(jobData);
      setError(null);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [jobId]);

  useEffect(() => {
    fetchJobDetails();
  }, [fetchJobDetails]);

  if (loading) {
    return <div className="loading">Loading job results...</div>;
  }

  if (error) {
    return <div className="error">Error: {error}</div>;
  }

  if (!job) {
    return <div className="error">Job not found</div>;
  }

  return (
    <div>
      <div className="card">
        <h2 className="page-title">Analysis Results</h2>
        <div className="job-meta">
          <strong>Job ID:</strong> {job.id}<br />
          <strong>Status:</strong> <span className={`job-status status-${job.status}`}>
            {job.status.replace('_', ' ')}
          </span><br />
          <strong>Completed:</strong> {new Date(job.updated_at).toLocaleString()}<br />
          <strong>Functions Found:</strong> {job.functions.length}
        </div>
      </div>

      {job.functions.length === 0 ? (
        <div className="card">
          <p>No functions were found in the code, or analysis is still in progress.</p>
        </div>
      ) : (
        <div className="function-grid">
          {job.functions.map((func, index) => (
            <div key={index} className="function-item">
              <div className="function-name">
                📋 {func.name}()
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
                <div>
                  <h4>Mermaid Syntax:</h4>
                  <div className="code-container">
                    {func.mermaid_diagram}
                  </div>
                </div>

                <div>
                  <h4>Visual Flowchart:</h4>
                  <MermaidDiagram chart={func.mermaid_diagram} />
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default JobResults;
