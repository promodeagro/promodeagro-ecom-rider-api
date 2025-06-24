import json
import os
from typing import Dict, Any
import boto3
from datetime import datetime
from botocore.exceptions import ClientError

from src.commonfunctions.logger import api_logger
from src.commonfunctions.response import api_response


@api_logger
def list_notifications_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    try:
        notifications_table = os.environ.get('NOTIFICATIONS_TABLE')
        user_id = event.get('pathParameters', {}).get('id')
        
        print(f"NOTIFICATION QUERY:")
        print(f"   Table: {notifications_table}")
        print(f"   User ID: {user_id}")
        
        if not user_id:
            return api_response(400, {'message': 'id is required'})
        
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table(notifications_table)
        
        from boto3.dynamodb.conditions import Key, Attr
        now = int(datetime.utcnow().timestamp())
        
        print(f"   Current timestamp: {now}")
        print(f"   Querying for unread notifications...")
        
        response = table.query(
            IndexName='userIndex',
            KeyConditionExpression=Key('userId').eq(user_id),
            FilterExpression='#readStatus = :unread AND (attribute_not_exists(#ttlField) OR #ttlField > :now)',
            ExpressionAttributeNames={'#readStatus': 'read', '#ttlField': 'ttl'},
            ExpressionAttributeValues={':unread': False, ':now': now},
            ScanIndexForward=False
        )
        
        items = response.get('Items', [])
        count = response.get('Count', 0)
        scanned_count = response.get('ScannedCount', 0)
        
        print(f"   Query Results:")
        print(f"     Items found: {len(items)}")
        print(f"     Count: {count}")
        print(f"     Scanned Count: {scanned_count}")
        
        if items:
            print(f"     Sample item: {items[0]}")
        else:
            print(f"     No items found")
            
        return api_response(200, items)
        
    except ClientError as e:
        print(f"   DYNAMODB ERROR: {str(e)}")
        print(f"   Error Code: {e.response['Error']['Code']}")
        print(f"   Error Message: {e.response['Error']['Message']}")
        return api_response(500, {
            'message': 'Failed to fetch notifications',
            'error': str(e)
        })
    except Exception as e:
        print(f"   UNEXPECTED ERROR: {str(e)}")
        return api_response(500, {
            'message': 'Failed to fetch notifications',
            'error': str(e)
        })


@api_logger
def update_notification_read_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Update notification read status"""
    try:
        notifications_table = os.environ.get('NOTIFICATIONS_TABLE')
        user_id = event.get('pathParameters', {}).get('id')
        
        print(f"UPDATE NOTIFICATION READ STATUS:")
        print(f"   Table: {notifications_table}")
        print(f"   User ID: {user_id}")
        
        if not user_id:
            return api_response(400, {'message': 'User ID is required'})
        
        # Parse request body
        body = json.loads(event.get('body', '{}'))
        notification_id = body.get('notificationId')
        read_status = body.get('read', True)  # Default to True
        
        print(f"   Notification ID: {notification_id}")
        print(f"   Read Status: {read_status}")
        
        if not notification_id:
            return api_response(400, {'message': 'notificationId is required in request body'})
        
        # Validate read status is boolean
        if not isinstance(read_status, bool):
            return api_response(400, {'message': 'read must be a boolean value (true/false)'})
        
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table(notifications_table)
        
        # First, check if the notification exists and belongs to the user
        try:
            response = table.get_item(Key={'id': notification_id})
            notification = response.get('Item')
            
            if not notification:
                return api_response(404, {'message': 'Notification not found'})
            
            if notification.get('userId') != user_id:
                return api_response(403, {'message': 'Access denied - notification does not belong to this user'})
            
            print(f"   Found notification: {notification.get('title')}")
            print(f"   Current read status: {notification.get('read')}")
            
        except ClientError as e:
            print(f"   ERROR fetching notification: {str(e)}")
            return api_response(500, {
                'message': 'Failed to fetch notification',
                'error': str(e)
            })
        
        # Update the notification read status
        try:
            update_response = table.update_item(
                Key={'id': notification_id},
                UpdateExpression='SET #readStatus = :readStatus, #updatedAt = :updatedAt',
                ExpressionAttributeNames={
                    '#readStatus': 'read',
                    '#updatedAt': 'updatedAt'
                },
                ExpressionAttributeValues={
                    ':readStatus': read_status,
                    ':updatedAt': datetime.utcnow().isoformat() + 'Z'
                },
                ReturnValues='ALL_NEW'
            )
            
            updated_notification = update_response.get('Attributes')
            print(f"   UPDATE SUCCESSFUL")
            print(f"   New read status: {updated_notification.get('read')}")
            
            return api_response(200, {
                'message': 'Notification read status updated successfully',
                'notification': {
                    'id': updated_notification.get('id'),
                    'title': updated_notification.get('title'),
                    'message': updated_notification.get('message'),
                    'read': updated_notification.get('read'),
                    'updatedAt': updated_notification.get('updatedAt')
                }
            })
            
        except ClientError as e:
            print(f"   ERROR updating notification: {str(e)}")
            print(f"   Error Code: {e.response['Error']['Code']}")
            print(f"   Error Message: {e.response['Error']['Message']}")
            return api_response(500, {
                'message': 'Failed to update notification read status',
                'error': str(e)
            })
        
    except json.JSONDecodeError as e:
        print(f"   JSON PARSE ERROR: {str(e)}")
        return api_response(400, {
            'message': 'Invalid JSON in request body',
            'error': str(e)
        })
    except Exception as e:
        print(f"   UNEXPECTED ERROR: {str(e)}")
        return api_response(500, {
            'message': 'Failed to update notification read status',
            'error': str(e)
        }) 