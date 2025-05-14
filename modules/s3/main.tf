resource "random_id" "bucket_suffix" {
  byte_length = 4 
}

resource "aws_s3_bucket" "input" {
  bucket = "dunviidy-input-${random_id.bucket_suffix.hex}"
  lifecycle {
    prevent_destroy = false
  }
}


resource "aws_s3_bucket" "output" {
  bucket = "dunviidy-output-${random_id.bucket_suffix.hex}"

  lifecycle {
    prevent_destroy = true
  }

  lifecycle_rule {
    id      = "output-lifecycle-rule"
    enabled = true

    expiration {
      days = 2
    }
  }
}