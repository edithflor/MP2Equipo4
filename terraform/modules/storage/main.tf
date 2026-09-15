variable "bucket_name" {
  type = string
}
resource "aws_s3_bucket" "dataset" {
  bucket        = var.bucket_name
  force_destroy = false
}
resource "aws_s3_bucket_versioning" "dataset" {
  bucket = aws_s3_bucket.dataset.id
  versioning_configuration {
    status = "Enabled"
  }
}
resource "aws_s3_bucket_public_access_block" "dataset" {
  bucket                  = aws_s3_bucket.dataset.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}
resource "aws_s3_bucket_server_side_encryption_configuration" "dataset" {
  bucket = aws_s3_bucket.dataset.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}
resource "aws_s3_bucket_policy" "tls" {
  bucket = aws_s3_bucket.dataset.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Deny"
      Principal = "*"
      Action    = "s3:*"
      Resource  = [aws_s3_bucket.dataset.arn, "${aws_s3_bucket.dataset.arn}/*"]
      Condition = { Bool = { "aws:SecureTransport" = "false" } }
    }]
  })
}
output "bucket_arn" {
  value = aws_s3_bucket.dataset.arn
}
output "bucket_name" {
  value = aws_s3_bucket.dataset.id
}
