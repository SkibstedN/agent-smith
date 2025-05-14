# agent.Dockerfile  
FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
        nmap curl iputils-ping \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . /app
RUN pip install --no-cache-dir -r requirements.txt

ENV AGENT_LOG=/logs/agent-smith.log
CMD ["python", "app/main.py"]