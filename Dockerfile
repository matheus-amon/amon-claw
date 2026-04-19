# --- Stage 1: Builder ---
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS builder

# Otimizações do uv para Docker e Lambda
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Instala dependências primeiro para aproveitar o cache do Docker
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project --no-dev

# Adiciona o código da aplicação e instala o projeto
COPY . /app
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

# --- Stage 2: Runtime ---
FROM python:3.12-slim-bookworm

# Instalar o AWS Lambda Web Adapter
COPY --from=public.ecr.aws/awsguru/aws-lambda-adapter:0.8.4 /lambda-adapter /opt/extensions/lambda-adapter

ENV PORT=8080
ENV PYTHONPATH=/var/task/src
WORKDIR /var/task

# Copia o ambiente virtual e o código do builder
COPY --from=builder /app /var/task

# Garante que o Python use as dependências do venv
ENV PATH="/var/task/.venv/bin:$PATH"

# O adaptador escuta na 8080 por padrão e repassa pro app
EXPOSE 8080

# Comando para rodar o app via Uvicorn de dentro do venv
CMD ["uvicorn", "amon_claw.presentation.api.app:app", "--host", "0.0.0.0", "--port", "8080"]
