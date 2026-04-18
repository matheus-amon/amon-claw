# Especificação Técnica de Infraestrutura (Cloud Native)

## 1. Arquitetura Geral
Baseada em serviços Serverless da AWS para custo zero inicial.

### Fluxo de Requisição
1. **WhatsApp** -> **Evolution API** (via VPS ou Twilio)
2. **Evolution API** -> **API Gateway** (AWS)
3. **API Gateway** -> **AWS Lambda** (FastAPI)
4. **Lambda** -> **MongoDB Atlas** / **Google Calendar** / **OpenRouter**

## 2. Componentes AWS
- **AWS Lambda:** Execução Docker com `aws-lambda-web-adapter`.
- **API Gateway:** HTTP API.
- **Amazon ECR:** Repositório de imagens Docker.
- **IAM:** Roles com permissões mínimas.
- **SSM Parameter Store:** Gestão de chaves de API.

## 3. Estratégia de Deploy
- **Docker:** Imagem otimizada para Lambda.
- **CI/CD:** GitHub Actions orquestrando o build e o terraform apply.
