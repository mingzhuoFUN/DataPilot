FROM python:3.12-alpine
ENV PYTHONUNBUFFERED=1 PYTHONUTF8=1
WORKDIR /app
COPY start_mock_vllmserver.py ./server.py
EXPOSE 8000
CMD ["python", "server.py"]
