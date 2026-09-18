variable "name" { type = string }
variable "vpc_cidr" { type = string }
variable "availability_zones" { type = list(string) }
resource "aws_vpc" "dataset" {
  cidr_block           = var.vpc_cidr
  enable_dns_support   = true
  enable_dns_hostnames = true
  tags                 = { Name = var.name }
}
resource "aws_subnet" "private" {
  count                   = 2
  vpc_id                  = aws_vpc.dataset.id
  cidr_block              = cidrsubnet(var.vpc_cidr, 8, count.index + 1)
  availability_zone       = var.availability_zones[count.index]
  map_public_ip_on_launch = false
  tags                    = { Name = "${var.name}-private-${count.index}" }
}
resource "aws_route_table" "private" { vpc_id = aws_vpc.dataset.id }
resource "aws_route_table_association" "private" {
  count          = 2
  subnet_id      = aws_subnet.private[count.index].id
  route_table_id = aws_route_table.private.id
}
output "vpc_id" { value = aws_vpc.dataset.id }
output "subnet_ids" { value = aws_subnet.private[*].id }

data "aws_region" "current" {}

resource "aws_vpc_endpoint" "s3" {
  vpc_id            = aws_vpc.dataset.id
  service_name      = "com.amazonaws.${data.aws_region.current.region}.s3"
  vpc_endpoint_type = "Gateway"

  route_table_ids = [
    aws_route_table.private.id
  ]

  tags = {
    Name = "${var.name}-s3-endpoint"
  }
}

output "s3_vpc_endpoint_id" {
  value = aws_vpc_endpoint.s3.id
}
