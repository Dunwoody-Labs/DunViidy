import boto3
import os
import time
import re
from urllib.parse import unquote_plus

s3 = boto3.client('s3')
transcribe = boto3.client('transcribe')
ses = boto3.client('ses', region_name='us-east-2')

SENDER_EMAIL = 'helmasw@dunwoody.edu'  # Update with your SES-verified email

output_bucket = os.environ['OUTPUT_BUCKET']

def lambda_handler(event, context):
    print("Event:", event)

    input_bucket = event['Records'][0]['s3']['bucket']['name']
    video_key = unquote_plus(event['Records'][0]['s3']['object']['key'])

    if not video_key.lower().endswith('.mp4'):
        print("Not an .mp4 file. Skipping.")
        return

    base_name = os.path.splitext(os.path.basename(video_key))[0]
    txt_key = f"{base_name}.txt"

    # Get email address from the .txt file
    try:
        txt_obj = s3.get_object(Bucket=input_bucket, Key=txt_key)
        email_address = txt_obj['Body'].read().decode('utf-8').strip()
    except Exception as e:
        print(f"Error fetching {txt_key}: {e}")
        return

    print("Email extracted:", email_address)

    # Copy the video to the output bucket
    copy_source = {'Bucket': input_bucket, 'Key': video_key}
    s3.copy_object(CopySource=copy_source, Bucket=output_bucket, Key=video_key)
    print(f"Copied video to {output_bucket}")

    # Sanitize the transcription job name
    transcribe_job_name = f"job-{int(time.time())}-{base_name}"
    transcribe_job_name = re.sub(r'[^a-zA-Z0-9._-]', '_', transcribe_job_name)
    print(f"Sanitized Transcribe job name: {transcribe_job_name}")

    # Start Transcribe job
    media_uri = f"s3://{output_bucket}/{video_key}"

    transcribe.start_transcription_job(
        TranscriptionJobName=transcribe_job_name,
        Media={'MediaFileUri': media_uri},
        MediaFormat='mp4',
        LanguageCode='en-US',
        OutputBucketName=output_bucket,
        Subtitles={
            'Formats': ['vtt'],
            'OutputStartIndex': 1
        }
    )

    print(f"Started Transcribe job: {transcribe_job_name}")

    # Wait for transcription job to complete
    while True:
        status = transcribe.get_transcription_job(TranscriptionJobName=transcribe_job_name)
        job_status = status['TranscriptionJob']['TranscriptionJobStatus']
        if job_status in ['COMPLETED', 'FAILED']:
            break
        print("Waiting for Transcribe job to complete...")
        time.sleep(10)

    if job_status == 'FAILED':
        print("Transcription failed.")
        return

    print("Transcription completed.")

    # Rename the .vtt file from job name to base name
    original_vtt_key = f"{transcribe_job_name}.vtt"
    new_vtt_key = f"{base_name}.vtt"

    try:
        s3.copy_object(
            Bucket=output_bucket,
            CopySource={'Bucket': output_bucket, 'Key': original_vtt_key},
            Key=new_vtt_key
        )
        s3.delete_object(Bucket=output_bucket, Key=original_vtt_key)
        print(f"Renamed {original_vtt_key} to {new_vtt_key}")
    except Exception as e:
        print(f"Error renaming .vtt file: {e}")
        return

    # Generate presigned URLs
    video_url = s3.generate_presigned_url(
        'get_object',
        Params={'Bucket': output_bucket, 'Key': video_key},
        ExpiresIn=172800
    )

    vtt_url = s3.generate_presigned_url(
        'get_object',
        Params={'Bucket': output_bucket, 'Key': new_vtt_key},
        ExpiresIn=172800
    )

    # Prepare email
    subject = "Dunviidy Video and Transcription"

    text_body = f"""
Hello,

Your video and transcription are ready.

Please right click and save the video in the link below:

Download video: {video_url}
Download subtitles (.vtt): {vtt_url}

These links will expire in 2 days.

Regards,
Dunviidy Automated Transcription System
"""

    html_body = f"""
<html>
  <body>
    <p>Hello,</p>
    <p>Your video and transcription are ready.</p>
    <p>Please right click and save the video in the link below:</p>
    <p>
      <a href="{video_url}">Download Video</a><br>
      <a href="{vtt_url}">Download Subtitles (.vtt)</a>
    </p>
    <p>These links will expire in 2 days.</p>
    <p>Regards,<br>Dunviidy Automated Transcription System</p>
  </body>
</html>
"""

    # Send SES email
    try:
        ses.send_email(
            Source=SENDER_EMAIL,
            Destination={'ToAddresses': [email_address]},
            Message={
                'Subject': {'Data': subject},
                'Body': {
                    'Text': {'Data': text_body},
                    'Html': {'Data': html_body}
                }
            }
        )
        print(f"Email sent to {email_address}")
    except Exception as e:
        print(f"Error sending email: {e}")
