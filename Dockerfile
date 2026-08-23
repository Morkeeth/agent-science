FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY clearance/ clearance/
COPY agent_science.py .
COPY cloud/ cloud/
ENV PORT=8080 \
    PYTHONUNBUFFERED=1 \
    CORPUS_DB=/tmp/corpus.db \
    AGENT_BUILDER=1 \
    GOOGLE_GENAI_USE_VERTEXAI=true \
    GOOGLE_CLOUD_LOCATION=global
EXPOSE 8080
CMD ["python3", "cloud/service.py"]
