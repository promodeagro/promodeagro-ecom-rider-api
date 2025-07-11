from src.commonfunctions.dynamodb import parse_json_body, response, DynamoDBHelper
import random
import string
import logging
logging.basicConfig(level=logging.INFO)

def generate_token():
    """Generate a random token"""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=32))

def handler(event, context):
    try:
        body = parse_json_body(event)
        refresh_token = body.get('refreshToken')
        
        if not refresh_token:
            return response(400, {
                'message': 'Refresh token is required',
                'success': False
            })
        
        # Validate refresh token using DynamoDB
        item, message = DynamoDBHelper.validate_token(refresh_token)
        if not item:
            return response(400, {
                'message': message,
                'success': False
            })
        
        # Generate new tokens
        new_access_token = generate_token()
        new_refresh_token = generate_token()

        # Store the new refresh token and delete the old one
        DynamoDBHelper.store_token(new_refresh_token, item['rider_id'], item['phone_number'])
        DynamoDBHelper.delete_token(refresh_token)
        
        return response(200, {
            'message': 'Token refreshed successfully',
            'success': True,
            'accessToken': new_access_token,
            'refreshToken': new_refresh_token,
            'rider': {
                'id': item['rider_id'],
                'phone_number': item['phone_number'],
                'name': item.get('name', ''),
                'status': item.get('status', 'active'),
                'profile_complete': item.get('profile_complete', False),
                'verification_status': item.get('verification_status', 'pending')
            }
        })
        
    except Exception as e:
        return response(500, {
            'message': 'Internal server error',
            'success': False
        }) 