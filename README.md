# Event Finder API

A FastAPI-based intelligent event discovery and analysis platform that helps users find relevant events based on their preferences and profile.

## Tech Stack

- **Framework**: FastAPI
- **Language**: Python 3.11+
- **AI/LLM**: Google Gemma 3 27B, Ollama
- **Web Scraping**: Playwright
- **Caching**: Upstash Redis
- **Background Jobs**: Google Cloud Run Jobs
- **HTTP Client**: Requests

## Installation

### Prerequisites

- Python 3.11 or higher
- pip or another Python package manager
- Docker (for Cloud Run Jobs)
- Google Cloud CLI (for deployment)

### Setup

1. Clone the repository:

```bash
git clone <repository-url>
cd event-finder-api
```

2. Install dependencies:

```bash
pip install -e .
```

3. Install development dependencies (optional):

```bash
pip install -e ".[dev]"
```

4. Install Playwright:

```bash
playwright install chromium
```

## Usage

### Running the API

Start the development server:

```bash
uvicorn api.main:app --reload
```

Or use the provided startup script:

```bash
./local-startup.sh
```

The API will be available at `http://localhost:8000`

### API Documentation

Once running, you can access:

- **Interactive API docs**: http://localhost:8000/docs
- **ReDoc documentation**: http://localhost:8000/redoc
- **Health check**: http://localhost:8000/health

## Cloud Run Jobs

The application uses Google Cloud Run Jobs for background task processing instead of Celery.

### Testing Jobs Locally

```bash
./test-job-local.sh
```

### Deploying Jobs

1. Set your Google Cloud project ID:

```bash
export PROJECT_ID="your-project-id"
```

2. Deploy the job:

```bash
./deploy-job.sh
```

3. Execute the job:

```bash
gcloud run jobs execute event-finder-agent-job --region us-central1
```

## Development

### Code Quality

The project uses several tools for code quality:

- **Type Checking**: mypy
- **Testing**: pytest
- **Code Formatting**: black
- **Import Sorting**: isort
- **Linting**: flake8

### Running Tests

```bash
pytest
```

### Code Formatting

```bash
# Format code
black .

# Sort imports
isort .

# Type checking
mypy .
```

### Project Structure

```
event-finder-api/
├── api/                    # FastAPI application
│   ├── main.py            # Application entry point
│   └── routers/           # API route definitions
├── cloud_run_job.py       # Cloud Run Job script
├── Dockerfile.job         # Dockerfile for Cloud Run Jobs
├── deploy-job.sh          # Job deployment script
├── test-job-local.sh      # Local job testing script
├── core/                  # Core configuration and utilities
├── models/                # Data models
├── services/              # Business logic services
│   ├── event_processing/  # Event analysis services
│   ├── scrapping/         # Web scraping services
│   └── search_words/      # Search keyword generation
├── utils/                 # Utility functions
└── pyproject.toml         # Project configuration
```

## Configuration

The application uses environment variables for configuration. Key settings include:

- LLM API keys and endpoints
- Redis connection details
- Browser pool settings
- Logging configuration

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and code quality checks
5. Submit a pull request
