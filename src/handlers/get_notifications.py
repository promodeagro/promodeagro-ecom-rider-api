from src.commonfunctions.dynamodb import response, DynamoDBHelper

def handler(event, context):
    path_params = event.get('pathParameters', {}) or {}
    rider_id = path_params.get('id')
    
    if not rider_id:
        return response(400, {
            'message': 'Rider ID is required',
            'success': False
        })
    
    # Get notifications from DynamoDB
    notifications = DynamoDBHelper.get_notifications(rider_id)
    
    return response(200, {
        'success': True,
        'notifications': notifications,
        'count': len(notifications)
    }) 