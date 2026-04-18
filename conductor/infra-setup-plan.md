# Plano de Implementação: Infraestrutura Cloud Native (AWS Lambda + Terraform)

Este plano descreve a criação da infraestrutura de produção para o Amon Claw, seguindo os princípios de "Production-First" e "Cloud Native".

## Objetivos
1. Documentar as decisões de infraestrutura.
2. Criar a estrutura de diretórios para o Terraform.
3. Configurar o pipeline de CI/CD via GitHub Actions.
4. Implementar o suporte a Docker e AWS Lambda Web Adapter no FastAPI.

## Fase 1: Documentação e ADRs
- Criar `docs/adr/003-infrastructure-as-code-terraform.md`.
- Criar `docs/infra/001-cloud-native-setup.md`.
- Criar `docs/infra/002-requirements-and-secrets.md`.

## Fase 2: Dockerização e Adaptadores
- Criar `Dockerfile` otimizado para AWS Lambda usando o `aws-lambda-web-adapter`.
- Ajustar `src/main.py` para garantir compatibilidade com o runtime da Lambda (porta 8080 padrão do adaptador).

## Fase 3: Terraform (IaC)
- Criar pasta `/infra`.
- Configurar o Backend Remoto (S3 + DynamoDB) para o Terraform State.
- Implementar módulos:
    - `ecr`: Para armazenar a imagem Docker.
    - `iam`: Roles e Policies para a Lambda.
    - `lambda`: Função Lambda configurada para usar a imagem do ECR.
    - `api_gateway`: Exposição da Lambda via HTTP API.
    - `ssm`: Armazenamento de configurações não sensíveis.

## Fase 4: CI/CD (GitHub Actions)
- Criar `.github/workflows/deploy.yml`.
- Passos do pipeline:
    1. Checkout do código.
    2. Configurar credenciais AWS.
    3. Login no Amazon ECR.
    4. Build, Tag e Push da imagem Docker.
    5. Terraform Init/Plan/Apply.
    6. Update da função Lambda para usar a nova tag da imagem.

## Verificação
1. Execução de `terraform plan` local para validar sintaxe.
2. Deploy em ambiente de `dev` na AWS.
3. Teste do endpoint `/health` via URL do API Gateway.
4. Verificação de logs no CloudWatch.

## Riscos e Mitigações
- **Cold Starts:** Mitigado pelo uso do `aws-lambda-web-adapter` e mantendo a imagem Docker leve.
- **Custos:** Monitoramento via AWS Budgets (esperado R$ 0,00 no Free Tier).
- **Segurança:** Uso de IAM Roles com permissão mínima e segredos via SSM/Secrets Manager.
