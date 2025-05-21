# Dunviidy Lambda Module
This module sets up Dunviidy's Lambda function which is used to:
  - Create VTT files
  - Move files from the input to output bucket
  - Send an email to the user who submitted the video and .txt file

It will create:
  - 1 Lambda Function
  - 1 IAM Role

The Lambda function code is located in the lambda_srcs\transcribe_function folder where you can view and edit it to match your specific use case. Currently, the sender Email for SES is hardcoded, and will need to be changed to suit your needs.

## Lambda Function Flow
1. The Lambda function is triggered when a video file is created in the S3 Input bucket. It only triggers from .mp4 files and ignores other file types.

2. Once triggered, the function looks in the input bucket for both a video file and a matching .txt file with the same name. The .txt file should contain an email address which is stored as a variable.

3. After finding both files, it initiates a transcribe job for the video and waits for transcription completion. The output is generated in .vtt format.

4. The function then:
   - Stores the .vtt file (named same as video) in the S3 Output bucket
   - Copies the video from Input bucket to Output bucket

5. The function generates two presigned URLs:
   - One for the .vtt file
   - One for the video file

6. Finally, it creates and sends an email to the stored email address containing both presigned URLs.

## How to use the Function
Outside of the terraform deployment, the Lambda function has one variable that need to be assigned in order to function properly. This is assigned in the lambda function itself under the name "SENDER_EMAIL". The email needs to be updated with an SES verified email. Once this change has been made, the terraform can be applied.

## IAM 

This function requires a specific set of permissions to opperate:
1. s3:CreateBucket
2. s3:PutObject
3. s3:GetObject
4. s3:DeleteObject
5. s3:ListBucket
6. transcribe:StartTranscriptionJob
7. transcribe:GetTranscriptionJob
8. ses:SendEmail
