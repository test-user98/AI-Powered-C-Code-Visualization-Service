const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8080';

export const api = {
  // Create a new job
  createJob: async (code) => {
    const response = await fetch(`${API_BASE_URL}/api/jobs`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ code }),
    });

    if (!response.ok) {
      throw new Error(`Failed to create job: ${response.status}`);
    }

    return response.json();
  },

  // Get all jobs
  getJobs: async () => {
    const response = await fetch(`${API_BASE_URL}/api/jobs`);

    if (!response.ok) {
      throw new Error(`Failed to fetch jobs: ${response.status}`);
    }

    return response.json();
  },

  // Get specific job details
  getJob: async (jobId) => {
    const response = await fetch(`${API_BASE_URL}/api/jobs/${jobId}`);

    if (!response.ok) {
      throw new Error(`Failed to fetch job: ${response.status}`);
    }

    return response.json();
  },

  // Health check
  healthCheck: async () => {
    const response = await fetch(`${API_BASE_URL}/`);
    return response.json();
  }
};
