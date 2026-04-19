# Implementation Plan: Infra & DX Otimizada

## Objective
Implementar as melhorias de infraestrutura definidas no spec `2026-04-19-infra-docker-terraform-design.md`, otimizando a imagem Docker para AWS Lambda com `uv`, estruturando os módulos do Terraform e ajustando o ambiente de desenvolvimento local (Docker Compose).

## Step 1: Otimização do Dockerfile (AWS Lambda + `uv`)
- [ ] Refatorar o arquivo `Dockerfile` na raiz do projeto.
- [ ] Implementar a abordagem **Multi-stage Build**.
- [ ] Stage 1 (Builder): 
  - Base `ghcr.io/astral-sh/uv:python3.12-bookworm-slim`.
  - Setar variáveis de otimização (`UV_COMPILE_BYTECODE=1`, `UV_LINK_MODE=copy`).
  - Fazer o `uv sync` das dependências com cache mount e exportar para `.venv`.
- [ ] Stage 2 (Runtime):
  - Base `python:3.12-slim-bookworm`.
  - Copiar o AWS Lambda Web Adapter (`public.ecr.aws/awsguru/aws-lambda-adapter:0.8.4`).
  - Copiar o diretório `.venv` e os fontes da aplicação.
  - Setar o `CMD` para rodar o Uvicorn apontando pro app correto (`amon_claw.main:app` ou `amon_claw.presentation.api.main:app`).

## Step 2: Ajuste da Developer Experience (Docker Compose)
- [ ] Modificar o `compose.yml` principal para ser focado apenas em dependências (MongoDB, Mongo Express, Redis, RedisInsight), removendo o serviço da aplicação (`app`).
- [ ] Criar um arquivo secundário `compose.full.yml` (ou similar) que inclua o serviço `app` buildando do novo `Dockerfile` otimizado, para servir de ambiente de demonstração/PoC.
- [ ] Atualizar documentação do README.md (ou adicionar um quickstart) explicando os dois fluxos de execução:
  - Workflow Dev (Bancos via Docker + API via `uv run local`).
  - Workflow PoC (Tudo via Docker Compose).

## Step 3: Estruturação Base do Terraform
- [ ] Criar diretório `infra/` na raiz do repositório.
- [ ] Criar arquivos base: `infra/main.tf`, `infra/providers.tf`, `infra/variables.tf`, `infra/outputs.tf`.
- [ ] Configurar backend S3/DynamoDB provisório ou comentado no `providers.tf`.
- [ ] Criar estrutura de módulos em `infra/modules/`:
  - [ ] `ecr/`: Configuração de Lifecycle policies.
  - [ ] `iam/`: Configuração de roles e policies (Least Privilege).
  - [ ] `lambda/`: Configuração de Image-based Lambda com arquitetura `arm64`.
  - [ ] `api_gateway/`: Configuração de HTTP API v2 com rota `$default`.
