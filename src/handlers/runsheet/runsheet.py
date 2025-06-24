import json
import os
from datetime import datetime
from typing import Dict, Any

from src.commonfunctions.logger import api_logger
from src.commonfunctions.dynamodb import find_by_id, update, batch_get
from src.commonfunctions.response import api_response


@api_logger
def list_runsheets_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    runsheet_table = os.environ.get('RUNSHEET_TABLE')
    orders_table = os.environ.get('ORDERS_TABLE')
    id = event.get('pathParameters', {}).get('id')
    if not id:
        return api_response(400, {'message': 'invalid id'})
    # Query runsheets for this rider
    from boto3.dynamodb.conditions import Key
    import boto3
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(runsheet_table)
    response = table.query(
        IndexName='riderIndex',
        KeyConditionExpression=Key('riderId').eq(id),
        FilterExpression='(#status = :pending OR #status = :active)',
        ExpressionAttributeNames={'#status': 'status'},
        ExpressionAttributeValues={':pending': 'pending', ':active': 'active'}
    )
    items = response.get('Items', [])
    all_orders = set()
    for item in items:
        all_orders.update(item.get('orders', []))
    order_statuses = {}
    if all_orders:
        keys = [{'id': oid} for oid in all_orders]
        orders = batch_get(orders_table, keys)
        for order in orders:
            order_statuses[order['id']] = order.get('status')
    result = []
    for item in items:
        total_orders = len(item.get('orders', []))
        item_order_statuses = [order_statuses.get(oid) for oid in item.get('orders', [])]
        delivered = item_order_statuses.count('delivered')
        undelivered = item_order_statuses.count('undelivered')
        pending = item_order_statuses.count(None)
        result.append({
            'id': item['id'],
            'orders': total_orders,
            'pendingOrders': pending,
            'status': item.get('status'),
            'deliveredOrders': delivered,
            'undeliveredOrders': undelivered,
            'amountCollectable': item.get('amountCollectable', 0)
        })
    return api_response(200, result)


@api_logger
def accept_runsheet_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    runsheet_table = os.environ.get('RUNSHEET_TABLE')
    runsheet_id = event.get('pathParameters', {}).get('runsheetId')
    if not runsheet_id:
        return api_response(400, {'message': 'invalid id'})
    updated = update(
        runsheet_table,
        {'id': runsheet_id},
        {
            'status': 'active',
            'acceptedAt': datetime.utcnow().isoformat() + 'Z'
        }
    )
    return api_response(200, updated)


@api_logger
def get_runsheet_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    runsheet_table = os.environ.get('RUNSHEET_TABLE')
    orders_table = os.environ.get('ORDERS_TABLE')
    runsheet_id = event.get('pathParameters', {}).get('runsheetId')
    if not runsheet_id:
        return api_response(400, {'message': 'invalid id'})
    runsheet = find_by_id(runsheet_table, runsheet_id)
    if not runsheet:
        return api_response(404, {'message': 'Runsheet not found'})
    order_ids = runsheet.get('orders', [])
    orders = batch_get(orders_table, [{'id': oid} for oid in order_ids])
    for order in orders:
        order.pop('_version', None)
        order.pop('taskToken', None)
        order.pop('__typename', None)
    runsheet['orders'] = orders
    return api_response(200, runsheet)


@api_logger
def confirm_order_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    runsheet_table = os.environ.get('RUNSHEET_TABLE')
    orders_table = os.environ.get('ORDERS_TABLE')
    path = event.get('pathParameters', {})
    runsheet_id = path.get('runsheetId')
    order_id = path.get('orderId')
    if not runsheet_id or not order_id:
        return api_response(400, {'message': 'invalid id'})
    body = json.loads(event.get('body', '{}'))
    image = body.get('image')
    via = body.get('via')
    runsheet = find_by_id(runsheet_table, runsheet_id)
    if not runsheet or order_id not in runsheet.get('orders', []):
        return api_response(400, {'message': 'order doesnt exist in runsheet.'})
    order = find_by_id(orders_table, order_id)
    if not order:
        return api_response(404, {'message': 'Order not found'})
    
    print(f"Orders table: {orders_table}")
    print(f"Current order data: {order}")
    print(f"Updating order {order_id} from status '{order.get('status')}' to 'delivered'")
    
    if order.get('paymentDetails', {}).get('method') == 'cash':
        payment_details = order['paymentDetails']
        payment_details['status'] = 'DONE'
        payment_details['via'] = via
        update_data = {
            'status': 'delivered',
            'deliveredAt': datetime.utcnow().isoformat() + 'Z',
            'deliveredImage': image,
            'paymentDetails': payment_details
        }
    else:
        update_data = {
            'status': 'delivered',
            'deliveredAt': datetime.utcnow().isoformat() + 'Z',
            'deliveredImage': image
        }
    
    print(f"Update data: {update_data}")
    updated = update(orders_table, {'id': order_id}, update_data)
    
    if updated is None:
        print(f"Failed to update order {order_id} - update returned None")
        return api_response(500, {'message': 'Failed to update order status'})
    
    print(f"Successfully updated order {order_id}. New status: {updated.get('status')}")
    return api_response(200, updated)


@api_logger
def cancel_order_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    runsheet_table = os.environ.get('RUNSHEET_TABLE')
    orders_table = os.environ.get('ORDERS_TABLE')
    path = event.get('pathParameters', {})
    runsheet_id = path.get('runsheetId')
    order_id = path.get('orderId')
    if not runsheet_id or not order_id:
        return api_response(400, {'message': 'invalid id'})
    body = json.loads(event.get('body', '{}'))
    reason = body.get('reason')
    runsheet = find_by_id(runsheet_table, runsheet_id)
    if not runsheet or order_id not in runsheet.get('orders', []):
        return api_response(400, {'message': 'order doesnt exist in runsheet.'})
    order = find_by_id(orders_table, order_id)
    if order.get('status') == 'cancelled':
        return api_response(400, {'message': 'order already cancelled'})
    
    # Check if order is already undelivered or delivered
    if order.get('status') in ['undelivered', 'delivered']:
        return api_response(400, {'message': f'order is already {order.get("status")}'})
    
    print(f"Orders table: {orders_table}")
    print(f"Current order data: {order}")
    print(f"Cancelling order {order_id} from status '{order.get('status')}'")
    
    status_details = {
        'reason': reason,
        'updatedBy': 'rider'
    }
    status = 'cancelled' if reason == 'rejected by customer' else 'undelivered'
    
    update_data = {
        'status': status,
        'statusDetails': status_details
    }
    
    print(f"Update data: {update_data}")
    updated = update(orders_table, {'id': order_id}, update_data)
    
    if updated is None:
        print(f"Failed to update order {order_id} - update returned None")
        return api_response(500, {'message': 'Failed to update order status'})
    
    print(f"Successfully updated order {order_id}. New status: {updated.get('status')}")
    return api_response(200, updated) 