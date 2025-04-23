import boto3
import os
import urllib.parse
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    # Define the S3 bucket and file name
    bucket_name = 'dunviidyquicktesttextbucket'
    file_key = 'email_HEYYEYAAEYAAAEYAEYAA.txt'
    from_email = "raslukw@dunwoody.edu"
    
    # Initialize AWS clients
    s3 = boto3.client('s3')
    ses = boto3.client('ses')
    
    try:
        # Retrieve the email address from S3
        response = s3.get_object(Bucket=bucket_name, Key=file_key)
        user_email = response['Body'].read().decode('utf-8').strip()
        
        logger.info(f"Retrieved email address: {user_email}")

        # Prepare email content
        subject = "Your Transcription File is Ready"
        body_text = (
            "Hello,\n\n"
            "Your transcription file is ready.\n\n"
            "This link is valid for 24 hours."
        )
        
        body_html = """
        <html>
        <head></head>
        <body>
          <p>Hello,</p>
          <p>Your transcription file is ready. You can download it using the link below:</p>
          <p><a href="">Download Transcription</a></p>
          <p><em>This link is valid for 24 hours.</em></p>
        </body>
        </html>
        """

        # Send email via SES
        email_response = ses.send_email(
            Source=from_email,
            Destination={'ToAddresses': [user_email]},
            Message={
                'Subject': {'Data': subject},
                'Body': {
                    'Text': {'Data': body_text},
                    'Html': {'Data': body_html}
                }
            }
        )

        logger.info(f"Email sent successfully: {email_response['MessageId']}")
        return {
            'statusCode': 200,
            'body': f"Email sent to {user_email}"
        }
    
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        return {
            'statusCode': 500,
            'body': f'Error processing request: {str(e)}'
        }
