FROM python:3.9-slim

WORKDIR /app

# Install system dependencies (build tools for pandas/numpy if needed)
RUN apt-get update && apt-get install -y gcc

COPY pyproject.toml .
# Install dependencies
RUN pip install --no-cache-dir fastapi uvicorn sqlalchemy alembic pydantic pydantic-settings httpx python-multipart aiosqlite pandas scikit-learn numpy xgboost riotskillissue

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
