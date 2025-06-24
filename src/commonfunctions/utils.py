import json
import logging


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