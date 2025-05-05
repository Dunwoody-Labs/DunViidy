output "input_bucket_name" {
  value = aws_s3_bucket.input.bucket
}

output "input_bucket_arn" {
  value = aws_s3_bucket.input.arn
}

output "ephemeral_bucket_name" {
  value = aws_s3_bucket.ephemeral.bucket
}

output "ephemeral_bucket_arn" {
  value = aws_s3_bucket.ephemeral.arn
}