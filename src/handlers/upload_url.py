from src.commonfunctions.dynamodb import response

def handler(event, context):
    params = event.get('queryStringParameters', {}) or {}
    file_name = params.get('fileName')
    # Here you would implement your upload URL generation logic
    return response(200, {
        'uploadUrl': 'https://mock-s3-url.com/upload',
        'fileKey': file_name or 'mock-file-key',
        'expiresIn': 3600
    }) 