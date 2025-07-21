import json
import os
from typing import Dict, Any
import boto3
from src.commonfunctions.response import api_response

# DynamoDB resource for ap-south-1 region
dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')
RIDER_TABLE = os.environ.get('RIDER_TABLE', 'Rider')

# Handler to create a new rider
def create_rider_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    try:
        body = json.loads(event.get('body', '{}'))
        table = dynamodb.Table(RIDER_TABLE)
        table.put_item(Item=body)
        return api_response(201, {'message': 'Rider created', 'rider': body})
    except Exception as e:
        return api_response(400, {'message': 'Failed to create rider', 'error': str(e)})

# Handler to get a rider by id
def get_rider_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    try:
        rider_id = event.get('pathParameters', {}).get('id')
        if not rider_id:
            return api_response(400, {'message': 'Rider id is required'})
        table = dynamodb.Table(RIDER_TABLE)
        response = table.get_item(Key={'riderId': rider_id})
        item = response.get('Item')
        if not item:
            return api_response(404, {'message': 'Rider not found'})
        return api_response(200, item)
    except Exception as e:
        return api_response(400, {'message': 'Failed to get rider', 'error': str(e)})

# Handler to list all riders
def list_riders_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    try:
        table = dynamodb.Table(RIDER_TABLE)
        response = table.scan()
        items = response.get('Items', [])
        return api_response(200, items)
    except Exception as e:
        return api_response(400, {'message': 'Failed to list riders', 'error': str(e)}) 