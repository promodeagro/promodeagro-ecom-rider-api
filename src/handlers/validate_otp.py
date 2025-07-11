from src.commonfunctions.dynamodb import parse_json_body, response
import re
import random
import string
from src.commonfunctions.dynamodb import DynamoDBHelper

def validate_phone_number(phone_number):
    """Validate phone number format"""
    cleaned_number = re.sub(r'\D', '', phone_number)
    if len(cleaned_number) == 10 and cleaned_number[0] in '6789':
        return cleaned_number
    elif len(cleaned_number) == 12 and cleaned_number.startswith('91') and cleaned_number[2] in '6789':
        return cleaned_number[2:]
    else:
        return None

def generate_token():
    """Generate a random token"""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=32))

def handler(event, context):
    try:
        body = parse_json_body(event)
        number = body.get('number')
        otp = body.get('otp')
        
        if not number or not otp:
            return response(400, {
                'message': 'Phone number and OTP are required',
                'success': False
            })
        
        # Validate phone number
        validated_number = validate_phone_number(number)
        if not validated_number:
            return response(400, {
                'message': 'Invalid phone number format',
                'success': False
            })
        
        # Validate OTP format
        if not otp.isdigit() or len(otp) != 6:
            return response(400, {
                'message': 'Invalid OTP format. Please enter a 6-digit code.',
                'success': False
            })
        
        # Validate OTP using DynamoDB
        is_valid, message = DynamoDBHelper.validate_otp(validated_number, otp)
        if not is_valid:
            return response(400, {
                'message': message,
                'success': False
            })
        
        # Delete OTP after successful validation
        DynamoDBHelper.delete_otp(validated_number)
        
        # Generate tokens
        refresh_token = generate_token()
        DynamoDBHelper.store_token(refresh_token, f'RIDER_{validated_number}', validated_number)
        
        return response(200, {
            'message': 'OTP validated successfully',
            'success': True,
            'refreshToken': refresh_token,
            'rider': {
                'id': f'RIDER_{validated_number}',
                'phone_number': validated_number,
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