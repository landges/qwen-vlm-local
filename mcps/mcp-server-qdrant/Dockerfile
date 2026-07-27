FROM python:3.11-slim

WORKDIR /app

ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    FASTEMBED_CACHE_PATH=/opt/fastembed-cache \
    HF_HUB_OFFLINE=1 \
    TRANSFORMERS_OFFLINE=1

COPY pyproject.toml README.md LICENSE ./

RUN pip install \
    "fastembed>=0.6.0" \
    "qdrant-client>=1.12.0" \
    "pydantic>=2.10.6,<2.12.0" \
    "fastmcp==2.7.0"

# Download and initialize the embedding model while network access is available
# during the image build. Runtime starts with offline flags enabled.
RUN HF_HUB_OFFLINE=0 TRANSFORMERS_OFFLINE=0 python -c \
    "from fastembed import TextEmbedding; model = TextEmbedding('sentence-transformers/all-MiniLM-L6-v2', cache_dir='/opt/fastembed-cache'); list(model.embed(['build-time cache warmup']))"

COPY src ./src

RUN pip install --no-deps .

RUN chown -R nobody:nogroup /opt/fastembed-cache

USER nobody:nogroup

EXPOSE 8000

ENTRYPOINT ["mcp-server-qdrant"]
CMD ["--transport", "streamable-http"]
