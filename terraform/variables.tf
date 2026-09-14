variable "environment" {
  type = string
  validation {
    condition     = contains(["dev", "prod"], var.environment)
    error_message = "environment debe ser dev o prod."
  }
}
variable "vpc_cidr" { type = string }
variable "availability_zones" {
  type = list(string)
  validation {
    condition     = length(var.availability_zones) == 2 && length(distinct(var.availability_zones)) == 2
    error_message = "Se requieren dos zonas distintas para RDS."
  }
}
variable "ami_id" {
  description = "AMI Linux x86_64 elegida para la región; requerida solo para plan/apply."
  type        = string
}
variable "bucket_name" {
  type = string
}
variable "instance_type" {
  type    = string
  default = "t3.micro"
}
variable "db_instance_class" {
  type    = string
  default = "db.t3.micro"
}
