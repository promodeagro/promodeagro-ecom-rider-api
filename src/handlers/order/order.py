import json
import os
from typing import Dict, Any
import boto3
from src.commonfunctions.response import api_response

# DynamoDB resource for ap-south-1 region
dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')
ORDERS_TABLE = os.environ.get('ORDERS_TABLE', 'Orders')

# Handler to create a new order
def create_order_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    try:
        body = json.loads(event.get('body', '{}'))
        # You may want to validate body here
        table = dynamodb.Table(ORDERS_TABLE)
        table.put_item(Item=body)
        return api_response(201, {'message': 'Order created', 'order': body})
    except Exception as e:
        return api_response(400, {'message': 'Failed to create order', 'error': str(e)})

# Handler to get an order by id
def get_order_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    try:
        order_id = event.get('pathParameters', {}).get('id')
        if not order_id:
            return api_response(400, {'message': 'Order id is required'})
        table = dynamodb.Table(ORDERS_TABLE)
        response = table.get_item(Key={'id': order_id})
        item = response.get('Item')
        if not item:
            return api_response(404, {'message': 'Order not found'})
        return api_response(200, item)
    except Exception as e:
        return api_response(400, {'message': 'Failed to get order', 'error': str(e)})

# Handler to list all orders
def list_orders_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    try:
        table = dynamodb.Table(ORDERS_TABLE)
        response = table.scan()
        items = response.get('Items', [])
        return api_response(200, items)
    except Exception as e:
        return api_response(400, {'message': 'Failed to list orders', 'error': str(e)}) 