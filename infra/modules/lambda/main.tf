resource "aws_lambda_function" "this" {
  function_name = "${var.project_name}-function-${var.environment}"
  role          = var.execution_role_arn
  package_type  = "Image"
  image_uri     = var.image_uri

  architectures = ["arm64"] # Graviton for cost & performance

  timeout     = 30  # Adjust as needed (seconds)
  memory_size = 512 # Adjust as needed (MB)

  environment {
    variables = var.environment_variables
  }

  tracing_config {
    mode = "Active"
  }

  # Se for o primeiro deploy e a imagem nao existir ainda, 
  # talvez voce queira criar com uma dummy image e ignorar mudancas
  # lifecycle {
  #   ignore_changes = [image_uri]
  # }
}

resource "aws_cloudwatch_log_group" "this" {
  name              = "/aws/lambda/${aws_lambda_function.this.function_name}"
  retention_in_days = 14
}
