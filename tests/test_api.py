import pytest
from unittest.mock import patch, MagicMock
from src.handlers.auth.auth import signin_handler, validate_otp_handler, refresh_token_handler, signout_handler
from src.handlers.rider.rider import create_rider_handler, update_personal_details_handler, update_bank_details_handler, update_document_details_handler
from src.handlers.runsheet.runsheet import list_runsheets_handler, get_runsheet_handler, accept_runsheet_handler, confirm_order_handler, cancel_order_handler
from src.handlers.notification.notification import list_notifications_handler
from src.handlers.media.media import get_presigned_upload_url_handler, delete_image_handler


RIDER_ID = "3e47e035-d3b4-4733-a911-9c138fc1c4e2"
RUNSHEET_ID = "f0db5b63f418"
ORDER_ID = "401-6992561"

def test_signin_handler():
    event = {'body': '{"number": "9876543210"}'}
    with patch('src.services.auth_service.auth_service.signin', return_value={'statusCode': 200, 'body': {'message': 'OTP sent', 'session': 'abc'}}):
        response = signin_handler(event, None)
        assert response['statusCode'] == 200
        assert 'OTP sent' in response['body']

def test_validate_otp_handler():
    event = {'body': '{"number": "9876543210", "code": "123456", "session": "abc"}'}
    with patch('src.services.auth_service.auth_service.validate_otp', return_value={'statusCode': 200, 'body': {'message': 'OTP validated'}}):
        response = validate_otp_handler(event, None)
        assert response['statusCode'] == 200
        assert 'OTP validated' in response['body']

def test_refresh_token_handler():
    event = {'body': '{"refreshToken": "refreshtoken"}'}
    with patch('src.services.auth_service.auth_service.refresh_tokens', return_value={'statusCode': 200, 'body': {'accessToken': 'newtoken'}}):
        response = refresh_token_handler(event, None)
        assert response['statusCode'] == 200
        assert 'accessToken' in response['body']

def test_signout_handler():
    event = {'body': '{"accessToken": "sometoken"}'}
    with patch('src.services.auth_service.auth_service.signout', return_value=None):
        response = signout_handler(event, None)
        assert response['statusCode'] == 200
        assert 'Successfully signed out' in response['body']

def test_create_rider_handler():
    event = {'body': '{"personalDetails": {"fullName": "Test User", "dob": "2000-01-01", "email": "test@example.com", "number": "9876543210", "address": {"address1": "A", "state": "B", "city": "C", "pincode": "12345", "address2": "", "landmark": ""}, "reference": {"relation": "Friend", "number": "9876543211"}}, "bankDetails": {"bankName": "Bank", "acc": "123", "ifsc": "IFSC0000001"}, "documents": [{"name": "userPhoto", "image": "http://example.com/img.jpg"}]}' }
    with patch('src.handlers.rider.rider.save', return_value=None), \
         patch('src.handlers.rider.rider.find_by_id', return_value={'id': 'test-id'}), \
         patch('src.services.auth_service.auth_service.admin_create_rider', return_value=None):
        response = create_rider_handler(event, None)
        assert response['statusCode'] in (200, 201)

def test_update_personal_details_handler():
    event = {'body': f'{{"id": "{RIDER_ID}", "personalDetails": {{"fullName": "Test User", "dob": "2000-01-01", "email": "test@example.com", "number": "9876543210", "address": {{"address1": "A", "state": "B", "city": "C", "pincode": "12345"}}, "reference": {{"relation": "Friend", "number": "9876543211"}}}}}}'}
    with patch('src.handlers.rider.rider.find_by_id', return_value={'id': RIDER_ID}), \
         patch('src.handlers.rider.rider.update', return_value={'id': RIDER_ID}):
        response = update_personal_details_handler(event, None)
        assert response['statusCode'] == 200

def test_update_bank_details_handler():
    event = {'body': f'{{"id": "{RIDER_ID}", "bankDetails": {{"bankName": "Bank", "acc": "123", "ifsc": "IFSC0000001"}}}}'}
    with patch('src.handlers.rider.rider.find_by_id', return_value={'id': RIDER_ID}), \
         patch('src.handlers.rider.rider.update', return_value={'id': RIDER_ID}):
        response = update_bank_details_handler(event, None)
        assert response['statusCode'] == 200

def test_update_document_details_handler():
    event = {'body': f'{{"id": "{RIDER_ID}", "document": {{"name": "userPhoto", "image": "http://example.com/new.jpg"}}}}'}
    with patch('src.handlers.rider.rider.find_by_id', return_value={'id': RIDER_ID, 'documents': []}), \
         patch('src.handlers.rider.rider.update', return_value={'id': RIDER_ID}):
        response = update_document_details_handler(event, None)
        assert response['statusCode'] == 200

def test_list_runsheets_handler():
    event = {'pathParameters': {'id': RIDER_ID}}
    with patch('boto3.resource') as mock_resource:
        mock_table = MagicMock()
        mock_table.query.return_value = {'Items': []}
        mock_resource.return_value.Table.return_value = mock_table
        response = list_runsheets_handler(event, None)
        assert response['statusCode'] == 200

def test_get_runsheet_handler():
    event = {'pathParameters': {'runsheetId': RUNSHEET_ID}}
    with patch('src.handlers.runsheet.runsheet.find_by_id', return_value={'id': RUNSHEET_ID, 'orders': []}), \
         patch('src.handlers.runsheet.runsheet.batch_get', return_value=[]):
        response = get_runsheet_handler(event, None)
        assert response['statusCode'] == 200

def test_accept_runsheet_handler():
    event = {'pathParameters': {'runsheetId': RUNSHEET_ID}}
    with patch('src.handlers.runsheet.runsheet.update', return_value={'id': RUNSHEET_ID, 'status': 'active'}):
        response = accept_runsheet_handler(event, None)
        assert response['statusCode'] == 200
        assert 'active' in response['body']

def test_confirm_order_handler():
    event = {'pathParameters': {'runsheetId': RUNSHEET_ID, 'orderId': ORDER_ID}, 'body': '{"image": "some_image_url.jpg", "via": "cash"}'}
    with patch('src.handlers.runsheet.runsheet.find_by_id') as mock_find_by_id:
        mock_find_by_id.side_effect = [
            {'id': RUNSHEET_ID, 'orders': [ORDER_ID]},
            {'id': ORDER_ID, 'paymentDetails': {'method': 'cash'}}
        ]
        with patch('src.handlers.runsheet.runsheet.update', return_value={'id': ORDER_ID, 'status': 'delivered'}):
            response = confirm_order_handler(event, None)
            assert response['statusCode'] == 200

def test_cancel_order_handler():
    event = {'pathParameters': {'runsheetId': RUNSHEET_ID, 'orderId': ORDER_ID}, 'body': '{"reason": "rejected by customer"}'}
    with patch('src.handlers.runsheet.runsheet.find_by_id') as mock_find_by_id:
        mock_find_by_id.side_effect = [
            {'id': RUNSHEET_ID, 'orders': [ORDER_ID]},
            {'id': ORDER_ID, 'status': 'pending'}
        ]
        with patch('src.handlers.runsheet.runsheet.update', return_value={'id': ORDER_ID, 'status': 'cancelled'}):
            response = cancel_order_handler(event, None)
            assert response['statusCode'] == 200

def test_list_notifications_handler():
    event = {'pathParameters': {'id': RIDER_ID}}
    with patch('boto3.resource') as mock_resource:
        mock_table = MagicMock()
        mock_table.query.return_value = {'Items': []}
        mock_resource.return_value.Table.return_value = mock_table
        response = list_notifications_handler(event, None)
        assert response['statusCode'] == 200

def test_get_presigned_upload_url_handler():
    event = {'queryStringParameters': {'fileName': 'test.jpg'}}
    with patch('boto3.client') as mock_client:
        mock_s3 = MagicMock()
        mock_s3.generate_presigned_url.return_value = 'http://example.com/upload'
        mock_client.return_value = mock_s3
        response = get_presigned_upload_url_handler(event, None)
        assert response['statusCode'] == 200
        assert 'uploadUrl' in response['body']

def test_delete_image_handler():
    event = {'queryStringParameters': {'imageName': 'test.jpg'}}
    with patch('boto3.client') as mock_client:
        mock_s3 = MagicMock()
        mock_s3.delete_object.return_value = {}
        mock_client.return_value = mock_s3
        response = delete_image_handler(event, None)
        assert response['statusCode'] == 200
        assert 'image deleted successfully' in response['body'] 