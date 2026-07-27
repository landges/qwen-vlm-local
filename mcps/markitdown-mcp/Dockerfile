FROM python:3.13-slim-bookworm

ENV DEBIAN_FRONTEND=noninteractive \
    EXIFTOOL_PATH=/usr/bin/exiftool \
    FFMPEG_PATH=/usr/bin/ffmpeg \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        ffmpeg \
        libimage-exiftool-perl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install "markitdown-mcp==0.0.1a4"

WORKDIR /workdir

USER nobody:nogroup

ENTRYPOINT ["markitdown-mcp"]
