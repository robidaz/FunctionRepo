from requests.api import get
import boto3
import botocore
import os
from os.path import *
import base64
import json
def get_aws_credentials():
    ec2name = get(
        "http://169.254.169.254/latest/meta-data/iam/security-credentials").text
    r = get(
        f"http://169.254.169.254/latest/meta-data/iam/security-credentials/{ec2name}")
    return (r.json())


def write_file_to_s3(bucketname, key, file, region):
    keys = get_aws_credentials()
    ACCESS_KEY = keys["AccessKeyId"]
    SECRET_KEY = keys["SecretAccessKey"]
    SESSION_TOKEN = keys["Token"]
    s3 = boto3.resource(
        "s3",
        aws_access_key_id=ACCESS_KEY,
        aws_secret_access_key=SECRET_KEY,
        aws_session_token=SESSION_TOKEN,
        region_name=region)
    s3.meta.client.upload_file(file, bucketname, key)


def write_folder_to_s3(bucketname, keyprefix, folder, region):
    keys = get_aws_credentials()
    ACCESS_KEY = keys["AccessKeyId"]
    SECRET_KEY = keys["SecretAccessKey"]
    SESSION_TOKEN = keys["Token"]
    s3 = boto3.resource(
        "s3",
        aws_access_key_id=ACCESS_KEY,
        aws_secret_access_key=SECRET_KEY,
        aws_session_token=SESSION_TOKEN,
        region_name=region)
    for root, _dirs, files in os.walk(folder):
        for file in files:
            filepath = join(root, file)
            key = join(keyprefix, (relpath(filepath, os.path.dirname(folder))))
            s3.meta.client.upload_file(file, bucketname, key)


def get_secret(secret_name, region_name, decode_json=True):
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name)
    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name)
        if 'SecretString' in get_secret_value_response:
            secret = get_secret_value_response['SecretString']
        else:
            secret = base64.b64decode(
                get_secret_value_response['SecretBinary'])
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == 'DecryptionFailureException':
            raise Exception(
                f"Secrets Manager can't decrypt the protected secret text using the provided KMS key. {e}")
        elif e.response['Error']['Code'] == 'InternalServiceErrorException':
            raise Exception(f"An error occurred on the server side. {e}")
        elif e.response['Error']['Code'] == 'InvalidParameterException':
            raise Exception(
                f"You provided an invalid value for a parameter. {e}")
        elif e.response['Error']['Code'] == 'InvalidRequestException':
            raise Exception(
                f"You provided a parameter value that is not valid for the current state of the resource. {e}")
            raise e
        elif e.response['Error']['Code'] == 'ResourceNotFoundException':
            raise Exception(
                f"We can't find the resource that you asked for. {e}")
    if decode_json is True:
        return json.loads(secret.replace("'", '"'))
    return secret