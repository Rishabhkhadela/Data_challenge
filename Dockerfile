FROM python:3.11-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN addgroup --system app && adduser --system --ingroup app app

COPY requirements.txt pyproject.toml README.md ./
COPY src ./src
COPY configs ./configs

RUN pip install --upgrade pip \
    && pip install -r requirements.txt \
    && pip install .

USER app

EXPOSE 8000

CMD ["uvicorn", "ai_hiring_intelligence.api.main:app", "--host", "0.0.0.0", "--port", "8000"]

