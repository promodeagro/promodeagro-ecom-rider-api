import json
import os
from typing import Dict, Any
from src.commonfunctions.logger import api_logger
from src.services.auth_service import auth_service
from src.commonfunctions.models import (
    PhoneNumberRequest, OTPValidationRequest, RefreshTokenRequest, 
    SignoutRequest
)
from src.commonfunctions.response import api_response


@api_logger
def signin_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Handle rider signin - send OTP"""
    try:
        body = json.loads(event.get('body', '{}'))
        number = body.get("number")
        if not number:
            return api_response(400, {
                'message': 'Missing number in request',
                'error': 'Number is required.'
            })
        # For local testing, skip 10-digit check
        result = auth_service.signin(number)
        # Log the number and OTP sent
        otp = result['body'].get('otp')
        print(f"[SIGNIN] Received number: {number}, Sent OTP: {otp}")
        return api_response(
            result['statusCode'],
            result['body']
        )
    except Exception as e:
        return api_response(400, {
            'message': 'Invalid request',
            'error': str(e)
        })


@api_logger
def validate_otp_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Handle OTP validation"""
    try:
        # Parse request body
        body = json.loads(event.get('body', '{}'))
        number = body.get('number')
        code = body.get('code')
        if not number or not code:
            return api_response(400, {
                'message': 'Missing number or code in request',
                'error': 'Both number and code are required.'
            })
        # Call auth service (session is ignored in local/mock mode)
        result = auth_service.validate_otp(number, code)
        return api_response(
            result['statusCode'],
            result['body']
        )
    except Exception as e:
        return api_response(400, {
            'message': 'Invalid request',
            'error': str(e)
        })


@api_logger
def refresh_token_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Handle token refresh"""
    try:
        # Parse request body
        body = json.loads(event.get('body', '{}'))
        request = RefreshTokenRequest(**body)
        
        # Call auth service
        result = auth_service.refresh_tokens(request.refreshToken)
        
        return api_response(200, result)
        
    except Exception as e:
        return api_response(400, {
            'message': 'Failed to refresh token',
            'error': str(e)
        })


@api_logger
def signout_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Handle user signout"""
    try:
        # Parse request body
        body = json.loads(event.get('body', '{}'))
        request = SignoutRequest(**body)
        
        # Call auth service
        auth_service.signout(request.accessToken)
        
        return api_response(200, {
            'message': 'Successfully signed out'
        })
        
    except Exception as e:
        return api_response(400, {
            'message': 'Failed to sign out',
            'error': str(e)
        }) 