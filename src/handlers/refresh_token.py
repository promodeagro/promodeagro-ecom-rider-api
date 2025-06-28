from src.commonfunctions.dynamodb import parse_json_body, response
import random
import string

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
        
        # Generate new tokens
        new_access_token = generate_token()
        new_refresh_token = generate_token()
        
        return response(200, {
            'message': 'Token refreshed successfully',
            'success': True,
            'accessToken': new_access_token,
            'refreshToken': new_refresh_token,
            'rider': {
                'id': 'RIDER_9876543210',
                'phone_number': '9876543210',
                'name': '',
                'status': 'active',
                'profile_complete': False,
                'verification_status': 'pending'
            }
        })
        
    except Exception as e:
        return response(500, {
            'message': 'Internal server error',
            'success': False
        }) 