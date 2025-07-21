import boto3
from decimal import Decimal
from botocore.exceptions import ClientError
import sys
from pathlib import Path

# ANSI color codes for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
RESET = '\033[0m'
BOLD = '\033[1m'

# Add project root to the Python path to allow importing from other scripts.
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

from dynamodb_scripts.create_order import create_orders_table, insert_order_data
from dynamodb_scripts.create_runsheet import create_runsheets_table, insert_runsheet_data
from dynamodb_scripts.create_inventory import create_inventory_table, insert_inventory_data
from dynamodb_scripts.create_notification import create_notifications_table, insert_notification_data

def fetch_table_item(dynamodb, table_name, key, expected=None):
    try:
        table = dynamodb.Table(table_name)
        response = table.get_item(Key=key)
        item = response.get('Item')
        if not item:
            print(f"{RED}FAIL{RESET}: No item found in '{table_name}' for key {key}")
            return 'FAIL'
        if expected:
            for field, value in expected.items():
                if field not in item:
                    print(f"{YELLOW}WRONG{RESET}: Field '{field}' missing in '{table_name}' for key {key}")
                    return 'WRONG'
                if item[field] != value:
                    print(f"{YELLOW}WRONG{RESET}: Field '{field}' in '{table_name}' for key {key} has value '{item[field]}' but expected '{value}'")
                    return 'WRONG'
        print(f"{GREEN}PASS{RESET}: Found item in '{table_name}' for key {key}")
        return 'PASS'
    except Exception as e:
        print(f"{RED}ERROR{RESET}: Could not fetch from '{table_name}': {e}")
        return 'FAIL'

def test_step(idx, desc, func):
    print(f"{BOLD}Step {idx}:{RESET} {desc} ...", end=" ")
    try:
        result = func()
        if result == 'PASS' or result is True:
            print(f"{GREEN}PASS{RESET}")
            return 'PASS'
        elif result == 'WRONG':
            print(f"{YELLOW}WRONG{RESET}")
            return 'WRONG'
        else:
            print(f"{RED}FAIL{RESET}")
            return 'FAIL'
    except Exception as e:
        print(f"{RED}ERROR: {e}{RESET}")
        return 'FAIL'

def print_section(title):
    print(f"\n{BOLD}{'='*10} {title} {'='*10}{RESET}")

def print_summary(total, passed, wrong, failed):
    print(f"\n{BOLD}{'='*8} TEST SUMMARY {'='*8}{RESET}")
    print(f"{BOLD}Total:{RESET}   {total}")
    print(f"{GREEN}Passed:{RESET}  {passed}")
    print(f"{YELLOW}Wrong:{RESET}   {wrong}")
    print(f"{RED}Failed:{RESET}  {failed}")
    print(f"{BOLD}{'='*30}{RESET}")
    if failed == 0 and wrong == 0:
        print(f"{GREEN}{BOLD}ALL TESTS PASSED: All tables created, data inserted, and fetches succeeded.{RESET}")
    elif failed == 0:
        print(f"{YELLOW}{BOLD}SOME TESTS WRONG: All steps ran, but some data was not as expected.{RESET}")
    else:
        print(f"{RED}{BOLD}SOME TESTS FAILED: Check the output above for details.{RESET}")

def main():
    print(f"\n{BOLD}=== DYNAMODB TEST JOURNEY START ==={RESET}")
    dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')
    results = []
    step = 1

    # 1. Create and insert for Orders
    print_section("Testing Orders Table")
    results.append(test_step(step, "Create Orders table", lambda: create_orders_table(dynamodb))); step += 1
    results.append(test_step(step, "Insert order data", lambda: insert_order_data(dynamodb))); step += 1
    results.append(test_step(
        step, "Fetch order data and check customerName",
        lambda: fetch_table_item(
            dynamodb, 'Orders', {'id': '401-3760341'}, expected={"customerName": "Fatima "}
        )
    )); step += 1

    # 2. Create and insert for Runsheets
    print_section("Testing Runsheets Table")
    results.append(test_step(step, "Create Runsheets table", lambda: create_runsheets_table(dynamodb))); step += 1
    results.append(test_step(step, "Insert runsheet data", lambda: insert_runsheet_data(dynamodb))); step += 1
    results.append(test_step(
        step, "Fetch runsheet data and check status",
        lambda: fetch_table_item(
            dynamodb, 'Runsheets', {'id': 'c30962fde2cf'}, expected={"status": "active"}
        )
    )); step += 1

    # 3. Create and insert for Inventory
    print_section("Testing Inventory Table")
    results.append(test_step(step, "Create Inventory table", lambda: create_inventory_table(dynamodb))); step += 1
    results.append(test_step(step, "Insert inventory data", lambda: insert_inventory_data(dynamodb))); step += 1
    results.append(test_step(
        step, "Fetch inventory data and check stockQuantity",
        lambda: fetch_table_item(
            dynamodb, 'Inventory', {'id': '74E5F8DD'}, expected={"stockQuantity": Decimal('25')}
        )
    )); step += 1

    # 4. Create and insert for Notifications
    print_section("Testing Notifications Table")
    results.append(test_step(step, "Create Notifications table", lambda: create_notifications_table(dynamodb))); step += 1
    results.append(test_step(step, "Insert notification data", lambda: insert_notification_data(dynamodb))); step += 1
    results.append(test_step(
        step, "Fetch notification data and check title",
        lambda: fetch_table_item(
            dynamodb, 'Notifications', {'notificationId': 'notif-alert-001'}, expected={"title": "Your Order is on its way!"}
        )
    )); step += 1

    total = len(results)
    passed = sum(1 for r in results if r == 'PASS')
    wrong = sum(1 for r in results if r == 'WRONG')
    failed = sum(1 for r in results if r == 'FAIL')

    print(f"\n{BOLD}=== DYNAMODB TEST JOURNEY END ==={RESET}")
    print_summary(total, passed, wrong, failed)

if __name__ == '__main__':
    main() 