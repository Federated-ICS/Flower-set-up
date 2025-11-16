FROM python:3.10-slim

WORKDIR /app
COPY services/fastapi_backend/requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
ENV PYTHONPATH=/app/src
CMD ["uvicorn", "services.fastapi_backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
