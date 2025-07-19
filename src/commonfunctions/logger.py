import functools
import json


def api_logger(handler):
    """A decorator to log API Gateway events and responses."""
    @functools.wraps(handler)
    def wrapper(event, context):
        print(f"--- Request for {handler.__name__} ---")
        print("Event:")
        # Pretty print JSON if possible
        try:
            # The event body is a JSON string.
            body = json.loads(event.get('body', '{}'))
            print(json.dumps(body, indent=2))
        except (json.JSONDecodeError, TypeError):
            # Fallback to printing the raw event if body is not a JSON string or not present
            print(event)

        # Call the actual handler
        response = handler(event, context)

        print(f"--- Response from {handler.__name__} ---")
        print("Response:")
        # Assuming the response is a dict that can be serialized to JSON.
        print(json.dumps(response, indent=2))
        
        return response

    return wrapper 