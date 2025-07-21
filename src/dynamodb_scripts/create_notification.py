# src/dynamodb_scripts/create_notification.py
import boto3
from botocore.exceptions import ClientError
from decimal import Decimal
import datetime

def create_notifications_table(dynamodb_resource):
    """
    Creates the 'Notifications' table in DynamoDB.
    Returns True if the table is created or already exists, False otherwise.
    """
    try:
        print("-> Attempting to create 'Notifications' table...")
        table = dynamodb_resource.create_table(
            TableName='Notifications',
            KeySchema=[{'AttributeName': 'notificationId', 'KeyType': 'HASH'}],
            AttributeDefinitions=[{'AttributeName': 'notificationId', 'AttributeType': 'S'}],
            ProvisionedThroughput={'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5}
        )
        print("   - Waiting for 'Notifications' table to become active...")
        table.wait_until_exists()
        print("   - 'Notifications' table is active.")
        return True
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceInUseException':
            print("   - 'Notifications' table already exists.")
            return True
        else:
            print(f"   - Error creating table: {e}")
            return False

def insert_notification_data(dynamodb_resource):
    """
    Inserts a sample notification item into the 'Notifications' table.
    Returns True on success, False on failure.
    """
    try:
        print("-> Preparing and inserting sample notification data...")
        table = dynamodb_resource.Table('Notifications')
        # Sample notification data
        notification_item = {
            'notificationId': 'notif-alert-001',
            'userId': '0d87e7d1-c878-45be-946d-120fa2af70c6', # Example user ID
            'title': 'Your Order is on its way!',
            'message': 'Your order 401-3760341 has been dispatched.',
            'read': False,
            'createdAt': datetime.datetime.utcnow().isoformat()
        }
        table.put_item(Item=notification_item)
        print("   - Sample notification data inserted successfully.")
        return True
    except Exception as e:
        print(f"   - Error inserting data: {e}")
        return False

def main():
    """
    Main function to run the setup process for the Notifications table.
    """
    print("--- Starting Notifications Table Setup ---")
    dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')
    
    # Step 1: Create the table.
    if create_notifications_table(dynamodb):
        # Step 2: If table creation is successful, insert the data.
        if insert_notification_data(dynamodb):
            print("--- Notifications Table Setup Completed Successfully! ---")
        else:
            print("--- Setup failed during data insertion. ---")
    else:
        print("--- Setup failed during table creation. ---")

if __name__ == '__main__':
    main() 