FROM python:3.12-slim
WORKDIR /app
COPY clearance/ clearance/
COPY agent_science.py .
COPY cloud/ cloud/
ENV PORT=8080 \
    PYTHONUNBUFFERED=1 \
    CORPUS_DB=/tmp/corpus.db
EXPOSE 8080
CMD ["python3", "cloud/service.py"]
