# Reproducible environment for every experiment (CPU).
#   docker build -t swarm .
#   docker run --rm -v "$PWD/runs:/app/runs" swarm swarm train --config configs/energy.yaml
FROM python:3.11-slim

WORKDIR /app
RUN pip install --no-cache-dir torch==2.5.1 --index-url https://download.pytorch.org/whl/cpu
COPY pyproject.toml README.md ./
COPY core core
COPY apps apps
RUN pip install --no-cache-dir -e ".[hotel,research]"
COPY configs configs
COPY experiments experiments
COPY tests tests
CMD ["pytest", "-q", "tests"]
