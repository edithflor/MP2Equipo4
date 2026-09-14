variable "name" { type = string }
variable "vpc_id" { type = string }
variable "subnet_id" { type = string }
variable "ami_id" { type = string }
variable "instance_type" { type = string }
resource "aws_security_group" "app" {
  name_prefix = "${var.name}-app-"
  description = "Aplicacion privada; sin ingreso publico ni SSH."
  vpc_id      = var.vpc_id
}
resource "aws_instance" "app" {
  ami                         = var.ami_id
  instance_type               = var.instance_type
  subnet_id                   = var.subnet_id
  vpc_security_group_ids      = [aws_security_group.app.id]
  associate_public_ip_address = false
  metadata_options {
    http_tokens = "required"
  }
  root_block_device { encrypted = true }
  tags = { Name = var.name }
}
output "instance_id" { value = aws_instance.app.id }
output "security_group_id" { value = aws_security_group.app.id }
