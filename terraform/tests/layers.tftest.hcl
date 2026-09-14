mock_provider "aws" {}

run "network_is_private" {
  command = plan
  module { source = "./modules/network" }
  variables {
    name               = "mp2-test"
    vpc_cidr           = "10.42.0.0/16"
    availability_zones = ["us-east-1a", "us-east-1b"]
  }
  assert {
    condition     = length(aws_subnet.private) == 2 && alltrue([for s in aws_subnet.private : !s.map_public_ip_on_launch])
    error_message = "RDS necesita dos subredes privadas."
  }
}
run "compute_is_private" {
  command = plan
  module { source = "./modules/compute" }
  variables {
    name          = "mp2-test"
    vpc_id        = "vpc-0123456789abcdef0"
    subnet_id     = "subnet-0123456789abcdef0"
    ami_id        = "ami-0123456789abcdef0"
    instance_type = "t3.micro"
  }
  assert {
    condition     = !aws_instance.app.associate_public_ip_address && aws_instance.app.metadata_options[0].http_tokens == "required"
    error_message = "EC2 debe ser privado y exigir IMDSv2."
  }
}
run "production_database" {
  command = plan
  module { source = "./modules/data" }
  variables {
    name                  = "mp2-prod"
    vpc_id                = "vpc-0123456789abcdef0"
    subnet_ids            = ["subnet-0123456789abcdef0", "subnet-1123456789abcdef0"]
    app_security_group_id = "sg-0123456789abcdef0"
    instance_class        = "db.t3.micro"
    production            = true
  }
  assert {
    condition     = aws_db_instance.database.engine == "mariadb" && aws_db_instance.database.manage_master_user_password && !aws_db_instance.database.publicly_accessible && aws_db_instance.database.multi_az && aws_db_instance.database.deletion_protection
    error_message = "PROD requiere MariaDB privado con clave administrada, Multi-AZ y protección."
  }
}
run "storage_is_versioned" {
  command = plan
  module { source = "./modules/storage" }
  variables { bucket_name = "mp2-test-bucket-dev" }
  assert {
    condition     = aws_s3_bucket_versioning.dataset.versioning_configuration[0].status == "Enabled" && aws_s3_bucket_public_access_block.dataset.block_public_policy
    error_message = "El bucket debe estar versionado y bloquear acceso público."
  }
}
