import json
import boto3
import uuid
import time
import logging
import urllib.parse
from datetime import datetime

# Set up logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    # Initialize AWS clients
    s3_client = boto3.client('s3')
    transcribe_client = boto3.client('transcribe')
    
    logger.info("Received event: %s", json.dumps(event))

    try:
        # Get the source bucket and file key from the event
        source_bucket = event['Records'][0]['s3']['bucket']['name']
        raw_key = event['Records'][0]['s3']['object']['key']
        file_key = urllib.parse.unquote_plus(raw_key)
        logger.info(f"Source bucket: {source_bucket}")
        logger.info(f"Decoded file key: {file_key}")
        
        # Verify that the object exists
        try:
            s3_client.head_object(Bucket=source_bucket, Key=file_key)
            logger.info("Source object exists, proceeding to copy.")
        except s3_client.exceptions.ClientError:
            logger.error(f"File not found: {file_key}", exc_info=True)
            raise Exception(f"File '{file_key}' does not exist in bucket '{source_bucket}'")
        
        # Create unique ephemeral bucket name
        timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
        ephemeral_bucket = f"Dunviidy-Output-{timestamp}-{str(uuid.uuid4())[:8]}".lower()
        logger.info(f"Generated ephemeral bucket name: {ephemeral_bucket}")
        
        # Create ephemeral bucket (handle region correctly)
        region = boto3.session.Session().region_name
        logger.info(f"Current AWS region: {region}")
        if region == 'us-east-1':
            s3_client.create_bucket(Bucket=ephemeral_bucket)
        else:
            s3_client.create_bucket(
                Bucket=ephemeral_bucket,
                CreateBucketConfiguration={'LocationConstraint': region}
            )
        logger.info(f"Created ephemeral bucket: {ephemeral_bucket}")
        
        # Copy original file to ephemeral bucket
        s3_client.copy_object(
            Bucket=ephemeral_bucket,
            CopySource={'Bucket': source_bucket, 'Key': file_key},
            Key=file_key
        )
        logger.info(f"Copied {file_key} from {source_bucket} to {ephemeral_bucket}")
        
        # Start transcription job
        job_name = f"transcribe-{timestamp}-{str(uuid.uuid4())[:8]}"
        job_uri = f"s3://{source_bucket}/{file_key}"
        logger.info(f"Starting transcription job: {job_name}")
        logger.info(f"Media URI: {job_uri}")
        
        transcribe_client.start_transcription_job(
            TranscriptionJobName=job_name,
            Media={'MediaFileUri': job_uri},
            MediaFormat=file_key.split('.')[-1],
            LanguageCode='en-US',
            OutputBucketName=ephemeral_bucket,
            OutputKey=f"transcript-{file_key}.json"
        )
        
        # Wait for transcription job to complete
        logger.info("Waiting for transcription job to complete...")
        while True:
            status = transcribe_client.get_transcription_job(TranscriptionJobName=job_name)
            job_status = status['TranscriptionJob']['TranscriptionJobStatus']
            logger.info(f"Transcription job status: {job_status}")
            if job_status in ['COMPLETED', 'FAILED']:
                break
            time.sleep(5)
        
        if job_status == 'FAILED':
            logger.error(f"Transcription job {job_name} failed: {status}")
            raise Exception(f"Transcription job failed: {status}")
        
        logger.info(f"Transcription job {job_name} completed successfully")
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Transcription job completed',
                'ephemeral_bucket': ephemeral_bucket,
                'original_file': file_key,
                'transcript_file': f"transcript-{file_key}.json"
            })
        }

    except Exception as e:
        logger.error("Exception occurred", exc_info=True)
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e)
            })
        }
