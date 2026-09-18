variable "dvc_cache_bucket_name" {
  type = string
}

variable "dataset_releases_bucket_name" {
  type = string
}

resource "aws_s3_bucket" "dvc_cache" {
  bucket        = var.dvc_cache_bucket_name
  force_destroy = false
}

resource "aws_s3_bucket" "dataset_releases" {
  bucket        = var.dataset_releases_bucket_name
  force_destroy = false
}

resource "aws_s3_bucket_versioning" "dvc_cache" {
  bucket = aws_s3_bucket.dvc_cache.id

  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_versioning" "dataset_releases" {
  bucket = aws_s3_bucket.dataset_releases.id

  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_public_access_block" "dvc_cache" {
  bucket                  = aws_s3_bucket.dvc_cache.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_public_access_block" "dataset_releases" {
  bucket                  = aws_s3_bucket.dataset_releases.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_server_side_encryption_configuration" "dvc_cache" {
  bucket = aws_s3_bucket.dvc_cache.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "dataset_releases" {
  bucket = aws_s3_bucket.dataset_releases.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_policy" "dvc_cache_tls" {
  bucket = aws_s3_bucket.dvc_cache.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Deny"
      Principal = "*"
      Action    = "s3:*"
      Resource = [
        aws_s3_bucket.dvc_cache.arn,
        "${aws_s3_bucket.dvc_cache.arn}/*"
      ]
      Condition = {
        Bool = {
          "aws:SecureTransport" = "false"
        }
      }
    }]
  })
}

resource "aws_s3_bucket_policy" "dataset_releases_tls" {
  bucket = aws_s3_bucket.dataset_releases.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Deny"
      Principal = "*"
      Action    = "s3:*"
      Resource = [
        aws_s3_bucket.dataset_releases.arn,
        "${aws_s3_bucket.dataset_releases.arn}/*"
      ]
      Condition = {
        Bool = {
          "aws:SecureTransport" = "false"
        }
      }
    }]
  })
}

output "dvc_cache_bucket_name" {
  value = aws_s3_bucket.dvc_cache.id
}

output "dataset_releases_bucket_name" {
  value = aws_s3_bucket.dataset_releases.id
}
