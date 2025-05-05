import json
import boto3
import uuid
import time
import logging
import urllib.parse
from datetime import datetime

# Initialize logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize AWS clients
s3_client = boto3.client('s3')
transcribe_client = boto3.client('transcribe')
ses_client = boto3.client('ses')

def lambda_handler(event, context):
    # Decode the S3 object key (handle spaces, parentheses, etc.)
    source_bucket = event['Records'][0]['s3']['bucket']['name']
    file_key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'])
    logger.info(f"Triggered by file: {file_key}")

    # Only process .mp4 files
    if not file_key.endswith('.mp4'):
        logger.info(f"Skipping non-MP4 file: {file_key}")
        return {'statusCode': 200, 'body': 'Not an MP4 file, skipping.'}

    base_name = file_key.rsplit('.', 1)[0]
    txt_key = base_name + '.txt'

    try:
        txt_obj = s3_client.get_object(Bucket=source_bucket, Key=txt_key)
        email_address = txt_obj['Body'].read().decode('utf-8').strip()
        logger.info(f"Email address found in {txt_key}: {email_address}")
    except Exception as e:
        logger.error(f"Failed to find or read the .txt file: {txt_key} - {str(e)}")
        return {'statusCode': 400, 'body': f"Missing or unreadable .txt file for {file_key}"}

    # Create unique ephemeral bucket
    timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
    ephemeral_bucket = f"transcribe-temp-{timestamp}-{str(uuid.uuid4())[:8]}"

    try:
        region = boto3.session.Session().region_name
        s3_client.create_bucket(
            Bucket=ephemeral_bucket,
            CreateBucketConfiguration={'LocationConstraint': region}
        )
        logger.info(f"Created ephemeral bucket: {ephemeral_bucket} in region {region}")
    except Exception as e:
        logger.error(f"Bucket creation failed: {str(e)}")
        return {'statusCode': 500, 'body': f"Failed to create bucket: {str(e)}"}

    try:
        s3_client.copy_object(
            Bucket=ephemeral_bucket,
            CopySource={'Bucket': source_bucket, 'Key': file_key},
            Key=file_key
        )
        logger.info(f"Copied {file_key} to {ephemeral_bucket}")
    except Exception as e:
        logger.error(f"Copy failed: {str(e)}")
        return {'statusCode': 500, 'body': f"Failed to copy video: {str(e)}"}

    # Start transcription job
    job_name = f"transcribe-{timestamp}-{str(uuid.uuid4())[:8]}"
    job_uri = f"s3://{source_bucket}/{file_key}"
    try:
        transcribe_client.start_transcription_job(
            TranscriptionJobName=job_name,
            Media={'MediaFileUri': job_uri},
            MediaFormat='mp4',
            LanguageCode='en-US',
            OutputBucketName=ephemeral_bucket,
            Subtitles={'Formats': ['vtt']}
        )
        logger.info(f"Started Transcribe job: {job_name}")
    except Exception as e:
        logger.error(f"Failed to start Transcribe job: {str(e)}")
        return {'statusCode': 500, 'body': f"Failed to start Transcribe job: {str(e)}"}

    # Wait for transcription to complete
    while True:
        status = transcribe_client.get_transcription_job(TranscriptionJobName=job_name)
        job_status = status['TranscriptionJob']['TranscriptionJobStatus']
        if job_status in ['COMPLETED', 'FAILED']:
            break
        logger.info(f"Waiting for transcription job {job_name} to complete...")
        time.sleep(5)

    if job_status == 'FAILED':
        logger.error(f"Transcription job failed: {status}")
        return {'statusCode': 500, 'body': 'Transcription job failed'}

    logger.info(f"Transcription job {job_name} completed")

    # Generate presigned URLs
    vtt_key = f"{job_name}.vtt"
    try:
        vtt_url = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': ephemeral_bucket, 'Key': vtt_key},
            ExpiresIn=3600
        )
        video_url = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': ephemeral_bucket, 'Key': file_key},
            ExpiresIn=3600
        )
        logger.info("Generated presigned URLs for video and subtitles")
    except Exception as e:
        logger.error(f"Failed to generate presigned URLs: {str(e)}")
        return {'statusCode': 500, 'body': 'Failed to generate download links'}

    # Send email using SES
    try:
        ses_client.send_email(
            Source='raslukw@dunwoody.edu',  # Replace with a verified email
            Destination={'ToAddresses': [email_address]},
            Message={
                'Subject': {'Data': 'Your transcription is ready'},
                'Body': {
                    'Text': {
                        'Data': f"""Your files are ready for download:

Video: {video_url}
Subtitles (.vtt): {vtt_url}

These links will expire in 1 hour.
"""
                    }
                }
            }
        )
        logger.info(f"Email sent to {email_address}")
    except Exception as e:
        logger.error(f"Failed to send email: {str(e)}")
        return {'statusCode': 500, 'body': 'Failed to send email'}

    return {
        'statusCode': 200,
        'body': json.dumps({
            'message': 'Transcription complete and email sent',
            'email': email_address,
            'ephemeral_bucket': ephemeral_bucket,
            'video_url': video_url,
            'vtt_url': vtt_url
        })
    }
