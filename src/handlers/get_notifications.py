import json
from src.commonfunctions.utils import response

def handler(event, context):
    path_params = event.get('pathParameters', {}) or {}
    rider_id = path_params.get('id')
    # Here you would implement your notification retrieval logic
    notifications = [
        {
            'id': 'notif-1',
            'userId': rider_id,
            'title': 'Welcome',
            'message': 'Welcome to PromodeAgro!',
            'read': False,
            'createdAt': '2023-01-01T00:00:00Z',
            'type': 'info'
        }
    ]
    return response(200, notifications) 