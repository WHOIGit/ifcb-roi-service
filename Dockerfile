FROM astral/uv:python3.12-bookworm-slim

WORKDIR /app

RUN apt-get update && apt-get install -y git && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

ENV PATH="/root/.local/bin:$PATH"

# No log buffering
ENV PYTHONUNBUFFERED=1

COPY . ./service

WORKDIR /app/service

RUN uv pip install --system .

EXPOSE 8001

CMD ["uvicorn", "service.main:app", "--host", "0.0.0.0", "--port", "8001"]
