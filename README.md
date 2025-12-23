# C Code Analyzer Backend

A FastAPI backend service for analyzing C code and generating Mermaid flowcharts for functions.

## Features

- Asynchronous job processing for C code analysis
- Function detection using ast-grep
- Mermaid diagram generation using OpenAI GPT
- Diagram validation with mermaid-cli
- RESTful API with progress tracking

## Setup

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

The frontend will be available at `http://localhost:3000` and connects to the backend at `http://localhost:8081`.

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
