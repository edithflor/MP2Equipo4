variable "aws_region" {
  type    = string
  default = "us-east-1"
}
variable "bucket_name" {
  description = "Nombre globalmente único del bucket PROD para DVC."
  type        = string
}
variable "github_repository" {
  description = "Repositorio autorizado: propietario/nombre."
  type        = string
  default     = "edithflor/MP2Equipo4"
}
variable "github_branch" {
  description = "Única rama autorizada a asumir el rol de datos."
  type        = string
  default     = "main"
}
variable "github_oidc_provider_arn" {
  description = "ARN del proveedor GitHub existente; null crea uno (uno por cuenta)."
  type        = string
  default     = null
}
