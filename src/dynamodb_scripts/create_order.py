# src/dynamodb_scripts/create_order.py
import boto3
from botocore.exceptions import ClientError
from decimal import Decimal

def create_orders_table(dynamodb_resource):
    """
    Creates the 'Orders' table in DynamoDB.
    Returns True if the table is created or already exists, False otherwise.
    """
    try:
        print("-> Attempting to create 'Orders' table...")
        table = dynamodb_resource.create_table(
            TableName='Orders',
            KeySchema=[{'AttributeName': 'id', 'KeyType': 'HASH'}],
            AttributeDefinitions=[{'AttributeName': 'id', 'AttributeType': 'S'}],
            ProvisionedThroughput={'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5}
        )
        print("   - Waiting for 'Orders' table to become active...")
        table.wait_until_exists()
        print("   - 'Orders' table is active.")
        return True
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceInUseException':
            print("   - 'Orders' table already exists.")
            return True
        else:
            print(f"   - Error creating table: {e}")
            return False

def insert_order_data(dynamodb_resource):
    """
    Inserts a sample order item into the 'Orders' table.
    Returns True on success, False on failure.
    """
    try:
        print("-> Preparing and inserting sample order data...")
        table = dynamodb_resource.Table('Orders')
        # The provided order data, with numeric values converted to Decimal
        order_item = {
            "id": "401-3760341",
            "address": {
                "address": "Guhcci", "addressId": "9399820d-1d7a-4043-8acb-155083aafb54",
                "address_type": "Home", "house_number": "Bdjje", "landmark_area": "abcd",
                "name": "Fatima ", "phoneNumber": "1234512345",
                "userId": "0d87e7d1-c878-45be-946d-120fa2af70c6", "zipCode": "500091"
            },
            "createdAt": "2025-05-12T19:43:47.724Z", "customerId": "0d87e7d1-c878-45be-946d-120fa2af70c6",
            "customerName": "Fatima ", "customerNameLower": "fatima ", "customerNumber": "1234512345",
            "deliveryCharges": Decimal('0'),
            "deliverySlot": {
                "id": "c7e8d862", "date": "2025-05-13", "endAmPm": "PM", "endTime": "1:00",
                "shift": "morning", "startAmPm": "AM", "startTime": "10:00"
            },
            "finalTotal": Decimal('120'),
            "items": [
                {
                    "category": "Bengali Special", "mrp": Decimal('60'), "price": Decimal('50'),
                    "productId": "3639101568", "productImage": "https://prod-promodeargo-admin-api-mediabucket46c59097-tynsj9joexji.s3.us-east-1.amazonaws.com/%CD%88%5B%24u0%EF%BF%BD%EF%BF%BD%03%1A%3C%EF%BF%BDx%60%60%EF%BF%BDlebu.webp",
                    "productName": "Gondhoraj Lemon (Nimbu)", "quantity": Decimal('1'), "quantityUnits": Decimal('3'),
                    "savings": Decimal('10'), "subCategory": "Bengali Vegetables", "subtotal": Decimal('50'), "unit": "pieces"
                },
                {
                    "category": "Bengali Special", "mrp": Decimal('95'), "price": Decimal('70'),
                    "productId": "9381385120", "productImage": "https://prod-promodeargo-admin-api-mediabucket46c59097-tynsj9joexji.s3.us-east-1.amazonaws.com/%EF%BF%BD%EF%BF%BD%25%EF%BF%BDs%C5%8En-%EF%BF%BDbn%3F%21%7B%EF%BF%BD30000434_13-fresho-brinjal-purple-bharta.webp",
                    "productName": "Bharta Brinjal (Black medium pieces)", "quantity": Decimal('1'), "quantityUnits": Decimal('1'),
                    "savings": Decimal('25'), "subCategory": "Bengali Vegetables", "subtotal": Decimal('70'), "unit": "kg"
                }
            ],
            "paymentDetails": {"method": "COD", "status": "PENDING"},
            "status": "delivered", "subTotal": Decimal('120'), "tax": Decimal('0'),
            "totalPrice": "120.00", "totalSavings": "35.00",
            "updatedAt": "2025-05-12T19:43:47.724Z", "userId": "0d87e7d1-c878-45be-946d-120fa2af70c6",
        }
        table.put_item(Item=order_item)
        print("   - Sample order data inserted successfully.")
        return True
    except Exception as e:
        print(f"   - Error inserting data: {e}")
        return False

def main():
    """
    Main function to run the setup process for the Orders table.
    """
    print("--- Starting Order Table Setup ---")
    dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')
    
    # Step 1: Create the table.
    if create_orders_table(dynamodb):
        # Step 2: If table creation is successful, insert the data.
        if insert_order_data(dynamodb):
            print("--- Order Table Setup Completed Successfully! ---")
        else:
            print("--- Setup failed during data insertion. ---")
    else:
        print("--- Setup failed during table creation. ---")

if __name__ == '__main__':
    main() 