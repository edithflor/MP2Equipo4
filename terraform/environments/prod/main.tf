provider "aws" {
  region = var.aws_region
  default_tags {
    tags = { Project = "MP2Equipo4", Environment = "prod", ManagedBy = "Terraform" }
  }
}
module "stack" {
  source             = "../.."
  environment        = "prod"
  vpc_cidr           = "10.43.0.0/16"
  availability_zones = var.availability_zones
  ami_id             = var.ami_id
  bucket_name        = var.bucket_name
}
output "instance_id" { value = module.stack.instance_id }
output "database_address" { value = module.stack.database_address }
output "bucket_name" { value = module.stack.bucket_name }
