import streamlit as st
import sqlite3
import hashlib
import pandas as pd
from datetime import datetime

# Initialize connection to SQLite database
def init_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    
    # Create users table
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  username TEXT UNIQUE NOT NULL,
                  password TEXT NOT NULL,
                  email TEXT UNIQUE NOT NULL,
                  role TEXT NOT NULL,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    
    # Create predictions table
    c.execute('''CREATE TABLE IF NOT EXISTS predictions
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  user_id INTEGER,
                  disease_type TEXT NOT NULL,
                  prediction_result TEXT NOT NULL,
                  confidence REAL,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  FOREIGN KEY (user_id) REFERENCES users (id))''')
    
    # Create an admin user if it doesn't exist
    admin_exists = c.execute("SELECT 1 FROM users WHERE username = 'admin'").fetchone()
    if not admin_exists:
        admin_password = hashlib.sha256("admin123".encode()).hexdigest()
        c.execute("INSERT INTO users (username, password, email, role) VALUES (?, ?, ?, ?)",
                 ("admin", admin_password, "admin@healthai.com", "admin"))
    
    conn.commit()
    conn.close()

# Hash password
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# User authentication
def authenticate_user(username, password):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    hashed_pwd = hash_password(password)
    
    result = c.execute("SELECT id, username, role FROM users WHERE username = ? AND password = ?",
                      (username, hashed_pwd)).fetchone()
    conn.close()
    
    if result:
        return {"id": result[0], "username": result[1], "role": result[2]}
    return None

# User registration
def register_user(username, password, email):
    try:
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        hashed_pwd = hash_password(password)
        
        c.execute("INSERT INTO users (username, password, email, role) VALUES (?, ?, ?, ?)",
                 (username, hashed_pwd, email, "user"))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        return False

# Save prediction
def save_prediction(user_id, disease_type, prediction_result, confidence):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    
    c.execute("""INSERT INTO predictions 
                 (user_id, disease_type, prediction_result, confidence)
                 VALUES (?, ?, ?, ?)""",
              (user_id, disease_type, prediction_result, confidence))
    
    conn.commit()
    conn.close()

# Get user predictions
def get_user_predictions(user_id):
    conn = sqlite3.connect('users.db')
    df = pd.read_sql_query("""
        SELECT disease_type, prediction_result, confidence, created_at
        FROM predictions
        WHERE user_id = ?
        ORDER BY created_at DESC
    """, conn, params=(user_id,))
    conn.close()
    return df

# Login UI with Modern Design
def login_page():
    # Custom CSS for modern login page
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        font-family: 'Inter', sans-serif;
    }
    
    .login-container {
        display: flex;
        justify-content: center;
        align-items: center;
        min-height: 100vh;
        padding: 20px;
    }
    
    .login-card {
        background: rgba(255, 255, 255, 0.95);
        padding: 40px;
        border-radius: 20px;
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.2);
        width: 100%;
        max-width: 420px;
        text-align: center;
    }
    
    .logo-container {
        margin-bottom: 30px;
    }
    
    .logo {
        font-size: 2.5rem;
        font-weight: 700;
        color: #2563eb;
        margin-bottom: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 10px;
    }
    
    .tagline {
        color: #64748b;
        font-size: 0.95rem;
        font-weight: 400;
        margin-bottom: 0;
    }
    
    .login-header {
        color: #1e293b;
        font-size: 1.75rem;
        font-weight: 600;
        margin-bottom: 8px;
    }
    
    .login-subtitle {
        color: #64748b;
        font-size: 1rem;
        margin-bottom: 32px;
    }
    
    .input-group {
        position: relative;
        margin-bottom: 20px;
        text-align: left;
    }
    
    .input-label {
        color: #374151;
        font-weight: 500;
        font-size: 0.9rem;
        margin-bottom: 6px;
        display: block;
    }
    
    .stTextInput > div > div > input {
        padding: 14px 16px 14px 45px !important;
        border: 2px solid #e2e8f0 !important;
        border-radius: 12px !important;
        font-size: 1rem !important;
        font-family: 'Inter', sans-serif !important;
        background: #f8fafc !important;
        transition: all 0.3s ease !important;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #2563eb !important;
        box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1) !important;
        background: white !important;
    }
    
    .input-icon {
        position: absolute;
        left: 15px;
        top: 50%;
        transform: translateY(-50%);
        color: #64748b;
        font-size: 1.1rem;
        z-index: 1;
        pointer-events: none;
    }
    
    .login-button {
        background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%) !important;
        color: white !important;
        border: none !important;
        padding: 14px 24px !important;
        border-radius: 12px !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        width: 100% !important;
        margin: 20px 0 !important;
        transition: all 0.3s ease !important;
        cursor: pointer !important;
        font-family: 'Inter', sans-serif !important;
    }
    
    .login-button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 10px 30px rgba(37, 99, 235, 0.3) !important;
    }
    
    .register-link {
        color: #64748b;
        font-size: 0.9rem;
        margin-top: 24px;
    }
    
    .register-link a {
        color: #2563eb;
        text-decoration: none;
        font-weight: 600;
    }
    
    .register-link a:hover {
        text-decoration: underline;
    }
    
    .admin-info {
        background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
        border: 1px solid #0284c7;
        border-radius: 12px;
        padding: 16px;
        margin-top: 24px;
        text-align: left;
    }
    
    .admin-info-title {
        color: #0284c7;
        font-weight: 600;
        font-size: 0.9rem;
        margin-bottom: 8px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    
    .admin-info-text {
        color: #0369a1;
        font-size: 0.85rem;
        line-height: 1.4;
    }
    
    .error-message {
        background: #fef2f2;
        border: 1px solid #fecaca;
        color: #dc2626;
        padding: 12px;
        border-radius: 8px;
        margin: 16px 0;
        font-size: 0.9rem;
    }
    
    .success-message {
        background: #f0fdf4;
        border: 1px solid #bbf7d0;
        color: #16a34a;
        padding: 12px;
        border-radius: 8px;
        margin: 16px 0;
        font-size: 0.9rem;
    }
    
    .warning-message {
        background: #fffbeb;
        border: 1px solid #fed7aa;
        color: #ea580c;
        padding: 12px;
        border-radius: 8px;
        margin: 16px 0;
        font-size: 0.9rem;
    }
    
    @media (max-width: 768px) {
        .login-card {
            margin: 10px;
            padding: 30px 24px;
        }
        
        .logo {
            font-size: 2rem;
        }
        
        .login-header {
            font-size: 1.5rem;
        }
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Main container
    st.markdown('<div class="login-container">', unsafe_allow_html=True)
    
    # Login card
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
        <div class="login-card">
            <div class="logo-container">
                <div class="logo">
                    🩺 Health AI
                </div>
                <div class="tagline">Advanced Disease Prediction System</div>
            </div>
            
            <div class="login-header">Welcome Back</div>
            <div class="login-subtitle">Sign in to access your health dashboard</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Login form with enhanced styling
        with st.form("login_form", clear_on_submit=False):
            # Username field
            st.markdown('<div class="input-group">', unsafe_allow_html=True)
            st.markdown('<label class="input-label">👤 Username</label>', unsafe_allow_html=True)
            username = st.text_input("Username", placeholder="Enter your username", label_visibility="collapsed", key="username_input")
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Password field
            st.markdown('<div class="input-group">', unsafe_allow_html=True)
            st.markdown('<label class="input-label">🔒 Password</label>', unsafe_allow_html=True)
            password = st.text_input("Password", placeholder="Enter your password", type="password", label_visibility="collapsed", key="password_input")
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Remember me checkbox
            col_remember, col_forgot = st.columns([1, 1])
            with col_remember:
                remember_me = st.checkbox("Remember me", key="remember_checkbox")
            with col_forgot:
                st.markdown('<div style="text-align: right; margin-top: 8px;"><a href="#" style="color: #2563eb; text-decoration: none; font-size: 0.9rem;">Forgot Password?</a></div>', unsafe_allow_html=True)
            
            # Login button
            submitted = st.form_submit_button("Sign In", use_container_width=True)
            
            if submitted:
                if username and password:
                    user = authenticate_user(username, password)
                    if user:
                        st.session_state['user'] = user
                        st.markdown('<div class="success-message">✅ Login successful! Redirecting...</div>', unsafe_allow_html=True)
                        st.rerun()
                    else:
                        st.markdown('<div class="error-message">❌ Invalid username or password. Please try again.</div>', unsafe_allow_html=True)
                else:
                    st.markdown('<div class="warning-message">⚠️ Please enter both username and password.</div>', unsafe_allow_html=True)
        
        # Register link
        st.markdown("""
        <div class="register-link">
            Don't have an account? <a href="#" onclick="return false;">Create Account</a>
        </div>
        """, unsafe_allow_html=True)
        
        # Admin info
        st.markdown("""
        <div class="admin-info">
            <div class="admin-info-title">
                👨‍⚕️ Demo Account
            </div>
            <div class="admin-info-text">
                <strong>Username:</strong> admin<br>
                <strong>Password:</strong> admin123
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# Registration UI with Modern Design
def registration_page():
    # Same CSS as login page (already included above)
    
    # Main container
    st.markdown('<div class="login-container">', unsafe_allow_html=True)
    
    # Registration card
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
        <div class="login-card">
            <div class="logo-container">
                <div class="logo">
                    🩺 Health AI
                </div>
                <div class="tagline">Advanced Disease Prediction System</div>
            </div>
            
            <div class="login-header">Create Account</div>
            <div class="login-subtitle">Join us to start monitoring your health</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Registration form
        with st.form("registration_form", clear_on_submit=False):
            # Username field
            st.markdown('<div class="input-group">', unsafe_allow_html=True)
            st.markdown('<label class="input-label">👤 Username</label>', unsafe_allow_html=True)
            username = st.text_input("Username", placeholder="Choose a username", label_visibility="collapsed", key="reg_username")
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Email field
            st.markdown('<div class="input-group">', unsafe_allow_html=True)
            st.markdown('<label class="input-label">📧 Email Address</label>', unsafe_allow_html=True)
            email = st.text_input("Email", placeholder="Enter your email", label_visibility="collapsed", key="reg_email")
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Password field
            st.markdown('<div class="input-group">', unsafe_allow_html=True)
            st.markdown('<label class="input-label">🔒 Password</label>', unsafe_allow_html=True)
            password = st.text_input("Password", placeholder="Create a password (min. 6 characters)", type="password", label_visibility="collapsed", key="reg_password")
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Confirm password field
            st.markdown('<div class="input-group">', unsafe_allow_html=True)
            st.markdown('<label class="input-label">🔒 Confirm Password</label>', unsafe_allow_html=True)
            confirm_password = st.text_input("Confirm Password", placeholder="Confirm your password", type="password", label_visibility="collapsed", key="reg_confirm_password")
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Terms agreement
            terms_agreed = st.checkbox("I agree to the Terms of Service and Privacy Policy", key="terms_checkbox")
            
            # Register button
            submitted = st.form_submit_button("Create Account", use_container_width=True)
            
            if submitted:
                if not username or not email or not password or not confirm_password:
                    st.markdown('<div class="warning-message">⚠️ Please fill in all fields.</div>', unsafe_allow_html=True)
                elif password != confirm_password:
                    st.markdown('<div class="error-message">❌ Passwords do not match.</div>', unsafe_allow_html=True)
                elif len(password) < 6:
                    st.markdown('<div class="error-message">❌ Password must be at least 6 characters long.</div>', unsafe_allow_html=True)
                elif not terms_agreed:
                    st.markdown('<div class="warning-message">⚠️ Please agree to the Terms of Service.</div>', unsafe_allow_html=True)
                else:
                    if register_user(username, password, email):
                        st.markdown('<div class="success-message">✅ Registration successful! You can now login.</div>', unsafe_allow_html=True)
                        st.session_state['show_registration'] = False
                        st.rerun()
                    else:
                        st.markdown('<div class="error-message">❌ Username or email already exists.</div>', unsafe_allow_html=True)
        
        # Login link
        st.markdown("""
        <div class="register-link">
            Already have an account? <a href="#" onclick="return false;">Sign In</a>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# Admin Panel UI
def admin_panel():
    st.title("Admin Panel")
    st.write("Admin functionality placeholder")

# User Dashboard UI
def user_dashboard():
    if 'user' not in st.session_state:
        st.error("Please login to access your dashboard.")
        return
    
    user = st.session_state.user
    st.title("User Dashboard")
    st.write(f"Welcome, {user['username']}!")
    
    # Get user predictions
    predictions_df = get_user_predictions(user['id'])
    
    if not predictions_df.empty:
        try:
            # Format the date column
            predictions_df['created_at'] = pd.to_datetime(predictions_df['created_at']).dt.strftime('%Y-%m-%d %H:%M')
            
            # Rename columns for better display
            predictions_df.columns = ['Disease Type', 'Prediction', 'Confidence', 'Date']
            
            # Display predictions
            st.subheader("Your Prediction History")
            st.dataframe(predictions_df)
        except Exception as e:
            st.error("Error displaying prediction history. Please try refreshing the page.")
            print(f"Error in user_dashboard: {e}")
    else:
        st.info("You haven't made any predictions yet. Try out our disease prediction tools!")

# Logout function
def logout():
    st.session_state.pop('user', None)
    st.rerun()

# Initialize the database
init_db()
