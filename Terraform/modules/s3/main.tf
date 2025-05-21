# resource ID added onto the buckets names when they are generated
resource "random_id" "bucket_suffix" {
  byte_length = 4 
}

# input bucket that stores the videos and .txt files from the datasync agent
resource "aws_s3_bucket" "input" {
  bucket = "dunviidy-input-${random_id.bucket_suffix.hex}"
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
  tags = {
    dunviidy = "S3"
  }
}

# output bucket that stores the output from the transcribe function and puts stores it here
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
  tags = {
    dunviidy = "S3"
  }
}