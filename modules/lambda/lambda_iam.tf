# IAM Hex GEnerator
resource "random_id" "iam_suffix" {
  byte_length = 4 
}

# Transcribe Lambda IAM Permissions

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

resource "aws_iam_policy" "transcribe_policy" {
  name = "transcribe_policy_${random_id.iam_suffix.hex}"
  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Action = [
          "transcribe:StartTranscriptionJob"
        ],
        Resource = "*"
      },
      {
        Effect = "Allow",
        Action = [
          "s3:GetObject",
          "s3:PutObject"
        ],
        "Resource": [
         "${var.input_bucket_arn}/*",   
  "       ${var.ephemeral_bucket_arn}/*" 
        ]
      },
      {
        Effect = "Allow",
        Action = [
          "logs:*"
        ],
        Resource = "*"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "transcribe_attachment" {
  role       = aws_iam_role.transcribe_lambda_role.name
  policy_arn = aws_iam_policy.transcribe_policy.arn
}

resource "aws_iam_policy" "lambda_logs_policy" {
  name = "lambda_logs_policy_${random_id.iam_suffix.hex}"
  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ],
        Resource = "*"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_logs_attachment" {
  role       = aws_iam_role.transcribe_lambda_role.name
  policy_arn = aws_iam_policy.lambda_logs_policy.arn
}

# SES Lambda IAM Permissions
resource "aws_iam_role" "ses_lambda_role" {
  name = "lambda_ses_role_${random_id.iam_suffix.hex}"
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

resource "aws_iam_role_policy_attachment" "lambda_ses_exec_policy" {
  role       = aws_iam_role.ses_lambda_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_role_policy_attachment" "lambda_ses_s3_policy" {
  role       = aws_iam_role.ses_lambda_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonS3FullAccess"
}

resource "aws_iam_role_policy_attachment" "lambda_ses_ses_policy" {
  role       = aws_iam_role.ses_lambda_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonSESFullAccess"
}



