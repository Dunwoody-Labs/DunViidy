variable "ses_lambda_role_arn" {}
variable "ephemeral_bucket_name" {}
variable "from_email" {}
variable "input_bucket_arn" {
  description = "ARN of the input S3 bucket"
  type        = string
}

variable "ephemeral_bucket_arn" {
  description = "ARN of the ephemeral S3 bucket"
  type        = string
}
