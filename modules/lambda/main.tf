# Create ZIP archives for Lambda functions
data "archive_file" "transcribe_zip" {
  type        = "zip"
  source_dir  = "${path.module}/lambda_srcs/transcribe_function"
  output_path = "${path.module}/Transcribe.zip"
}

# Transcribe Lambda
resource "aws_lambda_function" "transcribe_function" {
  function_name    = "dunviidy_transcribe_function"
  role             = aws_iam_role.transcribe_lambda_role.arn
  handler          = "lambda_function.lambda_handler"
  runtime          = "python3.11"
  filename         = data.archive_file.transcribe_zip.output_path
  source_code_hash = filebase64sha256(data.archive_file.transcribe_zip.output_path)
  timeout          = 180

  environment {
    variables = {
      OUTPUT_BUCKET = var.output_bucket_name
      INPUT_BUCKET  = var.input_bucket_name
    }
  }

  tags = {
    dunviidy = "lambda"
  }
}

resource "aws_lambda_permission" "allow_s3_2" {
  statement_id  = "AllowS3Invoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.transcribe_function.function_name
  principal     = "s3.amazonaws.com"
  source_arn    = "arn:aws:s3:::${var.input_bucket_name}"
}

resource "aws_s3_bucket_notification" "on_mp4_upload" {
  bucket = var.input_bucket_name

  lambda_function {
    lambda_function_arn = aws_lambda_function.transcribe_function.arn
    events              = ["s3:ObjectCreated:*"]
    filter_suffix       = ".mp4"
  }

  depends_on = [aws_lambda_permission.allow_s3_2]
}