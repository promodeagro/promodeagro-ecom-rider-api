import json
import os
import boto3
import secrets
from typing import Dict, Any
from datetime import datetime, timedelta

from src.commonfunctions.logger import api_logger
from src.commonfunctions.response import api_response


@api_logger
def get_presigned_upload_url_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    bucket_name = os.environ.get('MEDIA_BUCKET')
    params = event.get('queryStringParameters', {}) or {}
    image_name = params.get('fileName')
    if not image_name:
        return api_response(400, {'message': 'image name is required'})
    random_bytes = secrets.token_hex(8)
    key = f"productsImages/{random_bytes}{image_name.replace(' ', '')}"
    s3 = boto3.client('s3')
    try:
        url = s3.generate_presigned_url(
            'put_object',
            Params={'Bucket': bucket_name, 'Key': key},
            ExpiresIn=1800
        )
        return api_response(200, {'uploadUrl': url})
    except Exception as e:
        return api_response(500, {'message': 'Failed to generate upload URL', 'error': str(e)})


@api_logger
def delete_image_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    bucket_name = os.environ.get('MEDIA_BUCKET')
    params = event.get('queryStringParameters', {}) or {}
    image_key = params.get('imageName')
    if not image_key:
        return api_response(400, {'message': 'image key is required'})
    s3 = boto3.client('s3')
    try:
        s3.delete_object(Bucket=bucket_name, Key=image_key)
        return api_response(200, {'message': 'image deleted successfully'})
    except Exception as e:
        return api_response(500, {'message': 'Failed to delete image', 'error': str(e)})