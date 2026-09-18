provider "aws" {
  region = var.aws_region
  default_tags {
    tags = { Project = "MP2Equipo4", Environment = "dev", ManagedBy = "Terraform" }
  }
}
module "stack" {
  source             = "../.."
  environment        = "dev"
  vpc_cidr           = "10.42.0.0/16"
  availability_zones = var.availability_zones
  ami_id             = var.ami_id
  bucket_name        = var.bucket_name
}

output "instance_id" {
  value = module.stack.instance_id
}

output "database_address" {
  value = module.stack.database_address
}

output "dvc_cache_bucket_name" {
  value = module.stack.dvc_cache_bucket_name
}

output "dataset_releases_bucket_name" {
  value = module.stack.dataset_releases_bucket_name
}

output "s3_vpc_endpoint_id" {
  value = module.stack.s3_vpc_endpoint_id
}
