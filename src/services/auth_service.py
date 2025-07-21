import boto3
import jwt
import os
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from botocore.exceptions import ClientError
from src.commonfunctions.dynamodb import find_by_id


class AuthService:
    def __init__(self):
        self.cognito_client = boto3.client('cognito-idp', region_name=os.environ.get('AWS_REGION', 'ap-south-1'))
        self.users_table = os.environ.get('USERS_TABLE', 'your-users-table-name')
        self.user_pool_id = os.environ.get('USER_POOL_ID')
        self.client_id = os.environ.get('COGNITO_CLIENT')
    
    def number_exists(self, number: str) -> list:
        """Check if phone number exists in users table"""
        from src.commonfunctions.dynamodb import query_by_index
        
        key_values = {':number': number}
        return query_by_index(
            self.users_table, 
            'numberIndex', 
            '#number = :number',
            key_values,
            expression_attribute_names={'#number': 'number'}
        )
    
    def validate_otp(self, number: str, code: str, session: str = None) -> Dict[str, Any]:
        # MOCKED for local testing, session is ignored
        if code == '123456':
            return {
                'statusCode': 200,
                'body': {
                    'message': 'Signed in successfully (mocked)',
                    'user': {'id': 'mock-user-id', 'number': number},
                    'tokens': {
                        'accessToken': 'mock-access-token',
                        'idToken': 'mock-id-token',
                        'refreshToken': 'mock-refresh-token'
                    }
                }
            }
        else:
            return {
                'statusCode': 400,
                'body': {
                    'message': 'Invalid OTP (mocked)',
                    'error': 'Incorrect OTP'
                }
            }
    
    def signin(self, number: str) -> Dict[str, Any]:
        # MOCKED for local testing
        return {
            'statusCode': 200,
            'body': {
                'message': 'OTP sent successfully (mocked)',
                'otp': '123456'  # Return a mock OTP for local testing
            }
        }
    
    def admin_create_rider(self, number: str, user_id: str, date: str) -> Dict[str, Any]:
        # MOCKED for local testing
        return {'message': 'Rider created (mocked)'}
    
    def refresh_tokens(self, refresh_token: str) -> Dict[str, Any]:
        # MOCKED for local testing
        return {
            'accessToken': 'mock-access-token',
            'idToken': 'mock-id-token',
            'expiresIn': 3600
        }
    
    def signout(self, access_token: str) -> None:
        # MOCKED for local testing
        return None
    
    @staticmethod
    def utc_date(date: datetime) -> str:
        """Convert datetime to UTC string format"""
        return date.replace(tzinfo=timezone.utc).isoformat()


# Global instance
auth_service = AuthService() 