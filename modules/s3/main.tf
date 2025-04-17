resource "random_id" "bucket_suffix" {
  byte_length = 4 
}

resource "aws_s3_bucket" "input" {
  bucket = "dunviidy-input-${random_id.bucket_suffix.hex}"
}

resource "aws_s3_bucket" "ephemeral" {
  bucket = "dunviidy-transcription-${random_id.bucket_suffix.hex}"
}

resource "aws_s3_bucket_lifecycle_configuration" "ephemeral_lifecycle" {
  bucket = aws_s3_bucket.ephemeral.id

  rule {
    id     = "delete_after_3_days"
    status = "Enabled"

    filter {
      prefix = ""
    } 

    expiration {
      days = 3
    }
  }
}
