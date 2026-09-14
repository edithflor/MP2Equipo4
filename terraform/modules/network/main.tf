variable "aws_region" {
  type = string
}
resource "aws_vpc" "dataset" {
  cidr_block           = "10.42.0.0/16"
  enable_dns_support   = true
  enable_dns_hostnames = true
}
resource "aws_subnet" "private" {
  vpc_id                  = aws_vpc.dataset.id
  cidr_block              = "10.42.1.0/24"
  map_public_ip_on_launch = false
}
resource "aws_route_table" "private" {
  vpc_id = aws_vpc.dataset.id
}
resource "aws_route_table_association" "private" {
  subnet_id      = aws_subnet.private.id
  route_table_id = aws_route_table.private.id
}
resource "aws_vpc_endpoint" "s3" {
  vpc_id            = aws_vpc.dataset.id
  service_name      = "com.amazonaws.${var.aws_region}.s3"
  vpc_endpoint_type = "Gateway"
  route_table_ids   = [aws_route_table.private.id]
}
output "s3_endpoint_id" {
  value = aws_vpc_endpoint.s3.id
}
