# Infra & Developer Experience Design (Cloud Native + Local Dev)

## 1. Overview
Este documento define a arquitetura e as decisões técnicas de infraestrutura para o projeto Amon Claw, englobando a otimização do build Docker com `uv` para AWS Lambda e a organização da infraestrutura como código (IaC) com Terraform, além de garantir uma Developer Experience (DX) foda rodando localmente via Docker Compose.

## 2. Docker e Build Otimizado (`uv` + AWS Lambda Web Adapter)
Baseado nas melhores práticas de 2024/2025 para ambientes Serverless Python:

### 2.1. Multi-stage Build
- **Stage 1 (Builder):** Usa a imagem oficial do `uv` (`ghcr.io/astral-sh/uv:python3.12-bookworm-slim`) para gerenciar as dependências e usar o cache do Docker (via `--mount=type=cache`). Compila os bytecodes (`UV_COMPILE_BYTECODE=1`) e instala as dependências num `.venv`.
- **Stage 2 (Runtime):** Usa uma imagem base hiper leve da AWS ou Debian `slim`. Copia apenas o `.venv`, o código da aplicação e o binário do **AWS Lambda Web Adapter**.
- **Benefícios:** A imagem final fica muito menor (sem o binário Rust do `uv` e sem cache de pacotes inúteis), reduzindo drasticamente o *cold start* da Lambda.

### 2.2. Arquitetura Alvo
- A imagem Docker será configurada preferencialmente para `linux/arm64` (AWS Graviton), que oferece até 20% mais performance e menor custo na AWS.

## 3. Terraform (IaC) Moderno
A infraestrutura será modular e focada em Serverless:

### 3.1. Módulos Core
- **ECR:** Repositório privado com lifecycle policy para reter apenas as X últimas imagens (evita custo de storage desnecessário).
- **IAM:** Políticas granulares baseadas em "Least Privilege". Apenas permissões pro CloudWatch Logs e SSM Parameter Store (para ler segredos).
- **Lambda:** 
  - `package_type = "Image"` (apontando pro ECR).
  - Arquitetura `arm64`.
  - Configuração de tracing com AWS X-Ray (`Active`) para debug de latência LLM.
- **API Gateway (HTTP API v2):** Usado em vez do REST API v1 por ser ~70% mais barato e ter menor latência, perfeito para o Web Adapter com FastAPI.

### 3.2. Gerenciamento de Estado
- Backend remoto configurado em um bucket S3 com state locking via DynamoDB.

## 4. Developer Experience (DX)
Para garantir agilidade no dia a dia e testabilidade "real":

### 4.1. Workflow Local (Dev)
- **`compose.yml`**: Roda apenas as dependências de infra (MongoDB, Mongo Express, Redis, Redis Insight).
- **Rodar a API**: O desenvolvedor roda o FastAPI localmente usando `uv run uvicorn ... --reload`. Isso permite hot-reload nativo ultrarrápido, sem precisar rebuildar containers a cada virgula alterada.

### 4.2. Workflow "Test Drive" (Produção Local / PoC)
- Vamos criar um **`compose.prod.yml`** (ou um profile no compose). Ele buildará a imagem otimizada da "Lambda" e rodará o FastAPI dentro do container, simulando exatamente o ambiente empacotado que irá para a AWS. Ideal para apresentar o sistema em clientes ou validar a imagem final antes do deploy.

## 5. Próximos Passos (Plano de Ação)
1. Reescrever o `Dockerfile` com a estratégia Multi-stage + `uv`.
2. Criar/Atualizar o `compose.yml` para rodar apenas os serviços de banco/cache.
3. Criar o `compose.prod.yml` (opcional) para testes de "blackbox".
4. Estruturar o esqueleto base da pasta `infra/` com Terraform (módulos IAM, ECR, Lambda, API Gateway).