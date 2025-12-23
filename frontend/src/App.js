import React, { useState } from 'react';
import JobCreation from './components/JobCreation';
import JobDashboard from './components/JobDashboard';
import JobResults from './components/JobResults';
import './App.css';

function App() {
  const [currentPage, setCurrentPage] = useState('dashboard');
  const [selectedJobId, setSelectedJobId] = useState(null);
  const [refreshTrigger, setRefreshTrigger] = useState(0);

  const handleJobCreated = (jobId) => {
    setSelectedJobId(jobId);
    setCurrentPage('results');
    // Trigger refresh when returning to dashboard
    setRefreshTrigger(prev => prev + 1);
  };

  const handleJobSelected = (jobId) => {
    setSelectedJobId(jobId);
    setCurrentPage('results');
  };

  const handleBackToDashboard = () => {
    setCurrentPage('dashboard');
    setSelectedJobId(null);
    // Trigger refresh when explicitly going back to dashboard
    setRefreshTrigger(prev => prev + 1);
  };

  return (
    <div className="app">
      <header className="header">
        <h1>C Code Analyzer</h1>
        {currentPage !== 'dashboard' && (
          <button onClick={handleBackToDashboard} style={{ marginTop: '10px' }}>
            ← Back to Dashboard
          </button>
        )}
      </header>

      {currentPage === 'create' && (
        <JobCreation onJobCreated={handleJobCreated} />
      )}

      {currentPage === 'dashboard' && (
        <JobDashboard
          onJobSelected={handleJobSelected}
          onCreateJob={() => setCurrentPage('create')}
          refreshTrigger={refreshTrigger}
        />
      )}

      {currentPage === 'results' && selectedJobId && (
        <JobResults jobId={selectedJobId} />
      )}
    </div>
  );
}

export default App;
