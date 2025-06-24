from src.commonfunctions.utils import parse_json_body, response

def handler(event, context):
    body = parse_json_body(event)
    number = body.get('number')
    # Here you would implement your sign-in logic
    return response(200, {
        'message': 'OTP sent successfully',
        'success': True
    }) 