# Unique suffix for naming
resource "random_id" "iam_suffix" {
  byte_length = 4
}

# IAM Role for Transcribe Lambda
resource "aws_iam_role" "transcribe_lambda_role" {
  name = "lambda_transcribe_role_${random_id.iam_suffix.hex}"
  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Action = "sts:AssumeRole",
      Principal = {
        Service = "lambda.amazonaws.com"
      },
      Effect = "Allow"
    }]
  })
}

# Inline policy for S3 and Transcribe permissions
resource "aws_iam_role_policy" "lambda_s3_transcribe_policy" {
  name = "lambda-s3-transcribe"
  role = aws_iam_role.transcribe_lambda_role.id

  policy = jsonencode({
    Version: "2012-10-17",
    Statement: [
      {
        Effect: "Allow",
        Action: [
          "s3:CreateBucket",
          "s3:PutBucketPolicy",
          "s3:PutObject",
          "s3:GetObject",
          "s3:ListBucket",
          "transcribe:StartTranscriptionJob",
          "transcribe:GetTranscriptionJob",
          "ses:SendEmail"
        ],
        Resource: "*"
      },
    ]
  })
}

# Logs policy for Transcribe Lambda
resource "aws_iam_policy" "lambda_logs_policy" {
  name = "lambda_logs_policy_${random_id.iam_suffix.hex}"
  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect: "Allow",
        Action: [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ],
        Resource: "*"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_logs_attachment" {
  role       = aws_iam_role.transcribe_lambda_role.name
  policy_arn = aws_iam_policy.lambda_logs_policy.arn
}

resource "aws_s3_bucket_policy" "transcribe_access" {
  bucket = var.input_bucket_name

  policy = jsonencode({
    Version = "2012-10-17",
    Statement: [
      {
        Sid: "AllowTranscribeReadAccess",
        Effect: "Allow",
        Principal: {
          Service: "transcribe.amazonaws.com"
        },
        Action: "s3:GetObject",
        Resource: "arn:aws:s3:::${var.input_bucket_name}/*",
        Condition: {
          StringEquals: {
            "aws:SourceAccount": data.aws_caller_identity.current.account_id
          }
        }
      }
    ]
  })
}

data "aws_caller_identity" "current" {}