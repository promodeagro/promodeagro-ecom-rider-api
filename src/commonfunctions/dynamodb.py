import boto3
import os
import json
import logging
from datetime import datetime, timedelta
from botocore.exceptions import ClientError

# Initialize DynamoDB client
dynamodb = boto3.resource('dynamodb')
rider_table = dynamodb.Table(os.environ.get('RIDER_TABLE', 'prod-promodeagro-rider'))
notification_table = dynamodb.Table(os.environ.get('NOTIFICATION_TABLE', 'rider-NotificationTable'))

def parse_json_body(event):
    """Safely parse the JSON body from an API Gateway event."""
    try:
        return json.loads(event.get('body', '{}'))
    except Exception as e:
        logging.error(f"Failed to parse JSON body: {e}")
        return {}

def response(status_code, body):
    """Format a standard API Gateway response."""
    return {
        'statusCode': status_code,
        'body': json.dumps(body)
    }

class DynamoDBHelper:
    """Helper class for DynamoDB operations"""
    
    @staticmethod
    def store_otp(phone_number, otp, expires_in_minutes=10):
        """Store OTP in DynamoDB with expiration"""
        try:
            expiry_time = datetime.utcnow() + timedelta(minutes=expires_in_minutes)
            
            item = {
                'id': f"OTP_{phone_number}",
                'phone_number': phone_number,
                'otp': otp,
                'expires_at': expiry_time.isoformat(),
                'created_at': datetime.utcnow().isoformat(),
                'attempts': 0,
                'max_attempts': 3,
                'type': 'OTP'
            }
            
            rider_table.put_item(Item=item)
            return True
        except Exception as e:
            logging.error(f"Failed to store OTP: {e}")
            return False
    
    @staticmethod
    def validate_otp(phone_number, otp):
        """Validate OTP from DynamoDB"""
        try:
            response = rider_table.get_item(
                Key={'id': f"OTP_{phone_number}"}
            )
            
            if 'Item' not in response:
                return False, "OTP not found or expired"
            
            item = response['Item']
            
            # Check if OTP is expired
            expires_at = datetime.fromisoformat(item['expires_at'])
            if datetime.utcnow() > expires_at:
                return False, "OTP has expired"
            
            # Check if max attempts exceeded
            if item['attempts'] >= item['max_attempts']:
                return False, "Maximum OTP attempts exceeded"
            
            # Validate OTP
            if item['otp'] != otp:
                # Increment attempts
                rider_table.update_item(
                    Key={'id': f"OTP_{phone_number}"},
                    UpdateExpression='SET attempts = attempts + :inc',
                    ExpressionAttributeValues={':inc': 1}
                )
                return False, "Invalid OTP"
            
            return True, "OTP validated successfully"
            
        except Exception as e:
            logging.error(f"Failed to validate OTP: {e}")
            return False, "Database error"
    
    @staticmethod
    def delete_otp(phone_number):
        """Delete OTP from DynamoDB"""
        try:
            rider_table.delete_item(Key={'id': f"OTP_{phone_number}"})
            return True
        except Exception as e:
            logging.error(f"Failed to delete OTP: {e}")
            return False
    
    @staticmethod
    def store_token(refresh_token, rider_id, phone_number, expires_in_seconds=300):
        """Store refresh token in DynamoDB with 5 minutes expiration"""
        try:
            expiry_time = datetime.utcnow() + timedelta(seconds=expires_in_seconds)
            item = {
                'id': f"TOKEN_{refresh_token}",
                'rider_id': rider_id,
                'phone_number': phone_number,
                'refresh_token': refresh_token,
                'created_at': datetime.utcnow().isoformat(),
                'expires_at': expiry_time.isoformat(),
                'type': 'TOKEN'
            }
            rider_table.put_item(Item=item)
            return True
        except Exception as e:
            logging.error(f"Failed to store token: {e}")
            return False
    
    @staticmethod
    def validate_token(refresh_token):
        """Validate refresh token from DynamoDB"""
        try:
            response = rider_table.get_item(
                Key={'id': f"TOKEN_{refresh_token}"}
            )
            
            if 'Item' not in response:
                return None, "Invalid refresh token"
            
            item = response['Item']
            
            # Check if token is expired
            expires_at = datetime.fromisoformat(item['expires_at'])
            if datetime.utcnow() > expires_at:
                return None, "Refresh token has expired"
            
            return item, "Token valid"
            
        except Exception as e:
            logging.error(f"Failed to validate token: {e}")
            return None, "Database error"
    
    @staticmethod
    def delete_token(refresh_token):
        """Delete refresh token from DynamoDB"""
        try:
            rider_table.delete_item(Key={'id': f"TOKEN_{refresh_token}"})
            return True
        except Exception as e:
            logging.error(f"Failed to delete token: {e}")
            return False
    
    @staticmethod
    def create_or_update_rider(phone_number, name=None, status='active'):
        """Create new rider or update existing one"""
        try:
            rider_id = f"RIDER_{phone_number}"
            
            # Check if rider exists
            existing_response = rider_table.get_item(Key={'id': rider_id})
            
            if 'Item' in existing_response:
                # Update existing rider
                update_expression = 'SET last_login = :login, status = :status'
                expression_values = {
                    ':login': datetime.utcnow().isoformat(),
                    ':status': status
                }
                
                if name:
                    update_expression += ', #name = :name'
                    expression_values[':name'] = name
                    expression_values['#name'] = 'name'
                
                rider_table.update_item(
                    Key={'id': rider_id},
                    UpdateExpression=update_expression,
                    ExpressionAttributeValues=expression_values
                )
                
                return existing_response['Item']
            else:
                # Create new rider
                rider_data = {
                    'id': rider_id,
                    'phone_number': phone_number,
                    'name': name or '',
                    'status': status,
                    'created_at': datetime.utcnow().isoformat(),
                    'last_login': datetime.utcnow().isoformat(),
                    'profile_complete': False,
                    'verification_status': 'pending',
                    'type': 'RIDER'
                }
                
                rider_table.put_item(Item=rider_data)
                return rider_data
                
        except Exception as e:
            logging.error(f"Failed to create/update rider: {e}")
            return None
    
    @staticmethod
    def get_rider(rider_id):
        """Get rider by ID"""
        try:
            response = rider_table.get_item(Key={'id': rider_id})
            return response.get('Item')
        except Exception as e:
            logging.error(f"Failed to get rider: {e}")
            return None
    
    @staticmethod
    def get_notifications(rider_id, limit=10):
        """Get notifications for a rider"""
        try:
            response = notification_table.query(
                KeyConditionExpression='UserId = :user_id',
                ExpressionAttributeValues={':user_id': rider_id},
                Limit=limit,
                ScanIndexForward=False  # Get latest first
            )
            return response.get('Items', [])
        except Exception as e:
            logging.error(f"Failed to get notifications: {e}")
            return []

    @staticmethod
    def create_notification(rider_id, title, message, notification_type='info'):
        """Create a new notification"""
        try:
            notification_id = f"NOTIF_{rider_id}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
            now = datetime.utcnow().isoformat()
            item = {
                'UserId': rider_id,
                'createdAt': now,
                'id': notification_id,
                'title': title,
                'message': message,
                'type': notification_type,
                'read': False,
                'created_at': now
            }
            notification_table.put_item(Item=item)
            return item
        except Exception as e:
            logging.error(f"Failed to create notification: {e}")
            return None 