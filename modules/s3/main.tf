resource "random_id" "bucket_suffix" {
  byte_length = 4 
}

resource "aws_s3_bucket" "input" {
  bucket = "dunviidy-input-${random_id.bucket_suffix.hex}"
}

resource "aws_s3_bucket" "ephemeral" {
  bucket = "ephemeral-bucket-${random_id.bucket_suffix.hex}"
  acl    = "private"
}