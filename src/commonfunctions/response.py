import json
from decimal import Decimal
from typing import Dict, Any

class DecimalEncoder(json.JSONEncoder):
    """Custom JSON encoder to handle DynamoDB Decimal types"""
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super(DecimalEncoder, self).default(obj)

# Utility to convert floats that are whole numbers to ints

def convert_floats_to_ints(obj):
    if isinstance(obj, Decimal):
        if obj % 1 == 0:
            return int(obj)
        else:
            return float(obj)
    elif isinstance(obj, float) and obj.is_integer():
        return int(obj)
    elif isinstance(obj, list):
        return [convert_floats_to_ints(i) for i in obj]
    elif isinstance(obj, dict):
        return {k: convert_floats_to_ints(v) for k, v in obj.items()}
    else:
        return obj

def api_response(status_code: int, body: Any, headers: Dict[str, str] = None) -> Dict[str, Any]:
    """Create API Gateway compatible response"""
    # Ensure all floats that are whole numbers are converted to ints
    body = convert_floats_to_ints(body)
    response = {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type,Authorization',
            'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS'
        },
        'body': json.dumps(body, cls=DecimalEncoder)
    }
    if headers:
        response['headers'].update(headers)
    return response 