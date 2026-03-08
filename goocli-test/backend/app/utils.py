import os
import boto3
from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import JWTError, jwt
from botocore.exceptions import NoCredentialsError

# Security Constants
SECRET_KEY = os.getenv("SECRET_KEY", "super-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# S3 Configuration
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
AWS_BUCKET_NAME = os.getenv("AWS_BUCKET_NAME", "menopause-app-storage")
s3_client = boto3.client('s3', region_name=AWS_REGION)

def verify_password(plain_password, hashed_password):
    """
    Given a password and the hashed password in DB, return True if valid, False else
    """
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    """
    Given a normal password, return the hash version of that password
    """
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    """
    Given the data to create token, and a optional expire time return a unique access token (proverbial cookie)
    """
    to_encode = data.copy()
    # If there are expire time data, we use it, in other case we use a default of 15 minutes
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def upload_to_s3(file_obj, filename, folder="uploads"):
    """
    Given name of file_obj, filename and the folder the archive will be
    return an URL using that info in s3 aws format
    If something went wrong, return None
    """
    object_name = f"{folder}/{filename}"
    try:
        # Try upload the object 
        s3_client.upload_fileobj(
            file_obj, 
            AWS_BUCKET_NAME, 
            object_name, 
            ExtraArgs={'ACL': 'public-read'}
        )
        # If no errors, just return url
        url = f"https://{AWS_BUCKET_NAME}.s3.{AWS_REGION}.amazonaws.com/{object_name}"
        return url
    except NoCredentialsError:
        return None
    except Exception as e:
        print(f"Error uploading to S3: {e}")
        return None
