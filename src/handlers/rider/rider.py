import json
import uuid
import os
from datetime import datetime
from typing import Dict, Any
from src.commonfunctions.logger import api_logger
from src.services.auth_service import auth_service
from src.commonfunctions.dynamodb import save, find_by_id, update
from src.commonfunctions.models import RiderRegistration, RiderUpdateRequest
from src.commonfunctions.response import api_response


def clean_name(name: str) -> str:
    """Clean and format rider name"""
    return ' '.join(word.capitalize() for word in name.strip().lower().split())


def s_name(name: str) -> str:
    """Create search-friendly name"""
    return name.strip().lower().replace(' ', '')


@api_logger
def create_rider_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Handle rider registration"""
    try:
        # Parse request body
        body = json.loads(event.get('body', '{}'))
        request = RiderRegistration(**body)
        
        # Generate rider ID
        rider_id = str(uuid.uuid4())
        
        # Create rider object
        rider = {
            'id': rider_id,
            'number': request.personalDetails.number,
            'profileStatus': {},
            'name': clean_name(request.personalDetails.fullName),
            's_name': s_name(request.personalDetails.fullName),
            'personalDetails': request.personalDetails.dict(),
            'bankDetails': request.bankDetails.dict(),
            'documents': [
                {
                    'name': doc.name,
                    'image': doc.image,
                    'verified': 'pending',
                    'rejectionReason': None
                }
                for doc in request.documents
            ],
            'reviewStatus': 'pending',
            'submittedAt': datetime.utcnow().isoformat() + 'Z',
            'updatedAt': datetime.utcnow().isoformat() + 'Z',
            'accountVerified': False,
            'role': 'rider'
        }
        
        # Create user in Cognito
        # date = datetime.utcnow()
        # utc_date = auth_service.utc_date(date)
        # auth_service.admin_create_rider(request.personalDetails.number, rider_id, utc_date)
        
        # Save to DynamoDB
        users_table = os.environ.get('USERS_TABLE', 'your-users-table-name')
        save(users_table, rider)
        
        # Return created rider
        created_rider = find_by_id(users_table, rider_id)
        
        return api_response(201, created_rider)
        
    except Exception as e:
        return api_response(400, {
            'message': 'Failed to create rider',
            'error': str(e)
        })


@api_logger
def update_personal_details_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Handle personal details update"""
    try:
        # Parse request body
        body = json.loads(event.get('body', '{}'))
        request = RiderUpdateRequest(**body)
        
        if not request.personalDetails:
            return api_response(400, {
                'message': 'Personal details are required'
            })
        
        # Get current rider
        users_table = os.environ.get('USERS_TABLE', 'promodeagroUsers')
        rider = find_by_id(users_table, request.id)
        
        if not rider:
            return api_response(404, {
                'message': 'Rider not found'
            })
        
        # Update rider with personal details and mark as completed
        status = rider.get('profileStatus', {})
        status['personalDetailsCompleted'] = True
        
        updated_rider = update(
            users_table,
            {'id': request.id},
            {
                'personalDetails': request.personalDetails.dict(),
                'profileStatus': status
            }
        )
        
        if updated_rider is None:
            return api_response(500, {
                'message': 'Failed to update personal details'
            })
        
        return api_response(200, updated_rider)
        
    except Exception as e:
        return api_response(400, {
            'message': 'Failed to update personal details',
            'error': str(e)
        })


@api_logger
def update_bank_details_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Handle bank details update"""
    try:
        # Parse request body
        body = json.loads(event.get('body', '{}'))
        request = RiderUpdateRequest(**body)
        
        if not request.bankDetails:
            return api_response(400, {
                'message': 'Bank details are required'
            })
        
        # Get current rider
        users_table = os.environ.get('USERS_TABLE', 'promodeagroUsers')
        rider = find_by_id(users_table, request.id)
        
        if not rider:
            return api_response(404, {
                'message': 'Rider not found'
            })
        
        # Update bank details with pending status
        bank_details = request.bankDetails.dict()
        bank_details['status'] = 'pending'
        
        status = rider.get('profileStatus', {})
        updated_rider = update(
            users_table,
            {'id': request.id},
            {
                'bankDetails': bank_details,
                'profileStatus': status
            }
        )
        
        if updated_rider is None:
            return api_response(500, {
                'message': 'Failed to update bank details'
            })
        
        return api_response(200, updated_rider)
        
    except Exception as e:
        return api_response(400, {
            'message': 'Failed to update bank details',
            'error': str(e)
        })


@api_logger
def update_document_details_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Handle document details update"""
    try:
        # Parse request body
        body = json.loads(event.get('body', '{}'))
        request = RiderUpdateRequest(**body)
        
        if not request.document:
            return api_response(400, {
                'message': 'Document details are required'
            })
        
        # Get current rider
        users_table = os.environ.get('USERS_TABLE', 'promodeagroUsers')
        rider = find_by_id(users_table, request.id)
        
        if not rider:
            return api_response(404, {
                'message': 'Rider not found'
            })
        
        # Update documents
        documents = rider.get('documents', [])
        updated_documents = []
        
        for doc in documents:
            if doc['name'] == request.document.name:
                updated_documents.append({
                    'name': request.document.name,
                    'image': request.document.image,
                    'verified': 'pending',
                    'rejectionReason': None
                })
            else:
                updated_documents.append(doc)
        
        updated_rider = update(
            users_table,
            {'id': request.id},
            {
                'documents': updated_documents
            }
        )
        
        if updated_rider is None:
            return api_response(500, {
                'message': 'Failed to update document details'
            })
        
        return api_response(200, updated_rider)
        
    except Exception as e:
        return api_response(400, {
            'message': 'Failed to update document details',
            'error': str(e)
        }) 