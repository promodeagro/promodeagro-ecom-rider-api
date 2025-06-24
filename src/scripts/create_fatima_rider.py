import requests
import json
from datetime import datetime

# Production API endpoint
PRODUCTION_URL = "http://localhost:3000"

def create_fatima_rider():
    """
    Create a rider with name 'fatimaT' in production environment
    """
    
    # Rider registration data for Fatima
    rider_data = {
        "personalDetails": {
            "fullName": "fatimaTabas",
            "dob": "1992-03-15",
            "email": "fatima.t@example.com",
            "number": "9876543214",
            "address": {
                "address1": "789 Fatima Street",
                "address2": "Apartment 7C",
                "landmark": "Near Fatima Mosque",
                "state": "Maharashtra",
                "city": "Mumbai",
                "pincode": "400002"
            },
            "reference": {
                "relation": "Sister",
                "number": "9876543215"
            }
        },
        "bankDetails": {
            "bankName": "ICICI Bank",
            "acc": "123456789012",
            "ifsc": "ICIC0001234"
        },
        "documents": [
            {
                "name": "userPhoto",
                "image": "https://example.com/fatima/user-photo.jpg"
            },
            {
                "name": "aadharFront",
                "image": "https://example.com/fatima/aadhar-front.jpg"
            },
            {
                "name": "aadharback",
                "image": "https://example.com/fatima/aadhar-back.jpg"
            },
            {
                "name": "pan",
                "image": "https://example.com/fatima/pan-card.jpg"
            },
            {
                "name": "drivingFront",
                "image": "https://example.com/fatima/driving-license-front.jpg"
            },
            {
                "name": "drivingBack",
                "image": "https://example.com/fatima/driving-license-back.jpg"
            },
            {
                "name": "VehicleImage",
                "image": "https://example.com/fatima/vehicle-image.jpg"
            },
            {
                "name": "rcFront",
                "image": "https://example.com/fatima/rc-front.jpg"
            },
            {
                "name": "rcBack",
                "image": "https://example.com/fatima/rc-back.jpg"
            }
        ]
    }
    
    try:
        print("🚀 Creating rider 'fatimaT' in production...")
        print(f"📡 API Endpoint: {PRODUCTION_URL}/register")
        print(f"📋 Request Data: {json.dumps(rider_data, indent=2)}")
        
        # Make API call to create rider
        response = requests.post(
            f"{PRODUCTION_URL}/register",
            json=rider_data,
            headers={
                "Content-Type": "application/json"
            },
            timeout=30
        )
        
        print(f"\n📊 Response Status Code: {response.status_code}")
        print(f"📋 Response Headers: {dict(response.headers)}")
        
        if response.status_code == 201:
            rider_info = response.json()
            print("\n✅ Rider 'fatimaT' created successfully!")
            print("=" * 50)
            print(f"🆔 Rider ID: {rider_info.get('id')}")
            print(f"👤 Rider Name: {rider_info.get('name')}")
            print(f"📱 Phone Number: {rider_info.get('number')}")
            print(f"📧 Email: {rider_info.get('personalDetails', {}).get('email')}")
            print(f"🏦 Bank: {rider_info.get('bankDetails', {}).get('bankName')}")
            print(f"📋 Review Status: {rider_info.get('reviewStatus')}")
            print(f"✅ Account Verified: {rider_info.get('accountVerified')}")
            print(f"📅 Submitted At: {rider_info.get('submittedAt')}")
            print(f"🔄 Updated At: {rider_info.get('updatedAt')}")
            print(f"👥 Role: {rider_info.get('role')}")
            print("=" * 50)
            
            # Show documents
            documents = rider_info.get('documents', [])
            print(f"📄 Documents ({len(documents)}):")
            for doc in documents:
                print(f"  - {doc.get('name')}: {doc.get('verified')} status")
            
            return rider_info
        else:
            print(f"\n❌ Failed to create rider 'fatimaT'")
            print(f"🔍 Error Response: {response.text}")
            try:
                error_json = response.json()
                print(f"📋 Error Details: {json.dumps(error_json, indent=2)}")
            except:
                pass
            return None
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Could not connect to the production server")
        print("💡 Make sure the production server is running on http://localhost:8000")
        return None
    except requests.exceptions.Timeout:
        print("❌ Timeout Error: Request timed out")
        return None
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"❌ JSON parsing error: {e}")
        return None
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return None

def test_health_check():
    """Test if the production server is running"""
    try:
        response = requests.get(f"{PRODUCTION_URL}/health", timeout=10)
        if response.status_code == 200:
            health_data = response.json()
            print("✅ Production server is running!")
            print(f"🏥 Health Status: {health_data.get('status')}")
            print(f"🌍 Environment: {health_data.get('environment')}")
            print(f"🗄️  Table: {health_data.get('table')}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

if __name__ == "__main__":
    print("🎯 FatimaT Rider Creation Script")
    print("=" * 50)
    
    # First check if server is running
    if test_health_check():
        print("\n" + "=" * 50)
        # Create the rider
        create_fatima_rider()
    else:
        print("\n❌ Cannot proceed: Production server is not running")
        print("💡 Please start the production server first:")
        print("   python prod-server.py")
    
    print("\n🎉 Script execution completed!") 