import requests
import json
from datetime import datetime

# Local server endpoint
LOCAL_URL = "http://localhost:3000/dev"

def create_dev_rider():
    """
    Create a rider for development environment
    """
    
    # Rider registration data for a test rider
    rider_data = {
        "personalDetails": {
            "fullName": "Test Rider",
            "dob": "1995-01-01",
            "email": "test.rider@example.com",
            "number": "1234567890",
            "address": {
                "address1": "123 Test Street",
                "address2": "Apartment 1A",
                "landmark": "Near Test Tower",
                "state": "Test State",
                "city": "Test City",
                "pincode": "123456"
            },
            "reference": {
                "relation": "Friend",
                "number": "0987654321"
            }
        },
        "bankDetails": {
            "bankName": "Test Bank",
            "acc": "987654321098",
            "ifsc": "TEST0001234"
        },
        "documents": [
            {
                "name": "userPhoto",
                "image": "https://example.com/test/user-photo.jpg"
            },
            {
                "name": "aadharFront",
                "image": "https://example.com/test/aadhar-front.jpg"
            },
            {
                "name": "aadharback",
                "image": "https://example.com/test/aadhar-back.jpg"
            },
            {
                "name": "pan",
                "image": "https://example.com/test/pan-card.jpg"
            },
            {
                "name": "drivingFront",
                "image": "https://example.com/test/driving-license-front.jpg"
            },
            {
                "name": "drivingBack",
                "image": "https://example.com/test/driving-license-back.jpg"
            },
            {
                "name": "VehicleImage",
                "image": "https://example.com/test/vehicle-image.jpg"
            },
            {
                "name": "rcFront",
                "image": "https://example.com/test/rc-front.jpg"
            },
            {
                "name": "rcBack",
                "image": "https://example.com/test/rc-back.jpg"
            }
        ]
    }
    
    try:
        print("🚀 Creating rider 'Test Rider' in development...")
        # The default stage for serverless-offline is dev. 
        # The create_fatima_rider.py had /register, but functions in function.yml seem to have /dev/register
        # I'll check src/handlers/rider/function.yml to be sure
        # functions:
        #   registerRider:
        #     handler: rider.register_rider
        #     events:
        #       - httpApi:
        #           path: /register
        #           method: post
        # The path is /register. serverless-offline prepends the stage, so /dev/register is correct.
        # But the original script used http://localhost:3000 without stage.
        # serverless-offline defaults to port 3000, and prepends the stage to the path.
        # Let's see the serverless-offline configuration in package.json
        # "offline": "serverless offline start",
        # Default serverless offline config should be checked.
        # The original script for fatima rider was hitting http://localhost:3000/register
        # But the serverless.yml has stage as 'dev' by default.
        # provider:
        #   stage: ${opt:stage, 'dev'}
        # Let me assume the stage is prepended. The original script might be wrong or for a different setup.
        # The URL in `create_fatima_rider.py` is `http://localhost:3000`. And it has a health check to `/health`.
        # I don't see a `/health` endpoint.
        # I see in `src/handlers/auth/function.yml`:
        #   login:
        #     handler: auth.login
        #     events:
        #       - httpApi:
        #           path: /login
        #           method: post
        # The `create_fatima_rider.py` script has `PRODUCTION_URL = "http://localhost:3000"`.
        # And `test_health_check` hits `f"{PRODUCTION_URL}/health"`.
        # This is confusing. I will stick with what serverless offline usually does.
        # Which is prefixing with the stage.
        
        url = f"{LOCAL_URL}/register"
        print(f"📡 API Endpoint: {url}")
        print(f"📋 Request Data: {json.dumps(rider_data, indent=2)}")
        
        response = requests.post(
            url,
            json=rider_data,
            headers={
                "Content-Type": "application/json"
            },
            timeout=30
        )
        
        print(f"\n📊 Response Status Code: {response.status_code}")
        
        if response.status_code == 201:
            rider_info = response.json()
            print("\n✅ Rider 'Test Rider' created successfully!")
            print("=" * 50)
            print(json.dumps(rider_info, indent=2))
            print("=" * 50)
            return rider_info
        else:
            print(f"\n❌ Failed to create rider 'Test Rider'")
            print(f"🔍 Error Response: {response.text}")
            try:
                error_json = response.json()
                print(f"📋 Error Details: {json.dumps(error_json, indent=2)}")
            except json.JSONDecodeError:
                pass
            return None
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Could not connect to the server.")
        print("💡 Make sure the local server is running. Try running 'npm run offline'")
        return None
    except requests.exceptions.Timeout:
        print("❌ Timeout Error: Request timed out")
        return None
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error: {e}")
        return None
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return None

if __name__ == "__main__":
    print("🎯 Test Rider Creation Script")
    print("=" * 50)
    create_dev_rider()
    print("\n🎉 Script execution completed!") 