# src/dynamodb_scripts/create_inventory.py
import boto3
from botocore.exceptions import ClientError
from decimal import Decimal

def create_inventory_table(dynamodb_resource):
    """
    Creates the 'Inventory' table in DynamoDB.
    Returns True if the table is created or already exists, False otherwise.
    """
    try:
        print("-> Attempting to create 'Inventory' table...")
        table = dynamodb_resource.create_table(
            TableName='Inventory',
            KeySchema=[{'AttributeName': 'id', 'KeyType': 'HASH'}],
            AttributeDefinitions=[{'AttributeName': 'id', 'AttributeType': 'S'}],
            ProvisionedThroughput={'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5}
        )
        print("   - Waiting for 'Inventory' table to become active...")
        table.wait_until_exists()
        print("   - 'Inventory' table is active.")
        return True
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceInUseException':
            print("   - 'Inventory' table already exists.")
            return True
        else:
            print(f"   - Error creating table: {e}")
            return False

def insert_inventory_data(dynamodb_resource):
    """
    Inserts a sample inventory item into the 'Inventory' table.
    Returns True on success, False on failure.
    """
    try:
        print("-> Preparing and inserting sample inventory data...")
        table = dynamodb_resource.Table('Inventory')
        # The provided inventory data, with numeric values converted to Decimal
        inventory_item = {
            "id": "74E5F8DD",
            "compareAt": Decimal('105'),
            "createdAt": "2024-11-25T06:29:52.997Z",
            "msp": Decimal('100'),
            "onlineStorePrice": Decimal('100'),
            "productId": "74e5f8dd-9837-4359-ba08-d3c384c96adf",
            "purchasingPrice": Decimal('60'),
            "stockQuantity": Decimal('25'),
            "unitPrices": [
                {
                    "discountedPrice": Decimal('5'),
                    "price": Decimal('100'),
                    "qty": Decimal('1'),
                    "savings": Decimal('5'),
                    "varient_id": "0eba58e6-69c9-4d9f-b699-6f9e9d70f7f8"
                }
            ],
            "updatedAt": "2024-11-25T06:29:52.997Z"
        }
        table.put_item(Item=inventory_item)
        print("   - Sample inventory data inserted successfully.")
        return True
    except Exception as e:
        print(f"   - Error inserting data: {e}")
        return False

def main():
    """
    Main function to run the setup process for the Inventory table.
    """
    print("--- Starting Inventory Table Setup ---")
    dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')
    
    # Step 1: Create the table.
    if create_inventory_table(dynamodb):
        # Step 2: If table creation is successful, insert the data.
        if insert_inventory_data(dynamodb):
            print("--- Inventory Table Setup Completed Successfully! ---")
        else:
            print("--- Setup failed during data insertion. ---")
    else:
        print("--- Setup failed during table creation. ---")

if __name__ == '__main__':
    main() 