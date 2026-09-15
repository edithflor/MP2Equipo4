output "bucket_name" {
  value = module.storage.bucket_name
}
output "github_role_arn" {
  value = module.identity.role_arn
}
output "s3_endpoint_id" {
  value = module.network.s3_endpoint_id
}
output "dvc_remote_url" {
  value = "s3://${module.storage.bucket_name}/dvc"
}
