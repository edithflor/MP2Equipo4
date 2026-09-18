terraform {
  required_version = ">= 1.9, < 2.0"

  backend "s3" {
    bucket       = "mp2-equipo4-terraform-state-prod"
    key          = "prod/terraform.tfstate"
    region       = "us-east-1"
    use_lockfile = true
    encrypt      = true
  }

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }
  }
}
