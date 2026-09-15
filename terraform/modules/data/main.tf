variable "name" { type = string }
variable "vpc_id" { type = string }
variable "subnet_ids" { type = list(string) }
variable "app_security_group_id" { type = string }
variable "instance_class" { type = string }
variable "production" { type = bool }
resource "aws_security_group" "database" {
  name_prefix = "${var.name}-db-"
  vpc_id      = var.vpc_id
}
resource "aws_vpc_security_group_ingress_rule" "from_app" {
  security_group_id            = aws_security_group.database.id
  referenced_security_group_id = var.app_security_group_id
  from_port                    = 3306
  to_port                      = 3306
  ip_protocol                  = "tcp"
}
resource "aws_vpc_security_group_egress_rule" "to_database" {
  security_group_id            = var.app_security_group_id
  referenced_security_group_id = aws_security_group.database.id
  from_port                    = 3306
  to_port                      = 3306
  ip_protocol                  = "tcp"
}
resource "aws_db_subnet_group" "database" {
  name       = var.name
  subnet_ids = var.subnet_ids
}
resource "aws_db_instance" "database" {
  identifier                  = var.name
  engine                      = "mariadb"
  instance_class              = var.instance_class
  allocated_storage           = 20
  storage_encrypted           = true
  db_name                     = "dataset_quality"
  username                    = "dataset_admin"
  manage_master_user_password = true
  db_subnet_group_name        = aws_db_subnet_group.database.name
  vpc_security_group_ids      = [aws_security_group.database.id]
  publicly_accessible         = false
  multi_az                    = var.production
  backup_retention_period     = var.production ? 7 : 1
  deletion_protection         = var.production
  skip_final_snapshot         = !var.production
  final_snapshot_identifier   = "${var.name}-final"
}
output "address" { value = aws_db_instance.database.address }
