"""AWS接続情報の設定用モジュール"""

import os

from boto3.session import Session
from botocore.config import Config

config = Config(
    connect_timeout=int(os.environ['AWS_CONNECT_TIMEOUT']),
    read_timeout=int(os.environ['AWS_READ_TIMEOUT']),
    retries={
        'max_attempts': int(os.environ['AWS_MAX_ATTEMPTS'])
    }
)

# ローカル用
if os.getenv('MY_AWS_ACCESS_KEY_ID') and os.getenv('MY_AWS_SECRET_ACCESS_KEY'):
    session = Session(
        aws_access_key_id=os.environ['MY_AWS_ACCESS_KEY_ID'],
        aws_secret_access_key=os.environ['MY_AWS_SECRET_ACCESS_KEY'],
        region_name=os.environ['AWS_REGION_NAME'],
    )
# AWS Lambda用
else:
    session = Session(
        region_name=os.environ['AWS_REGION_NAME']
    )
