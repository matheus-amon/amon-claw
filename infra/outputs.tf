output "api_gateway_url" {
  description = "URL base do API Gateway"
  value       = module.api_gateway.api_endpoint
}

output "ecr_repository_url" {
  description = "URL do repositório ECR"
  value       = module.ecr.repository_url
}
