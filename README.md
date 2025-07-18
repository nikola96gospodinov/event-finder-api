# Event Finder API

A FastAPI-based intelligent event discovery and analysis platform that helps users find relevant events based on their preferences and profile.

## Tech Stack

- **Framework**: FastAPI
- **Language**: Python 3.11+
- **AI/LLM**: Google Gemma 3 27B, Ollama
- **Web Scraping**: Playwright
- **Caching**: Upstash Redis
- **HTTP Client**: Requests

## Installation

### Prerequisites

- Python 3.11 or higher
- pip or another Python package manager

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

The API will be available at `http://localhost:8000`

### API Documentation

Once running, you can access:

- **Interactive API docs**: http://localhost:8000/docs
- **ReDoc documentation**: http://localhost:8000/redoc

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
