FROM python:3.11-slim

RUN pip install uv

WORKDIR /app

COPY . /app

CMD ["uv", "run", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
