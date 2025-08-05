# Streamlit Login System with Hidden Sidebar

This implementation provides a complete authentication system for Streamlit applications that hides the sidebar until the user successfully logs in.

## 🌟 Features

- **Hidden Sidebar**: Sidebar is completely hidden on the login page using CSS
- **Session Management**: Uses `st.session_state['logged_in']` to manage login status
- **Modern UI**: Healthcare-themed design with glassmorphism effects
- **Responsive Design**: Works on desktop and mobile devices
- **Form Validation**: Input validation with clear error messages
- **Admin Account**: Pre-configured admin account (admin/admin123)
- **User Registration**: New user registration with email validation
- **Logout Functionality**: Logout button in sidebar that resets session
- **Streamlit Compatible**: Works with Streamlit 1.4 and above

## 🚀 Quick Start

### 1. Run the Application

```bash
streamlit run multiplediseaseprediction.py
```

### 2. Login

Use the admin account to test:
- **Username**: admin
- **Password**: admin123

Or create a new account using the registration form.

## 📁 File Structure

```
├── auth.py                    # Authentication system
├── multiplediseaseprediction.py   # Main application with login integration
├── login_demo.py             # Standalone demo
└── test_login.py             # Test script
```

## 🔧 Implementation Details

### Login Page Features

The login page (`login_page()` function) includes:

- **Hidden Sidebar CSS**: Completely hides sidebar elements
- **Modern Design**: Healthcare-themed UI with blue color scheme
- **Form Elements**:
  - Username field with user icon
  - Password field with lock icon
  - Remember me checkbox
  - Forgot password link (placeholder)
  - Login button with hover effects
- **Error Messages**: Styled feedback for invalid credentials
- **Registration Link**: Option to create new account

### Main Application Integration

The main app checks login status and:

- Shows login page if not authenticated
- Displays full app with sidebar if authenticated
- Includes user info in sidebar
- Provides logout button

### CSS Implementation

Key CSS features for hiding sidebar:

```css
/* Hide sidebar elements */
.css-1d391kg, .css-1lcbmhc, .css-17eq0hr, .css-k7vsyb, .css-1y0tadw {
    display: none !important;
}

/* Hide sidebar toggle button */
.css-1rs6os.edgvbvh3, .css-17eq0hr.edgvbvh10 {
    display: none !important;
}

/* Hide main menu */
.css-14xtw13.e8zbici0, .css-10trblm.e16nr0p30 {
    display: none !important;
}
```

## 🎨 Customization

### Modify Login Page Styling

Edit the CSS in `login_page()` function in `auth.py`:

```python
def login_page():
    st.markdown("""
    <style>
    /* Your custom CSS here */
    .login-card {
        background: your-custom-color;
        /* ... other styles */
    }
    </style>
    """, unsafe_allow_html=True)
```

### Change Color Scheme

Update the color variables in the CSS:

```css
/* Primary colors */
--primary-blue: #2563eb;
--primary-dark: #1d4ed8;
--background-gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
```

### Add Custom Fields

Add new fields to the login form:

```python
# In login_page() function
email = st.text_input("Email", placeholder="Enter your email")
department = st.selectbox("Department", ["IT", "HR", "Finance"])
```

## 🔐 Security Features

- **Password Hashing**: SHA-256 encryption for stored passwords
- **SQL Injection Protection**: Parameterized queries
- **Session Management**: Secure session state handling
- **Input Validation**: Client-side and server-side validation

## 📱 Mobile Responsiveness

The login page includes responsive CSS:

```css
@media (max-width: 768px) {
    .login-card {
        margin: 10px;
        padding: 30px 24px;
    }
    
    .logo {
        font-size: 2rem;
    }
}
```

## 🧪 Testing

Run the test script to verify functionality:

```bash
python test_login.py
```

This will test:
- Database initialization
- Admin login
- User registration
- Duplicate prevention
- Wrong password handling

## 📋 API Reference

### Authentication Functions

#### `login_page()`
Displays the login page with hidden sidebar.

#### `main_app()`
Shows the main application after successful login.

#### `authenticate_user(username, password)`
Validates user credentials and returns user data.

#### `register_user(username, password, email)`
Creates new user account.

#### `logout()`
Clears session state and returns to login page.

### Session State Variables

- `st.session_state['logged_in']`: Boolean login status
- `st.session_state['user']`: User data dictionary

## 🚨 Troubleshooting

### Common Issues

1. **Sidebar Still Visible**
   - Check CSS selectors match your Streamlit version
   - Clear browser cache
   - Verify CSS is properly injected

2. **Login Not Persisting**
   - Ensure session state is properly initialized
   - Check for competing session state modifications

3. **Database Errors**
   - Verify SQLite database permissions
   - Check if `users.db` file is created

### Debug Mode

Add debug information to troubleshoot:

```python
# Add to main app
st.sidebar.write("Debug Info:")
st.sidebar.write(f"Logged in: {st.session_state.get('logged_in', False)}")
st.sidebar.write(f"User: {st.session_state.get('user', None)}")
```

## 🔄 Migration Guide

### From Basic Streamlit App

1. Import auth functions:
```python
from auth import login_page, logout
```

2. Add login check:
```python
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

if not st.session_state['logged_in']:
    login_page()
    st.stop()
```

3. Add logout button:
```python
if st.button("Logout"):
    logout()
```

## 📄 License

This implementation is open source and can be freely modified for your projects.

## 🤝 Contributing

Feel free to submit issues and enhancement requests!

## 📞 Support

For questions or issues, please refer to the test script and implementation examples provided.
