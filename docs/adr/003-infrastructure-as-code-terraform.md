# ADR 003: Infrastructure as Code with Terraform

## Contexto
A aplicação Amon Claw precisa de uma infraestrutura escalável, reprodutível e versionada. Como o objetivo é ser "Cloud Native" na AWS, precisamos de uma ferramenta para gerenciar recursos sem intervenção manual.

## Decisão
Utilizar o **Terraform** como ferramenta de IaC. O código de infra residirá em uma pasta `/infra` no repositório principal.

## Status
Aceito.

## Consequências
- **Prós:** Garantia de ambientes idênticos, versionamento e facilidade de recriar a infra.
- **Contras:** Necessidade de gerenciar o `tfstate` (usaremos S3 + DynamoDB).

## Mitigação
Pipeline de CI/CD que valida mudanças via `terraform plan`.
