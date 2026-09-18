module "network" {
  source             = "./modules/network"
  name               = local.name
  vpc_cidr           = var.vpc_cidr
  availability_zones = var.availability_zones
}
module "compute" {
  source        = "./modules/compute"
  name          = local.name
  vpc_id        = module.network.vpc_id
  subnet_id     = module.network.subnet_ids[0]
  ami_id        = var.ami_id
  instance_type = var.instance_type
}
module "data" {
  source                = "./modules/data"
  name                  = local.name
  vpc_id                = module.network.vpc_id
  subnet_ids            = module.network.subnet_ids
  app_security_group_id = module.compute.security_group_id
  instance_class        = var.db_instance_class
  production            = var.environment == "prod"
}

module "storage" {
  source = "./modules/storage"

  dvc_cache_bucket_name        = "${var.bucket_name}-dvc-cache"
  dataset_releases_bucket_name = "${var.bucket_name}-dataset-releases"
}

locals {
  name = "mp2-${var.environment}"
}
