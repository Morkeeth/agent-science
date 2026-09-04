FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY clearance/ clearance/
COPY truth-dictionary/ truth-dictionary/
COPY agent_science.py ask_registry.py clear_corpus.py ./
COPY docs/inspiration/PRACTICES-CORPUS.md docs/inspiration/PRACTICES-CORPUS.md
COPY cloud/ cloud/
ENV PORT=8080 \
    PYTHONUNBUFFERED=1 \
    CORPUS_DB=/tmp/corpus.db \
    REFUSAL_LOG_DB=/tmp/refusal_log.db \
    AGENT_BUILDER=1 \
    GOOGLE_GENAI_USE_VERTEXAI=true \
    GOOGLE_CLOUD_LOCATION=global
EXPOSE 8080
CMD ["python3", "cloud/service.py"]
