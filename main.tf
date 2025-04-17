provider "aws" {
  region = "us-east-2"
}

module "s3" {
  source = "./modules/s3"
}

module "iam" {
  source = "./modules/iam"
  input_bucket_name     = module.s3.input_bucket_name
  ephemeral_bucket_name = module.s3.ephemeral_bucket_name
}

module "lambda" {
  source                 = "./modules/lambda"
  ses_lambda_role_arn    = module.iam.ses_lambda_role_arn
  ephemeral_bucket_name  = module.s3.ephemeral_bucket_name
  from_email             = "your_verified_email@example.com"
  input_bucket_arn       = module.s3.input_bucket_arn   
  ephemeral_bucket_arn   = module.s3.ephemeral_bucket_arn   
}