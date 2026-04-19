variable "aws_region" {
  description = "Região da AWS onde os recursos serão criados"
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Nome do projeto"
  type        = string
  default     = "amon-claw"
}

variable "environment" {
  description = "Ambiente (dev, stg, prod)"
  type        = string
  default     = "prod"
}

variable "mongodb_uri" {
  description = "URI de conexão com o MongoDB Atlas"
  type        = string
  sensitive   = true
}

variable "openrouter_api_key" {
  description = "API Key do OpenRouter"
  type        = string
  sensitive   = true
}
