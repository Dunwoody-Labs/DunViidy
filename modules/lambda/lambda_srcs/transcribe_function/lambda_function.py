import boto3
import os
import uuid
import json
from datetime import datetime

def lambda_handler(event, context):
    try:
        # Retrieve S3 event details
        s3_bucket = event['Records'][0]['s3']['bucket']['name']
        s3_key = event['Records'][0]['s3']['object']['key']
        print(f"Processing file: {s3_key} from bucket: {s3_bucket}")

        # Extract the original file name without extension
        original_filename = os.path.splitext(os.path.basename(s3_key))[0]

        # Generate unique job name
        job_name = f"{original_filename}-{uuid.uuid4()}"

        # Create an Amazon Transcribe client
        transcribe_client = boto3.client('transcribe')

        # Set S3 URI for input file
        s3_uri = f"s3://{s3_bucket}/{s3_key}"

        # Get output bucket from environment
        output_bucket_name = os.environ.get("OUTPUT_BUCKET")

        print(f"Starting Transcription Job: {job_name}")
        print(f"Input S3 URI: {s3_uri}")
        print(f"Output S3 Bucket: {output_bucket_name}")

        # Start transcription job
        response = transcribe_client.start_transcription_job(
            TranscriptionJobName=job_name,
            LanguageCode="en-US",
            Media={"MediaFileUri": s3_uri},
            OutputBucketName=output_bucket_name,
            Subtitles={"Formats": ["vtt"]}
        )

        print(f"Transcription job started successfully.")

        def json_serial(obj):
            """Convert non-serializable types (datetime) to strings"""
            if isinstance(obj, datetime):
                return obj.isoformat()
            raise TypeError(f"Type {type(obj)} not serializable")

        return {
            "statusCode": 200,
            "body": json.dumps(response, default=json_serial)
        }

    except Exception as e:
        print(f"Error starting transcription job: {str(e)}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }