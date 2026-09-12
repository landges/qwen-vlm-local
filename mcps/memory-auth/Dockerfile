FROM python:3.12-slim-bookworm

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1

COPY requirements.txt ./
RUN pip install --requirement requirements.txt

COPY . .
RUN chmod +x /app/entrypoint.sh \
    && chown -R nobody:nogroup /app

USER nobody:nogroup
EXPOSE 8080

ENTRYPOINT ["/app/entrypoint.sh"]

