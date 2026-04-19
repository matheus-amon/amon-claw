# Estrutura do Terraform (IaC)

Este documento detalha como a infraestrutura do Amon Claw será organizada via Terraform. A ideia é ser modular e fácil de manter.

## 1. Organização de Arquivos
A pasta `/infra` será organizada da seguinte forma:

```text
infra/
├── main.tf            # Ponto de entrada, chama os módulos
├── providers.tf       # Configuração da AWS e Versão do Terraform
├── variables.tf       # Variáveis globais (região, nome do projeto)
├── outputs.tf         # URLs e IDs importantes (ex: URL da API)
├── terraform.tfvars   # Valores das variáveis (NÃO comitar se tiver segredo)
└── modules/           # Módulos reutilizáveis
    ├── ecr/           # Repositório de imagens Docker
    ├── iam/           # Roles e permissões da Lambda
    ├── lambda/        # A função Lambda propriamente dita
    └── api_gateway/   # Configuração do endpoint HTTP
```

## 2. Detalhes dos Módulos

### Módulo: ECR
- Responsável por criar o repositório privado na AWS.
- Configura política de limpeza (ex: manter apenas as últimas 5 imagens para economizar espaço).

### Módulo: IAM
- Cria a role de execução da Lambda.
- Adiciona permissões básicas de logs (CloudWatch) e acesso à rede (se necessário).
- **Security First:** Apenas permissões estritamente necessárias.

### Módulo: Lambda
- Configura a função para usar imagens do ECR.
- Define memória (inicial 512MB) e timeout (30s).
- Injeta as variáveis de ambiente (Mongo URI, OpenRouter Key, etc).

### Módulo: API Gateway
- Cria uma HTTP API (v2).
- Faz o "link" (integração) com a Lambda.
- Define a rota `$default` para encaminhar tudo pro FastAPI.

## 3. Estado Remoto (Terraform Backend)
Para não perder o controle da infra, usaremos um bucket S3 para salvar o `terraform.tfstate`.
- **Bucket:** `amon-claw-terraform-state` (exemplo)
- **Locking:** Uma tabela no DynamoDB para evitar que dois deploys rodem ao mesmo tempo.

## 4. Fluxo de Trabalho
1. `terraform init`: Prepara o terreno.
2. `terraform plan`: Mostra o que vai ser criado (O "olha o que eu vou fazer").
3. `terraform apply`: Cria a infra de verdade (Só quando você tiver a conta AWS).
