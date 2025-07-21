# src/dynamodb_scripts/run_full_journey.py
import boto3
import sys
from pathlib import Path
from decimal import Decimal

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

def print_section(title):
    print(f"\n{BOLD}{'='*10} {title} {'='*10}{RESET}")

def print_step(desc):
    print(f"{BOLD}{desc}{RESET}")

def print_result(result, detail=None):
    if result:
        print(f"{GREEN}SUCCESS{RESET}" + (f": {detail}" if detail else ""))
    else:
        print(f"{RED}FAILURE{RESET}" + (f": {detail}" if detail else ""))

def main():
    print(f"\n{BOLD}=== DYNAMODB FULL JOURNEY START ==={RESET}")
    dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')
    all_ok = True

    # --- Orders Table ---
    print_section("ORDERS TABLE")
    print_step("1. Creating Orders table...")
    ok = create_orders_table(dynamodb)
    print_result(ok)
    all_ok &= ok

    print_step("2. Inserting sample order data...")
    ok = insert_order_data(dynamodb)
    print_result(ok)
    all_ok &= ok

    print_step("3. Fetching order by ID...")
    try:
        table = dynamodb.Table('Orders')
        response = table.get_item(Key={'id': '401-3760341'})
        item = response.get('Item')
        if item:
            print(f"{GREEN}SUCCESS{RESET}: Order found: {item}")
        else:
            print(f"{RED}FAILURE{RESET}: Order not found.")
            all_ok = False
    except Exception as e:
        print(f"{RED}ERROR{RESET}: {e}")
        all_ok = False

    # --- Runsheet Table ---
    print_section("RUNSHEET TABLE")
    print_step("4. Creating Runsheets table...")
    ok = create_runsheets_table(dynamodb)
    print_result(ok)
    all_ok &= ok

    print_step("5. Inserting sample runsheet data...")
    ok = insert_runsheet_data(dynamodb)
    print_result(ok)
    all_ok &= ok

    print_step("6. Fetching runsheet by ID...")
    try:
        table = dynamodb.Table('Runsheets')
        response = table.get_item(Key={'id': 'c30962fde2cf'})
        item = response.get('Item')
        if item:
            print(f"{GREEN}SUCCESS{RESET}: Runsheet found: {item}")
        else:
            print(f"{RED}FAILURE{RESET}: Runsheet not found.")
            all_ok = False
    except Exception as e:
        print(f"{RED}ERROR{RESET}: {e}")
        all_ok = False

    # --- Inventory Table ---
    print_section("INVENTORY TABLE")
    print_step("7. Creating Inventory table...")
    ok = create_inventory_table(dynamodb)
    print_result(ok)
    all_ok &= ok

    print_step("8. Inserting sample inventory data...")
    ok = insert_inventory_data(dynamodb)
    print_result(ok)
    all_ok &= ok

    print_step("9. Fetching inventory by ID...")
    try:
        table = dynamodb.Table('Inventory')
        response = table.get_item(Key={'id': '74E5F8DD'})
        item = response.get('Item')
        if item:
            print(f"{GREEN}SUCCESS{RESET}: Inventory found: {item}")
        else:
            print(f"{RED}FAILURE{RESET}: Inventory not found.")
            all_ok = False
    except Exception as e:
        print(f"{RED}ERROR{RESET}: {e}")
        all_ok = False

    # --- Notifications Table ---
    print_section("NOTIFICATIONS TABLE")
    print_step("10. Creating Notifications table...")
    ok = create_notifications_table(dynamodb)
    print_result(ok)
    all_ok &= ok

    print_step("11. Inserting sample notification data...")
    ok = insert_notification_data(dynamodb)
    print_result(ok)
    all_ok &= ok

    print_step("12. Fetching notification by ID...")
    try:
        table = dynamodb.Table('Notifications')
        response = table.get_item(Key={'notificationId': 'notif-alert-001'})
        item = response.get('Item')
        if item:
            print(f"{GREEN}SUCCESS{RESET}: Notification found: {item}")
        else:
            print(f"{RED}FAILURE{RESET}: Notification not found.")
            all_ok = False
    except Exception as e:
        print(f"{RED}ERROR{RESET}: {e}")
        all_ok = False

    print(f"\n{BOLD}=== DYNAMODB FULL JOURNEY END ==={RESET}")
    if all_ok:
        print(f"{GREEN}{BOLD}ALL STEPS PASSED: All tables created, data inserted, and fetches succeeded.{RESET}")
    else:
        print(f"{RED}{BOLD}SOME STEPS FAILED: Check the output above for details.{RESET}")

if __name__ == '__main__':
    main() 