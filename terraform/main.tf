module "network" {
  source     = "./modules/network"
  aws_region = var.aws_region
}
module "storage" {
  source      = "./modules/storage"
  bucket_name = var.bucket_name
}
module "identity" {
  source                   = "./modules/identity"
  bucket_arn               = module.storage.bucket_arn
  github_repository        = var.github_repository
  github_branch            = var.github_branch
  github_oidc_provider_arn = var.github_oidc_provider_arn
}
