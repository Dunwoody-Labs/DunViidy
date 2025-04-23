import boto3
import uuid
import os

def lambda_handler(event, context):
    region = os.environ.get("AWS_REGION", "us-east-1")
    base_name = os.environ.get("BASE_EPHEMERAL_BUCKET", "dunviidy-transcription")
    bucket_name = f"{base_name}-{uuid.uuid4().hex}"

    s3 = boto3.client("s3")

    # Create the ephemeral bucket
    s3.create_bucket(
        Bucket=bucket_name,
        CreateBucketConfiguration={"LocationConstraint": region}
    )

    # Add lifecycle policy (deletes after 3 days)
    s3.put_bucket_lifecycle_configuration(
        Bucket=bucket_name,
        LifecycleConfiguration={
            "Rules": [{
                "ID": "delete_after_3_days",
                "Status": "Enabled",
                "Filter": {"Prefix": ""},
                "Expiration": {"Days": 3}
            }]
        }
    )

    # Return the bucket name to be used in the transcription task
    return {
        "ephemeral_bucket_name": bucket_name
    }
