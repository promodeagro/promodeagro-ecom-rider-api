import boto3
import os
from datetime import datetime
from typing import Dict, Any, Optional, List
from boto3.dynamodb.conditions import Key, Attr
from botocore.exceptions import ClientError


class DynamoDBClient:
    def __init__(self, region_name: str = None):
        # Get region from environment or use default
        self.region_name = region_name or os.environ.get('AWS_REGION', 'ap-south-1')
        print(f"Initializing DynamoDB client with region: {self.region_name}")
        
        # Initialize client and resource
        self.client = boto3.client('dynamodb', region_name=self.region_name)
        self.resource = boto3.resource('dynamodb', region_name=self.region_name)
        
        # Test connection
        try:
            self.client.list_tables()
            print(f"DynamoDB connection successful in region: {self.region_name}")
        except Exception as e:
            print(f"Warning: DynamoDB connection test failed: {str(e)}")
    
    def save(self, table_name: str, item: Dict[str, Any]) -> Dict[str, Any]:
        """Save an item to DynamoDB table"""
        timestamp = datetime.utcnow().isoformat() + 'Z'
        item = {**item, 'createdAt': timestamp, 'updatedAt': timestamp}
        
        print(f"SAVE OPERATION:")
        print(f"   Table: {table_name}")
        print(f"   Item: {item}")
        
        table = self.resource.Table(table_name)
        try:
            table.put_item(Item=item)
            print(f"   SAVE SUCCESSFUL")
            return item
        except ClientError as e:
            print(f"   CLIENT ERROR in save for table {table_name}: {str(e)}")
            print(f"   Error Code: {e.response['Error']['Code']}")
            print(f"   Error Message: {e.response['Error']['Message']}")
            raise
        except Exception as e:
            print(f"   UNEXPECTED ERROR in save for table {table_name}: {str(e)}")
            raise
    
    def find_by_id(self, table_name: str, item_id: str) -> Optional[Dict[str, Any]]:
        """Find an item by its ID"""
        table = self.resource.Table(table_name)
        print(f"FIND BY ID OPERATION:")
        print(f"   Table: {table_name}")
        print(f"   ID: {item_id}")
        
        try:
            response = table.get_item(Key={'id': item_id})
            item = response.get('Item')
            if item:
                print(f"   FIND SUCCESSFUL - Item found")
            else:
                print(f"   FIND SUCCESSFUL - No item found")
            return item
        except ClientError as e:
            print(f"   CLIENT ERROR in find_by_id for table {table_name}, id {item_id}: {str(e)}")
            print(f"   Error Code: {e.response['Error']['Code']}")
            print(f"   Error Message: {e.response['Error']['Message']}")
            return None
        except Exception as e:
            print(f"   UNEXPECTED ERROR in find_by_id for table {table_name}, id {item_id}: {str(e)}")
            return None
    
    def update(self, table_name: str, key: Dict[str, Any], update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update an item in DynamoDB table"""
        table = self.resource.Table(table_name)
        
        print(f"UPDATE OPERATION:")
        print(f"   Table: {table_name}")
        print(f"   Key: {key}")
        print(f"   Update Data: {update_data}")
        
        # Build update expression
        update_expression = []
        expression_attribute_names = {}
        expression_attribute_values = {}
        
        for i, (attr, value) in enumerate(update_data.items()):
            attr_name = f"#attr{i}"
            attr_value = f":val{i}"
            update_expression.append(f"{attr_name} = {attr_value}")
            expression_attribute_names[attr_name] = attr
            expression_attribute_values[attr_value] = value
        
        # Add updatedAt timestamp only if not already present
        if 'updatedAt' not in update_data:
            update_expression.append("#updatedAt = :updatedAt")
            expression_attribute_names["#updatedAt"] = "updatedAt"
            expression_attribute_values[":updatedAt"] = datetime.utcnow().isoformat() + 'Z'
        
        print(f"   Update Expression: SET {', '.join(update_expression)}")
        print(f"   Expression Names: {expression_attribute_names}")
        print(f"   Expression Values: {expression_attribute_values}")
        
        try:
            response = table.update_item(
                Key=key,
                UpdateExpression=f"SET {', '.join(update_expression)}",
                ExpressionAttributeNames=expression_attribute_names,
                ExpressionAttributeValues=expression_attribute_values,
                ReturnValues="ALL_NEW"
            )
            
            updated_item = response.get('Attributes')
            print(f"   UPDATE SUCCESSFUL")
            print(f"   Response: {updated_item}")
            return updated_item
            
        except ClientError as e:
            print(f"   CLIENT ERROR in update for table {table_name}, key {key}: {str(e)}")
            print(f"   Error Code: {e.response['Error']['Code']}")
            print(f"   Error Message: {e.response['Error']['Message']}")
            return None
        except Exception as e:
            print(f"   UNEXPECTED ERROR in update for table {table_name}, key {key}: {str(e)}")
            return None
    
    def query_by_index(self, table_name: str, index_name: str, key_condition: str, 
                      key_values: Dict[str, Any], filter_expression: Optional[str] = None,
                      filter_values: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Query items by GSI"""
        table = self.resource.Table(table_name)
        
        query_params = {
            'IndexName': index_name,
            'KeyConditionExpression': key_condition,
            'ExpressionAttributeValues': key_values
        }
        
        if filter_expression:
            query_params['FilterExpression'] = filter_expression
            if filter_values:
                query_params['ExpressionAttributeValues'].update(filter_values)
        
        try:
            response = table.query(**query_params)
            return response.get('Items', [])
        except ClientError:
            return []
    
    def batch_get(self, table_name: str, keys: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Batch get items from DynamoDB"""
        try:
            if not keys:
                return []
            
            response = self.client.batch_get_item(
                RequestItems={
                    table_name: {
                        'Keys': keys
                    }
                }
            )
            return response.get('Responses', {}).get(table_name, [])
        except ClientError as e:
            print(f"Error in batch_get for table {table_name}: {str(e)}")
            return []
        except Exception as e:
            print(f"Unexpected error in batch_get for table {table_name}: {str(e)}")
            return []


# Global instance
db_client = DynamoDBClient()

# Convenience functions
def save(table_name: str, item: Dict[str, Any]) -> Dict[str, Any]:
    return db_client.save(table_name, item)

def find_by_id(table_name: str, item_id: str) -> Optional[Dict[str, Any]]:
    return db_client.find_by_id(table_name, item_id)

def update(table_name: str, key: Dict[str, Any], update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    return db_client.update(table_name, key, update_data)

def query_by_index(table_name: str, index_name: str, key_condition: str, 
                  key_values: Dict[str, Any], filter_expression: Optional[str] = None,
                  filter_values: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    return db_client.query_by_index(table_name, index_name, key_condition, key_values, 
                                   filter_expression, filter_values)

def batch_get(table_name: str, keys: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return db_client.batch_get(table_name, keys) 