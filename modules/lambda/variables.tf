variable "input_bucket_name" {
  description = "Name of the input S3 bucket"
  type        = string
}

variable "input_bucket_arn" {
  description = "ARN of the input S3 bucket"
  type        = string
}

variable "output_bucket_name" {
  description = "Name of the output S3 bucket"
  type        = string
}

variable "from_email" {
  description = "Verified SES email address to send from"
  type        = string
}

variable "ses_lambda_role_arn" {
  description = "IAM role ARN for the SES Lambda function"
  type        = string
}