import React, { useState, useEffect, useCallback, useRef } from 'react';
import { api } from '../api';

function JobDashboard({ onJobSelected, onCreateJob, refreshTrigger }) {
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const wsRef = useRef(null);

  const fetchJobs = useCallback(async () => {
    try {
      const jobsData = await api.getJobs();
      setJobs(jobsData);
      setError(null);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, []);

  const connectWebSocket = useCallback(() => {
    const wsUrl = `ws://localhost:8080/ws/jobs`.replace('http', 'ws');
    const ws = new WebSocket(wsUrl);

    ws.onopen = () => {
      console.log('WebSocket connected for job updates');
    };

    ws.onmessage = (event) => {
      try {
        const update = JSON.parse(event.data);
        if (update.type === 'job_update') {
          // Update job status in the jobs list
          setJobs(prevJobs =>
            prevJobs.map(job =>
              job.id === update.job_id
                ? { ...job, status: update.status, processed_functions: update.processed_functions, updated_at: update.updated_at }
                : job
            )
          );
        }
      } catch (err) {
        console.error('Failed to parse WebSocket message:', err);
      }
    };

    ws.onclose = () => {
      console.log('WebSocket disconnected, will reconnect...');
      // Auto-reconnect after 5 seconds
      setTimeout(connectWebSocket, 5000);
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    wsRef.current = ws;
  }, []);


  useEffect(() => {
    fetchJobs();
    connectWebSocket();
  }, [refreshTrigger, fetchJobs, connectWebSocket]); // Fetch jobs and connect WebSocket

  useEffect(() => {
    // Cleanup WebSocket on unmount
    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, []);

  const handleJobClick = (job) => {
    if (job.status === 'success') {
      onJobSelected(job.id);
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleString();
  };

  if (loading) {
    return <div className="loading">Loading jobs...</div>;
  }

  if (error) {
    return <div className="error">Error: {error}</div>;
  }

  return (
    <div>
      <div className="card">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
          <h2 className="page-title">Job Dashboard</h2>
          <button onClick={onCreateJob} className="button">
            New Analysis
          </button>
        </div>

        {jobs.length === 0 ? (
          <p>No jobs found. Create your first analysis!</p>
        ) : (
          <ul className="job-list">
            {jobs.map(job => (
              <li
                key={job.id}
                className={`job-item ${job.status}`}
                onClick={() => handleJobClick(job)}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                  <div>
                    <div className="job-meta">
                      ID: {job.id.slice(-8)} • {formatDate(job.created_at)}
                    </div>
                    <div style={{ marginBottom: '8px' }}>
                      <span className={`job-status status-${job.status}`}>
                        {job.status.replace('_', ' ')}
                      </span>
                    </div>
                    {job.status === 'in_progress' && (
                      <div className="job-progress">
                        Analyzing... ({job.processed_functions} / {job.total_functions} functions processed)
                      </div>
                    )}
                    {job.status === 'success' && (
                      <div className="job-progress">
                        ✅ Completed: {job.total_functions} functions analyzed
                      </div>
                    )}
                    {job.status === 'failed' && job.error_message && (
                      <div style={{ color: '#dc3545', fontSize: '14px' }}>
                        ❌ {job.error_message}
                      </div>
                    )}
                  </div>
                  {job.status === 'success' && (
                    <div style={{ color: '#28a745', fontSize: '24px' }}>👁️</div>
                  )}
                </div>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}

export default JobDashboard;
