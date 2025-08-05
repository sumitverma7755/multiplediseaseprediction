"""
Test script for the login system functionality
This demonstrates how the login system works without running the full Streamlit app
"""

import sys
import os

# Add the current directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Test the authentication functions
from auth import init_db, authenticate_user, register_user, hash_password

def test_login_system():
    """Test the basic login functionality"""
    print("🧪 Testing Login System")
    print("=" * 50)
    
    # Initialize database
    print("1. Initializing database...")
    init_db()
    print("   ✅ Database initialized successfully")
    
    # Test admin login
    print("\n2. Testing admin login...")
    admin_user = authenticate_user("admin", "admin123")
    if admin_user:
        print(f"   ✅ Admin login successful: {admin_user}")
    else:
        print("   ❌ Admin login failed")
    
    # Test wrong password
    print("\n3. Testing wrong password...")
    wrong_user = authenticate_user("admin", "wrongpassword")
    if wrong_user:
        print("   ❌ Wrong password test failed - should not authenticate")
    else:
        print("   ✅ Wrong password correctly rejected")
    
    # Test user registration
    print("\n4. Testing user registration...")
    success = register_user("testuser", "password123", "test@example.com")
    if success:
        print("   ✅ User registration successful")
        
        # Test login with new user
        test_user = authenticate_user("testuser", "password123")
        if test_user:
            print(f"   ✅ New user login successful: {test_user}")
        else:
            print("   ❌ New user login failed")
    else:
        print("   ❌ User registration failed")
    
    # Test duplicate registration
    print("\n5. Testing duplicate registration...")
    duplicate = register_user("testuser", "password123", "test@example.com")
    if duplicate:
        print("   ❌ Duplicate registration allowed - should be prevented")
    else:
        print("   ✅ Duplicate registration correctly prevented")
    
    print("\n" + "=" * 50)
    print("🎉 Login system test completed!")

def show_usage_example():
    """Show example of how to use the login system"""
    print("\n📚 Usage Example")
    print("=" * 50)
    
    example_code = '''
# In your main Streamlit app (multiplediseaseprediction.py):

import streamlit as st
from auth import login_page, logout

# Initialize session state
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

# Check login status
if not st.session_state['logged_in']:
    login_page()  # This shows login page with hidden sidebar
    st.stop()     # Stop execution until login

# Main app (only runs after successful login)
with st.sidebar:
    st.title("Your App")
    if st.button("Logout"):
        logout()  # This clears session and returns to login

st.title("Welcome to your protected app!")
'''
    
    print(example_code)

if __name__ == "__main__":
    test_login_system()
    show_usage_example()
    
    print("\n🔧 Implementation Features:")
    print("  • Sidebar completely hidden on login page")
    print("  • Session state management with 'logged_in' flag")
    print("  • Modern UI with healthcare theming")
    print("  • Responsive design for mobile devices")
    print("  • Form validation and error messages")
    print("  • Remember me functionality")
    print("  • Admin account (admin/admin123)")
    print("  • User registration with email validation")
    print("  • Logout button in sidebar")
    print("  • Compatible with Streamlit 1.4+")
