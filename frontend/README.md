# C Code Analyzer Frontend

A React frontend for the C Code Analyzer API that provides an interactive interface for analyzing C code and viewing generated flowcharts.

## Features

- **Job Creation**: Submit C code for analysis via textarea or file upload
- **Job Dashboard**: View all submitted jobs with real-time progress updates
- **Results Viewer**: Display function analysis results with Mermaid diagrams
- **Live Progress**: Automatic polling for job progress updates

## Setup

1. **Install dependencies:**
   ```bash
   cd frontend
   npm install
   ```

2. **Start the development server:**
   ```bash
   npm start
   ```
   The frontend will be available at `http://localhost:3000`

3. **Ensure the backend is running:**
   Make sure the backend server is running on `http://localhost:8080`

## API Configuration

The frontend is configured to connect to the backend at `http://localhost:8080`. To change this:

1. Create a `.env` file in the frontend directory:
   ```
   REACT_APP_API_URL=http://your-backend-url:port
   ```

2. Or modify `src/api.js` directly:
   ```javascript
   const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://your-backend-url:port';
   ```

## Components

### JobCreation
- Textarea for C code input
- File upload for .c files
- Form validation and error handling

### JobDashboard
- List of all jobs with status indicators
- Real-time progress updates for running jobs
- Click to view completed job results

### JobResults
- Detailed view of job analysis
- Side-by-side display of Mermaid syntax and rendered diagrams
- Function-by-function breakdown

### MermaidDiagram
- React wrapper for mermaid.js library
- Renders flowchart diagrams from Mermaid syntax
- Error handling for invalid syntax

## Development

- Built with React 18
- Uses Create React App for development tooling
- Mermaid.js for diagram rendering
- Responsive design with minimal CSS

## Production Build

```bash
npm run build
```

This creates a production build in the `build` folder that can be served by any static web server.
