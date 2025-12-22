import os

from stateless_microservice import ServiceConfig, create_app

from .processor import IfcbRoiProcessor

config = ServiceConfig(
    description="Service for accessing IFCB ROI images and associated technical metadata.",
)

# S3 Configuration
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")
S3_ENDPOINT_URL = os.getenv("S3_ENDPOINT_URL")  # Optional, for non-AWS S3
S3_ACCESS_KEY = os.getenv("S3_ACCESS_KEY")
S3_SECRET_KEY = os.getenv("S3_SECRET_KEY")
S3_PREFIX = os.getenv("S3_PREFIX", "")  # Optional prefix for all keys

# Validate required configuration
if not S3_BUCKET_NAME:
    raise ValueError("S3_BUCKET_NAME environment variable is required")
if not S3_ACCESS_KEY:
    raise ValueError("S3_ACCESS_KEY environment variable is required")
if not S3_SECRET_KEY:
    raise ValueError("S3_SECRET_KEY environment variable is required")

app = create_app(
    IfcbRoiProcessor(
        bucket_name=S3_BUCKET_NAME,
        endpoint_url=S3_ENDPOINT_URL,
        s3_access_key=S3_ACCESS_KEY,
        s3_secret_key=S3_SECRET_KEY,
        prefix=S3_PREFIX,
    ),
    config,
)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8001)
