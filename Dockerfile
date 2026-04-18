# Dockerfile otimizado para AWS Lambda com Web Adapter
FROM public.ecr.aws/docker/library/python:3.12-slim

# Instalar o AWS Lambda Web Adapter
COPY --from=public.ecr.aws/awsguru/aws-lambda-adapter:0.8.4 /lambda-adapter /opt/extensions/lambda-adapter

WORKDIR /app

# Instalar UV
RUN pip install --no-cache-dir uv

# Copiar apenas os arquivos de dependências primeiro (cache layer)
COPY pyproject.toml uv.lock ./
RUN uv pip install --system --no-cache-dir -r pyproject.toml

# Copiar o código do projeto
COPY . .

# Instalar o próprio projeto em modo editável ou normal para o PYTHONPATH ser resolvido
RUN uv pip install --system --no-cache-dir -e .

# Variáveis de ambiente padrão
ENV PORT=8080
ENV PYTHONPATH=/app/src

# O adaptador escuta na 8080 por padrão e repassa pro app
EXPOSE 8080

# Comando para rodar o app via Uvicorn
CMD ["python", "-m", "uvicorn", "amon_claw.presentation.api.app:app", "--host", "0.0.0.0", "--port", "8080"]
