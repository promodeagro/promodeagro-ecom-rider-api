# src/dynamodb_scripts/create_runsheet.py
import boto3
from botocore.exceptions import ClientError
from decimal import Decimal

def create_runsheets_table(dynamodb_resource):
    """
    Creates the 'Runsheets' table in DynamoDB.
    Returns True if the table is created or already exists, False otherwise.
    """
    try:
        print("-> Attempting to create 'Runsheets' table...")
        table = dynamodb_resource.create_table(
            TableName='Runsheets',
            KeySchema=[{'AttributeName': 'id', 'KeyType': 'HASH'}],
            AttributeDefinitions=[{'AttributeName': 'id', 'AttributeType': 'S'}],
            ProvisionedThroughput={'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5}
        )
        print("   - Waiting for 'Runsheets' table to become active...")
        table.wait_until_exists()
        print("   - 'Runsheets' table is active.")
        return True
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceInUseException':
            print("   - 'Runsheets' table already exists.")
            return True
        else:
            print(f"   - Error creating table: {e}")
            return False

def insert_runsheet_data(dynamodb_resource):
    """
    Inserts a sample runsheet item into the 'Runsheets' table.
    Returns True on success, False on failure.
    """
    try:
        print("-> Preparing and inserting sample runsheet data...")
        table = dynamodb_resource.Table('Runsheets')
        # The provided runsheet data, with numeric values converted to Decimal
        runsheet_item = {
            "id": "c30962fde2cf",
            "acceptedAt": "2025-06-27T13:05:03.769349Z",
            "amountCollectable": Decimal('0'),
            "amountCollected": Decimal('6274'),
            "createdAt": "2024-11-20T10:52:35.846Z",
            "orders": ["401-6020697-8045324"],
            "riderId": "ad6f18b8-b40d-4fe4-921a-655a5c64661f",
            "status": "active",
            "updatedAt": "2025-06-27T13:05:03.775870Z"
        }
        table.put_item(Item=runsheet_item)
        print("   - Sample runsheet data inserted successfully.")
        return True
    except Exception as e:
        print(f"   - Error inserting data: {e}")
        return False

def main():
    """
    Main function to run the setup process for the Runsheets table.
    """
    print("--- Starting Runsheet Table Setup ---")
    dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')
    
    # Step 1: Create the table.
    if create_runsheets_table(dynamodb):
        # Step 2: If table creation is successful, insert the data.
        if insert_runsheet_data(dynamodb):
            print("--- Runsheet Table Setup Completed Successfully! ---")
        else:
            print("--- Setup failed during data insertion. ---")
    else:
        print("--- Setup failed during table creation. ---")

if __name__ == '__main__':
    main() 