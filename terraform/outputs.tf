output "instance_id" {
  value = module.compute.instance_id
}

output "database_address" {
  value = module.data.address
}

output "dvc_cache_bucket_name" {
  value = module.storage.dvc_cache_bucket_name
}

output "dataset_releases_bucket_name" {
  value = module.storage.dataset_releases_bucket_name
}

output "vpc_id" {
  value = module.network.vpc_id
}

output "s3_vpc_endpoint_id" {
  value = module.network.s3_vpc_endpoint_id
}
