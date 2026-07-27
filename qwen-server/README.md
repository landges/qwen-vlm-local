# Qwen Server

Локальный сервер для работы с моделями Qwen: генерация текста и модуль предсказания проектов (mmproj).

## Технологии

- Python (FastAPI)
- GGUF формат моделей (llama.cpp backend)
- Docker для контейнеризации

## Требования

- Python 3.9+
- llama-cpp-python
- минимум 8GB RAM
- минимум 16 ядер CPU

## Конфигурация

См. файл `.env`:

```bash
MODEL_PATH=/models/Qwen3.5-4B-Q4_K_M.gguf      # Путь к модели Qwen
MMPROJ_PATH=/models/mmproj-F16.gguf            # Путь к модулю mmproj
PORT=8000                                       # Порт сервера
CTX_SIZE=20096                                  # Размер контекста
N_GPU_LAYERS=999                                # GPU слои (max для GPU)
THREADS=16                                      # Количество ядер
BATCH_SIZE=1024                                 # Размер батча
ENABLE_THINKING=false                           # Включить chain-of-thought
```

## Запуск

### Вариант 1: Docker

```bash
docker-compose up -d
```

### Вариант 2: Локально (Python)

```bash
# Установка зависимостей
pip install -r requirements.txt

# Запуск сервера
uvicorn app:app --host 0.0.0.0 --port 8000
```

## API

### Генерация текста

```bash
curl -X POST "http://localhost:8000/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Привет",
    "model": "Qwen3.5-4B-Q4_K_M.gguf",
    "max_tokens": 256
  }'
```

### Предсказание проекта (mmproj)

```bash
curl -X POST "http://localhost:8000/mmproj" \
  -H "Content-Type: application/json" \
  -d '{
    "project_path": "/path/to/project"
  }'
```

## Модели

Доступные модели в папке `models/`:

- `Qwen3.5-4B-Q4_K_M.gguf` — 4B параметров, 4-bit квантование (Qwen3.5)
- `mmproj-F16.gguf` — модуль предсказания проектов (FP16)

## Остановка

```bash
# Docker
docker-compose down

# Python
# Ctrl+C
```

## Лицензия

MIT
