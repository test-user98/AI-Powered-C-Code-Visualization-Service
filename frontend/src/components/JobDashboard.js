import React, { useState, useEffect, useCallback } from 'react';
import { api } from '../api';

function JobDashboard({ onJobSelected, onCreateJob, refreshTrigger }) {
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [pollingJobs, setPollingJobs] = useState(new Set());

  const fetchJobs = useCallback(async () => {
    try {
      const jobsData = await api.getJobs();
      setJobs(jobsData);
      setError(null);

      // Start polling for in-progress jobs
      const inProgressJobIds = jobsData
        .filter(job => job.status === 'in_progress')
        .map(job => job.id);

      setPollingJobs(new Set(inProgressJobIds));
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, []);

  const pollJobProgress = useCallback(async (jobId) => {
    try {
      const jobDetails = await api.getJob(jobId);
      setJobs(prevJobs =>
        prevJobs.map(job =>
          job.id === jobId ? jobDetails : job
        )
      );

      // Stop polling if job is complete
      if (jobDetails.status !== 'in_progress') {
        setPollingJobs(prev => {
          const newSet = new Set(prev);
          newSet.delete(jobId);
          return newSet;
        });
      }
    } catch (err) {
      console.error(`Error polling job ${jobId}:`, err);
    }
  }, []);

  useEffect(() => {
    fetchJobs();
  }, [refreshTrigger]); // Fetch jobs when component mounts or refresh is triggered

  useEffect(() => {
    if (pollingJobs.size === 0) return;

    // Set up polling interval
    const interval = setInterval(() => {
      pollingJobs.forEach(jobId => pollJobProgress(jobId));
    }, 2000); // Poll every 2 seconds

    return () => clearInterval(interval);
  }, [pollingJobs, pollJobProgress]); // Include pollJobProgress in dependencies

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
