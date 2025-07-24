import boto3
from botocore.exceptions import NoCredentialsError, ClientError

# Replace with your bucket name
BUCKET_NAME = 'sachchida'

# Optional: specify region if required
s3 = boto3.client('s3')  # Or boto3.resource('s3')

try:
    response = s3.list_objects_v2(Bucket=BUCKET_NAME)
    if 'Contents' in response:
        print(f"✅ Found {len(response['Contents'])} files in bucket '{BUCKET_NAME}':")
        for obj in response['Contents']:
            print(" -", obj['Key'])
    else:
        print(f"✅ Bucket '{BUCKET_NAME}' is empty.")
except NoCredentialsError:
    print("AWS credentials not found. Set them using environment variables or AWS CLI.")
except ClientError as e:
    print(f"Error accessing S3: {e}")
