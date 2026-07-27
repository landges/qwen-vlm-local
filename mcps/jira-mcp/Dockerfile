FROM python:3.12-slim-bookworm

ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1

RUN pip install "mcp-atlassian==0.23.0"

USER nobody:nogroup

EXPOSE 9000

ENTRYPOINT ["mcp-atlassian"]
CMD ["--transport", "streamable-http", "--host", "0.0.0.0", "--port", "9000"]
