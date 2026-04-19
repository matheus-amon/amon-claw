variable "project_name" { type = string }
variable "environment" { type = string }
variable "image_uri" { type = string }
variable "execution_role_arn" { type = string }
variable "environment_variables" {
  type    = map(string)
  default = {}
}
