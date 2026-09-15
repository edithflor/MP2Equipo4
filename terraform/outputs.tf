output "instance_id" { value = module.compute.instance_id }
output "database_address" { value = module.data.address }
output "bucket_name" { value = module.storage.bucket_name }
output "vpc_id" { value = module.network.vpc_id }
