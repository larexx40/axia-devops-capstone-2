import os
import json
import boto3
from dotenv import load_dotenv

# Load .env file if it exists (local development only)
# In production on EC2, .env does not exist — this line does nothing
load_dotenv()


def get_secret_from_aws(secret_name, region_name="us-east-1"):
    """
    Fetch secrets from AWS Secrets Manager.
    Only called when APP_ENV=production.
    """
    try:
        client = boto3.client(
            "secretsmanager",
            region_name=region_name
        )
        response = client.get_secret_value(SecretId=secret_name)
        return json.loads(response["SecretString"])
    except Exception as e:
        print(f"Warning: Could not fetch AWS secrets: {e}")
        return {}


def load_config():
    """
    Config loading strategy:
    - Local:      reads from .env file via python-dotenv
    - Production: reads from AWS Secrets Manager
    """
    environment = os.environ.get("APP_ENV", "development")

    if environment == "production":
        aws_secrets = get_secret_from_aws("capstone2/app/config")
    else:
        aws_secrets = {}

    return {
        "DB_HOST": aws_secrets.get(
            "DB_HOST", os.environ.get("DB_HOST", "localhost")
        ),
        "DB_USER": aws_secrets.get(
            "DB_USER", os.environ.get("DB_USER", "dev_user")
        ),
        "DB_PASSWORD": aws_secrets.get(
            "DB_PASSWORD", os.environ.get("DB_PASSWORD", "")
        ),
        "DB_NAME": aws_secrets.get(
            "DB_NAME", os.environ.get("DB_NAME", "internal_db")
        ),
        "ENVIRONMENT": environment,
        "SECRET_KEY": aws_secrets.get(
            "SECRET_KEY", os.environ.get(
                "SECRET_KEY", "dev-secret-key-change-in-prod"
            )
        ),
    }


_config = load_config()

DB_HOST = _config["DB_HOST"]
DB_USER = _config["DB_USER"]
DB_PASSWORD = _config["DB_PASSWORD"]
DB_NAME = _config["DB_NAME"]
ENVIRONMENT = _config["ENVIRONMENT"]
SECRET_KEY = _config["SECRET_KEY"]
