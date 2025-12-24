# C Code Analyzer

A full-stack web application for analyzing C code and generating interactive Mermaid flowcharts for functions.

## 🚀 Quick Start (Docker - Recommended for External Users)

The easiest way to run the complete application is using Docker:

```bash
# Clone the repository
git clone https://github.com/test-user98/AI-Powered-C-Code-Visualization-Service.git
cd c-code-analyzer-backend

# Run the automated setup script
./setup.sh

# Or manually:
# docker-compose build
# docker-compose up -d

# Access the application:
# Frontend: http://localhost:3000
# Backend API: http://localhost:8080
```

That's it! The application will be running with:
- ✅ Backend API (FastAPI)
- ✅ Frontend UI (React)
- ✅ Real-time WebSocket updates
- ✅ All dependencies pre-installed

## Features

- 🔄 **Asynchronous job processing** for C code analysis
- 🎯 **Smart function detection** using ast-grep (with regex fallback)
- 📊 **Mermaid diagram generation** using AST traversal
- ⚡ **Real-time updates** via WebSockets (no polling)
- 🌐 **RESTful API** with progress tracking
- 🐳 **Docker containerization** for easy deployment
- 🎨 **Interactive frontend** with live progress updates

## 🐳 Docker Setup (Detailed)

### Prerequisites
- Docker Engine 20.10+
- Docker Compose 2.0+

### Quick Docker Commands

```bash
# Build and start all services
docker-compose up --build

# Run in background
docker-compose up -d --build

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Rebuild after code changes
docker-compose up --build --force-recreate
```

### Service Architecture

The application consists of two services:

1. **Backend** (FastAPI)
   - Port: 8080
   - Handles C code analysis and Mermaid generation
   - Uses WebSocket for real-time updates
   - Health check endpoint: `GET /`

2. **Frontend** (React)
   - Port: 3000
   - Modern React UI with live progress updates
   - Communicates with backend via REST API and WebSockets

### Container Features

- **Health Checks**: Automatic service health monitoring
- **Volume Mounting**: Development-friendly code mounting
- **Network Isolation**: Secure inter-service communication
- **Automatic Restarts**: Fault-tolerant deployment
- **ast-grep Integration**: Advanced C code analysis included

### Production Deployment

For production, use the optimized build:

```bash
# Build for production
docker-compose -f docker-compose.yml up --build -d

# The frontend container serves optimized static files
# Backend runs with production settings
```

## 💻 Local Development Setup

### Prerequisites

- Python 3.11+
- Node.js (for mermaid-cli)
- OpenAI API key

### Installation

1. Clone the repository and navigate to the backend directory:
```bash
cd c_code_analyzer_backend
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. Install ast-grep (recommended for better C function detection):
```bash
# On macOS
brew install ast-grep

# On Linux
curl -L https://github.com/ast-grep/ast-grep/releases/latest/download/ast-grep-linux-x86_64.tar.gz | tar xz
sudo mv ast-grep /usr/local/bin/

# Manual installation (if above methods fail)
mkdir -p ~/bin
curl -L https://github.com/ast-grep/ast-grep/releases/latest/download/ast-grep-$(uname -s | tr '[:upper:]' '[:lower:]')-$(uname -m | sed 's/x86_64/x86_64/' | sed 's/aarch64/arm64/').tar.gz | tar xz
mv ast-grep ~/bin/
export PATH="$HOME/bin:$PATH"
```

**Note:** ast-grep is optional. If not installed, the system will automatically fall back to regex-based function detection, which works reliably for most C code.

**Useful links:**
- **Mermaid**: [mermaid.live](https://mermaid.live)
- **Mermaid flowchart documentation**: [Mermaid Docs](https://mermaid.js.org/)
- **Ast-grep**: [ast-grep.github.io](https://ast-grep.github.io/)
- **Ast-grep Python API**: [PyPI](https://pypi.org/project/ast-grep/)

4. Install mermaid-cli:
```bash
npm install -g @mermaid-js/mermaid-cli
```

5. Set up environment variables:
```bash
cp .env.example .env
# Edit .env and add your OpenAI API key
```

### Docker Setup

Use Docker Compose to run both frontend and backend:

```bash
docker-compose up --build
```

This will start:
- **Backend API**: http://localhost:8000
- **Frontend UI**: http://localhost:3000

For backend-only Docker setup:

```bash
docker build -t c-analyzer-backend .
docker run -p 8000:8000 -e OPENAI_API_KEY=your_key c-analyzer-backend
```

## API Endpoints

### POST /api/jobs
Create a new analysis job.

**Request Body:**
```json
{
  "code": "#include <stdio.h>\n\nint main(void) {\n    printf(\"Hello World\\n\");\n    return 0;\n}"
}
```

**Response:**
```json
{
  "job_id": "uuid-here",
  "status": "queued"
}
```

### GET /api/jobs
Get all jobs with their status.

**Response:**
```json
[
  {
    "id": "uuid-here",
    "status": "in_progress",
    "created_at": "2023-12-01T10:00:00Z",
    "total_functions": 2,
    "processed_functions": 1
  }
]
```

### GET /api/jobs/{job_id}
Get detailed information about a specific job.

**Response:**
```json
{
  "id": "uuid-here",
  "code": "...",
  "status": "success",
  "created_at": "2023-12-01T10:00:00Z",
  "updated_at": "2023-12-01T10:01:00Z",
  "total_functions": 2,
  "processed_functions": 2,
  "functions": [
    {
      "name": "main",
      "mermaid_diagram": "flowchart TD\n    A[main] --> B[printf]\n    B --> C[return]"
    }
  ],
  "error_message": null

}
```

## Real-time Updates

The API provides real-time job status updates via WebSockets:

### WebSocket Endpoint
- `WS /ws/jobs` - Real-time job status updates

### WebSocket Message Format
```json
{
  "type": "job_update",
  "job_id": "uuid",
  "status": "in_progress|success|failed",
  "total_functions": 3,
  "processed_functions": 2,
  "updated_at": "2025-12-23T09:18:45.123456"
}
```

**Benefits:**
- No polling required
- Instant status updates
- Reduced server load
- Better user experience

## Development

Run the development server:
```bash
python app/main.py
```

The API will be available at http://localhost:8000

## Frontend Setup

A React frontend is available for an interactive user experience:

```bash
cd frontend
npm install
npm start
```

The frontend will be available at `http://localhost:3000` and connects to the backend at `http://localhost:8080`.

## Architecture

- **FastAPI**: Web framework for the REST API
- **Job Service**: Manages job lifecycle and background processing
- **Code Analyzer**: Handles C code analysis with AST traversal and Mermaid generation
- **React Frontend**: Interactive UI for job submission and results visualization
- **Background Processing**: Uses threading for asynchronous job processing

## Job Processing Flow

1. **Job Creation**: User submits C code, job is queued
2. **Function Detection**: ast-grep analyzes code to find function definitions
3. **Diagram Generation**: For each function, LLM generates Mermaid flowchart
4. **Validation**: mermaid-cli validates diagram syntax
5. **Completion**: Job marked as success with results or failed with error
