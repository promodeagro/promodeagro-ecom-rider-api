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
    
    def validate_otp(self, number: str, code: str, session: str) -> Dict[str, Any]:
        """Validate OTP and return user data with tokens"""
        try:
            response = self.cognito_client.respond_to_auth_challenge(
                ClientId=self.client_id,
                ChallengeName='CUSTOM_CHALLENGE',
                Session=session,
                ChallengeResponses={
                    'USERNAME': f'+91{number}',
                    'ANSWER': code
                }
            )
            
            if 'AuthenticationResult' not in response:
                return {
                    'statusCode': 400,
                    'body': {
                        'message': 'Invalid OTP, please try again',
                        'session': response.get('Session')
                    }
                }
            
            # Decode ID token to get user ID
            id_token_decoded = jwt.decode(
                response['AuthenticationResult']['IdToken'], 
                options={"verify_signature": False}
            )
            user_id = id_token_decoded.get('custom:userId')
            user = find_by_id(self.users_table, user_id)
            
            return {
                'statusCode': 200,
                'body': {
                    'message': 'Signed in successfully',
                    'user': user,
                    'tokens': {
                        'accessToken': response['AuthenticationResult']['AccessToken'],
                        'idToken': response['AuthenticationResult']['IdToken'],
                        'refreshToken': response['AuthenticationResult']['RefreshToken']
                    }
                }
            }
            
        except ClientError as e:
            return {
                'statusCode': 400,
                'body': {
                    'message': 'Invalid OTP, please try again',
                    'error': str(e)
                }
            }
    
    def signin(self, number: str) -> Dict[str, Any]:
        """Initiate signin process and send OTP"""
        try:
            response = self.cognito_client.admin_initiate_auth(
                AuthFlow='CUSTOM_AUTH',
                UserPoolId=self.user_pool_id,
                ClientId=self.client_id,
                AuthParameters={
                    'USERNAME': f'+91{number}'
                }
            )
            
            return {
                'statusCode': 200,
                'body': {
                    'message': 'OTP sent successfully',
                    'session': response['Session']
                }
            }
            
        except ClientError as e:
            return {
                'statusCode': 400,
                'body': {
                    'message': 'Failed to send OTP',
                    'error': str(e)
                }
            }
    
    def admin_create_rider(self, number: str, user_id: str, date: str) -> Dict[str, Any]:
        """Create a new rider user in Cognito"""
        try:
            response = self.cognito_client.admin_create_user(
                UserPoolId=self.user_pool_id,
                Username=f'+91{number}',
                UserAttributes=[
                    {'Name': 'phone_number', 'Value': f'+91{number}'},
                    {'Name': 'custom:userId', 'Value': user_id},
                    {'Name': 'custom:role', 'Value': 'rider'},
                    {'Name': 'custom:createdAt', 'Value': date},
                    {'Name': 'phone_number_verified', 'Value': 'true'}
                ],
                MessageAction='SUPPRESS'
            )
            return response
        except ClientError as e:
            raise Exception(f"Failed to create rider: {str(e)}")
    
    def refresh_tokens(self, refresh_token: str) -> Dict[str, Any]:
        """Refresh access token using refresh token"""
        try:
            response = self.cognito_client.admin_initiate_auth(
                AuthFlow='REFRESH_TOKEN_AUTH',
                UserPoolId=self.user_pool_id,
                ClientId=self.client_id,
                AuthParameters={
                    'REFRESH_TOKEN': refresh_token
                }
            )
            
            return {
                'accessToken': response['AuthenticationResult']['AccessToken'],
                'idToken': response['AuthenticationResult']['IdToken'],
                'expiresIn': response['AuthenticationResult']['ExpiresIn']
            }
            
        except ClientError as e:
            raise Exception(f"Failed to refresh tokens: {str(e)}")
    
    def signout(self, access_token: str) -> None:
        """Sign out user by invalidating access token"""
        try:
            self.cognito_client.global_sign_out(
                AccessToken=access_token
            )
        except ClientError as e:
            raise Exception(f"Failed to sign out: {str(e)}")
    
    @staticmethod
    def utc_date(date: datetime) -> str:
        """Convert datetime to UTC string format"""
        return date.replace(tzinfo=timezone.utc).isoformat()


# Global instance
auth_service = AuthService() 