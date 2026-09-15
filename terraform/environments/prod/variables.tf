variable "aws_region" {
  type    = string
  default = "us-east-1"
}
variable "availability_zones" {
  type    = list(string)
  default = ["us-east-1a", "us-east-1b"]
}
variable "ami_id" { type = string }
variable "bucket_name" {
  type = string
  validation {
    condition     = endswith(var.bucket_name, "-prod")
    error_message = "Usa un bucket globalmente unico terminado en -prod."
  }
}
