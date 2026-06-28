# AI Hiring Intelligence

Production-grade boilerplate for an AI Hiring Intelligence platform.

This repository currently contains project structure, configuration, and service shells only. Business logic is intentionally not implemented yet.

## Stack

- Python 3.11
- FastAPI API service
- Streamlit UI service
- `src` package layout
- Pydantic settings
- Structured logging
- Pytest
- Docker

## Local Development

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
pip install -e ".[dev]"
```

Run the API:

```bash
uvicorn ai_hiring_intelligence.api.main:app --reload
```

Run the Streamlit app:

```bash
streamlit run src/ai_hiring_intelligence/ui/app.py
```

Run tests:

```bash
pytest
```

## Docker

Build and run the API image:

```bash
docker build -t ai-hiring-intelligence .
docker run --rm -p 8000:8000 ai-hiring-intelligence
```

Or run API and UI together:

```bash
docker compose up --build
```

