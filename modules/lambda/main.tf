
# making the zip files for the functions
data "archive_file" "transcribe_zip" {
  type = "zip"
  source_dir = "${path.module}/lambda_srcs/transcribe_function"
  output_path = "${path.module}/Transcribe.zip"
}

data "archive_file" "ses_zip" {
  type = "zip"
  source_dir = "${path.module}/lambda_srcs/ses_function"
  output_path = "${path.module}/Ses.zip"
}

data "archive_file" "bucket_zip" {
  type = "zip"
  source_dir = "${path.module}/lambda_srcs/ephemeral_bucket_function"
  output_path = "${path.module}/EphemeralBucket.zip"
}

# transcribe function
resource "aws_lambda_function" "transcribe_function" {
  function_name = "dunviidy_transcribe_function"
  role          = aws_iam_role.transcribe_lambda_role.arn
  handler       = "lambda_function.lambda_handler"
  runtime       = "python3.11"
  filename      = data.archive_file.transcribe_zip.output_path
  source_code_hash = filebase64sha256(data.archive_file.transcribe_zip.output_path)
  timeout       = 180

    environment {
    variables = {
      OUTPUT_BUCKET = var.ephemeral_bucket_name
    }
  }
}

# ses function
resource "aws_lambda_function" "ses_function" {
  function_name = "dunviidy_ses_function"
  role          = aws_iam_role.ses_lambda_role.arn
  handler       = "lambda_function.lambda_handler"
  runtime       = "python3.11"
  filename      = data.archive_file.ses_zip.output_path
  source_code_hash = filebase64sha256(data.archive_file.ses_zip.output_path)
  timeout       = 180
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
  function_name = aws_lambda_function.ses_function.arn
  principal     = "s3.amazonaws.com"
  source_arn    = "arn:aws:s3:::${var.ephemeral_bucket_name}"
}

resource "aws_s3_bucket_notification" "on_vtt_upload" {
  bucket = var.ephemeral_bucket_name

  lambda_function {
    lambda_function_arn = aws_lambda_function.ses_function.arn
    events              = ["s3:ObjectCreated:*"]
    filter_suffix       = ".vtt"
  }

  depends_on = [aws_lambda_permission.allow_s3]
}
