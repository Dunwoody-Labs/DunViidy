resource "aws_lambda_function" "ses_notifier" {
  function_name = "ses_notifier"
  role          = var.ses_lambda_role_arn
  handler       = "lambda_function.lambda_handler"
  runtime       = "python3.11"
  filename      = "${path.module}/ses_notifier.zip"
  source_code_hash = filebase64sha256("${path.module}/ses_notifier.zip")
  timeout       = 60

        environment {
        variables = {
            BUCKET_NAME  = var.ephemeral_bucket_name
            INPUT_BUCKET = "dunviidy-input"
            FROM_EMAIL   = var.from_email
        }
    }
}


resource "aws_lambda_permission" "allow_s3" {
  statement_id  = "AllowExecutionFromS3"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.ses_notifier.arn
  principal     = "s3.amazonaws.com"
  source_arn    = "arn:aws:s3:::${var.ephemeral_bucket_name}"
}

resource "aws_s3_bucket_notification" "on_vtt_upload" {
  bucket = var.ephemeral_bucket_name

  lambda_function {
    lambda_function_arn = aws_lambda_function.ses_notifier.arn
    events              = ["s3:ObjectCreated:*"]
    filter_suffix       = ".vtt"
  }

  depends_on = [aws_lambda_permission.allow_s3]
}



resource "aws_lambda_function" "transcribe_function" {
  function_name = "transcribe_function"
  role          = aws_iam_role.transcribe_lambda_role.arn
  handler       = "lambda_function.lambda_handler"
  runtime       = "python3.11"
  filename      = "${path.module}/Transcribe.zip"
  timeout       = 180

    environment {
    variables = {
      OUTPUT_BUCKET = var.ephemeral_bucket_name
    }
  }
}

resource "aws_iam_role" "transcribe_lambda_role" {
  name = "lambda_transcribe_role"
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
  name = "transcribe_policy"
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
  name = "lambda_logs_policy"
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