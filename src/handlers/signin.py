from src.commonfunctions.dynamodb import parse_json_body, response
import re
import random
import string
import logging

def validate_phone_number(phone_number):
    """Validate phone number format"""
    # Remove any non-digit characters
    cleaned_number = re.sub(r'\D', '', phone_number)
    
    # Check if it's a valid Indian mobile number (10 digits starting with 6-9)
    if len(cleaned_number) == 10 and cleaned_number[0] in '6789':
        return cleaned_number
    elif len(cleaned_number) == 12 and cleaned_number.startswith('91') and cleaned_number[2] in '6789':
        return cleaned_number[2:]  # Remove country code
    else:
        return None

def generate_otp():
    """Generate a 6-digit OTP"""
    return ''.join(random.choices(string.digits, k=6))

def handler(event, context):
    try:
        body = parse_json_body(event)
        phone_number = body.get('number')
        
        # Input validation
        if not phone_number:
            return response(400, {
                'message': 'Phone number is required',
                'success': False,
                'error_code': 'MISSING_PHONE_NUMBER'
            })
        
        # Validate phone number format
        validated_number = validate_phone_number(phone_number)
        if not validated_number:
            return response(400, {
                'message': 'Invalid phone number format. Please provide a valid 10-digit Indian mobile number.',
                'success': False,
                'error_code': 'INVALID_PHONE_NUMBER'
            })
        
        # Generate OTP
        otp = generate_otp()
        
        # Log OTP for development (remove in production)
        logging.info(f"Generated OTP {otp} for phone number {validated_number}")
        
        return response(200, {
            'message': 'OTP sent successfully',
            'success': True,
            'phone_number': validated_number,
            'otp': otp,  # Remove this in production - only for development
            'otp_expires_in': '10 minutes'
        })
        
    except Exception as e:
        logging.error(f"Signin error: {e}")
        return response(500, {
            'message': 'Internal server error. Please try again.',
            'success': False,
            'error_code': 'INTERNAL_ERROR'
        }) 