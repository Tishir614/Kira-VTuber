FROM python:3.13-slim
WORKDIR /agent
COPY cloud/agent/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && playwright install --with-deps chromium
COPY cloud/agent/main.py .
EXPOSE 8766
CMD ["uvicorn","main:app","--host","0.0.0.0","--port","8766"]
