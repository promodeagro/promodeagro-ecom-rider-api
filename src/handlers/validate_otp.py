from src.commonfunctions.utils import parse_json_body, response

def handler(event, context):
    body = parse_json_body(event)
    number = body.get('number')
    otp = body.get('otp')
    # Here you would implement your OTP validation logic
    return response(200, {
        'message': 'OTP validated successfully',
        'accessToken': 'mock-access-token',
        'refreshToken': 'mock-refresh-token',
        'rider': {
            'id': 'mock-id',
            'number': number,
            'status': 'active'
        }
    }) 