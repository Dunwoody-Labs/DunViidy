# this .tf file displays the input and output bucket names and arns when terraform apply is run

output "input_bucket_name" {
  value = aws_s3_bucket.input.bucket
}

output "input_bucket_arn" {
  value = aws_s3_bucket.input.arn
}

output "output_bucket_name" {
  value = aws_s3_bucket.output.bucket
}

output "output_bucket_arn" {
  value = aws_s3_bucket.output.arn
}