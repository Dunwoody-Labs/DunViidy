# region that all the architecture is created in
provider "aws" {
  region = "us-east-2"
}

# s3 module being called on
module "s3" {
  source = "./modules/s3"
}

# lambda module being called on
module "lambda" {
  source                 = "./modules/lambda"
  input_bucket_name      = module.s3.input_bucket_name
  output_bucket_name     = module.s3.output_bucket_name
  from_email             = "your_verified_email@example.com"
  input_bucket_arn       = module.s3.input_bucket_arn   
}
