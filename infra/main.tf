module "ecr" {
  source = "./modules/ecr"

  repository_name = "${var.project_name}-repo-${var.environment}"
}

module "iam" {
  source = "./modules/iam"

  project_name = var.project_name
  environment  = var.environment
}

module "lambda" {
  source = "./modules/lambda"

  project_name      = var.project_name
  environment       = var.environment
  image_uri         = "${module.ecr.repository_url}:latest" # Em CI/CD, isso muda pra tag exata (ex: git hash)
  execution_role_arn= module.iam.lambda_role_arn

  environment_variables = {
    MONGODB__URI       = var.mongodb_uri
    OPENROUTER_API_KEY = var.openrouter_api_key
    API__DEBUG         = "False"
  }
}

module "api_gateway" {
  source = "./modules/api_gateway"

  project_name     = var.project_name
  environment      = var.environment
  lambda_invoke_arn= module.lambda.lambda_invoke_arn
  lambda_name      = module.lambda.lambda_function_name
}
