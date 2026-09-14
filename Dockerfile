FROM python:3.12-slim@sha256:78387bc3881b8273120a12ebe6c1ab22b018ccc2c9adf565ae1ac9b536e184ea

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY pyproject.toml README.md ./
COPY src ./src
COPY tests ./tests
COPY features ./features
COPY terraform ./terraform
COPY examples ./examples
RUN pip install --upgrade pip && pip install ".[dev]"

EXPOSE 8000
CMD ["uvicorn", "dataset_quality.app:app", "--host", "0.0.0.0", "--port", "8000"]
