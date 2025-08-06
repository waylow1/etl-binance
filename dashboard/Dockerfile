FROM python:3.11-slim

WORKDIR /app

RUN pip install uv
COPY . .

EXPOSE 8050

CMD ["uv", "pip", "run", "python", "src/app.py"]
