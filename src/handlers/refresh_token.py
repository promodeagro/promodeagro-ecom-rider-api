from src.commonfunctions.utils import parse_json_body, response

def handler(event, context):
    body = parse_json_body(event)
    refresh_token = body.get('refreshToken')
    # Here you would implement your token refresh logic
    return response(200, {
        'accessToken': 'new-mock-access-token',
        'refreshToken': 'new-mock-refresh-token'
    }) 