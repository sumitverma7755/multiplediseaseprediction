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
    # Initialize login state if not exists
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False
    
    # Custom CSS for modern login page with hidden sidebar
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');
    @import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css');
    
    /* Hide sidebar on login page */
    .css-1d391kg, .css-1lcbmhc, .css-17eq0hr, .css-k7vsyb, .css-1y0tadw {
        display: none !important;
    }
    
    /* Hide sidebar toggle button */
    .css-1rs6os.edgvbvh3, .css-17eq0hr.edgvbvh10 {
        display: none !important;
    }
    
    /* Hide main menu button */
    .css-14xtw13.e8zbici0 {
        display: none !important;
    }
    
    /* Modern purple-to-blue gradient background */
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        min-height: 100vh;
    }
    
    .main .block-container {
        padding: 0;
        max-width: none;
        background: transparent;
    }
    
    .login-main-container {
        display: flex;
        align-items: center;
        justify-content: center;
        min-height: 100vh;
        padding: 20px;
        position: relative;
        overflow: hidden;
        font-family: 'Inter', 'Poppins', sans-serif;
    }
    
    .login-main-container::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: 
            radial-gradient(circle at 20% 50%, rgba(120, 119, 198, 0.3) 0%, transparent 50%),
            radial-gradient(circle at 80% 20%, rgba(255, 255, 255, 0.1) 0%, transparent 50%),
            radial-gradient(circle at 40% 80%, rgba(120, 119, 198, 0.2) 0%, transparent 50%);
        pointer-events: none;
    }
    
    .login-container {
        display: flex;
        background: rgba(255, 255, 255, 0.98);
        backdrop-filter: blur(20px);
        border-radius: 24px;
        box-shadow: 0 25px 50px rgba(0, 0, 0, 0.15);
        overflow: hidden;
        width: 100%;
        max-width: 1000px;
        min-height: 600px;
        position: relative;
        z-index: 1;
    }
    
    .login-left {
        flex: 1;
        padding: 60px 50px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        background: white;
    }
    
    .login-right {
        flex: 1;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 40px;
        position: relative;
        color: white;
    }
    
    .illustration {
        text-align: center;
        z-index: 2;
    }
    
    .illustration i {
        font-size: 120px;
        margin-bottom: 20px;
        opacity: 0.9;
    }
    
    .illustration h3 {
        font-size: 1.8rem;
        margin-bottom: 15px;
        font-weight: 600;
        color: white;
    }
    
    .illustration p {
        font-size: 1.1rem;
        opacity: 0.9;
        line-height: 1.6;
        color: white;
    }
    
    .login-header {
        margin-bottom: 40px;
        text-align: left;
    }
    
    .login-header h2 {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1a202c;
        margin-bottom: 8px;
        font-family: 'Poppins', sans-serif;
    }
    
    .login-header p {
        color: #718096;
        font-size: 1.1rem;
        font-weight: 400;
    }
    
    .input-group {
        margin-bottom: 24px;
        position: relative;
    }
    
    .input-icon {
        position: absolute;
        left: 16px;
        top: 50%;
        transform: translateY(-50%);
        color: #a0aec0;
        font-size: 1.1rem;
        z-index: 2;
    }
    
    .stTextInput > div > div > input {
        border: 2px solid #e2e8f0 !important;
        border-radius: 12px !important;
        padding: 16px 16px 16px 50px !important;
        font-size: 1rem !important;
        transition: all 0.3s ease !important;
        background-color: #f7fafc !important;
        width: 100% !important;
        font-family: 'Inter', sans-serif !important;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #667eea !important;
        box-shadow: 0 0 0 4px rgba(102, 126, 234, 0.1) !important;
        background-color: white !important;
        outline: none !important;
    }
    
    .stTextInput > div > div > input:hover {
        border-color: #cbd5e0 !important;
        background-color: white !important;
    }
    
    .checkbox-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin: 24px 0;
        font-size: 0.9rem;
    }
    
    .remember-me {
        display: flex;
        align-items: center;
        color: #4a5568;
    }
    
    .forgot-password {
        color: #667eea;
        text-decoration: none;
        font-weight: 500;
        transition: color 0.3s ease;
    }
    
    .forgot-password:hover {
        color: #5a67d8;
        text-decoration: underline;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 16px 20px !important;
        font-size: 1.1rem !important;
        font-weight: 600 !important;
        cursor: pointer !important;
        transition: all 0.3s ease !important;
        width: 100% !important;
        margin: 20px 0 !important;
        font-family: 'Inter', sans-serif !important;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3) !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4) !important;
    }
    
    .stButton > button:active {
        transform: translateY(0) !important;
    }
    
    .divider {
        display: flex;
        align-items: center;
        margin: 30px 0;
        color: #a0aec0;
        font-size: 0.9rem;
    }
    
    .divider::before,
    .divider::after {
        content: '';
        flex: 1;
        height: 1px;
        background: #e2e8f0;
    }
    
    .divider span {
        padding: 0 16px;
        background: white;
    }
    
    .signup-link {
        text-align: center;
        margin-top: 32px;
        color: #718096;
        font-size: 0.95rem;
    }
    
    .signup-link a {
        color: #667eea;
        text-decoration: none;
        font-weight: 600;
        transition: color 0.3s ease;
    }
    
    .signup-link a:hover {
        color: #5a67d8;
        text-decoration: underline;
    }
    
    .success-message {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white;
        padding: 16px 20px;
        border-radius: 12px;
        margin: 20px 0;
        font-weight: 500;
        border-left: 4px solid #047857;
    }
    
    .error-message {
        background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
        color: white;
        padding: 16px 20px;
        border-radius: 12px;
        margin: 20px 0;
        font-weight: 500;
        border-left: 4px solid #b91c1c;
    }
    
    .warning-message {
        background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
        color: white;
        padding: 16px 20px;
        border-radius: 12px;
        margin: 20px 0;
        font-weight: 500;
        border-left: 4px solid #92400e;
    }
    
    /* Mobile Responsive */
    @media (max-width: 768px) {
        .login-container {
            flex-direction: column;
            max-width: 400px;
            min-height: auto;
        }
        
        .login-right {
            order: -1;
            min-height: 200px;
            padding: 30px 20px;
        }
        
        .login-left {
            padding: 40px 30px;
        }
        
        .login-header h2 {
            font-size: 2rem;
        }
        
        .illustration i {
            font-size: 80px;
        }
        
        .illustration h3 {
            font-size: 1.5rem;
        }
        
        .illustration p {
            font-size: 1rem;
        }
    }
    
    @media (max-width: 480px) {
        .login-main-container {
            padding: 10px;
        }
        
        .login-left {
            padding: 30px 20px;
        }
        
        .login-header h2 {
            font-size: 1.8rem;
        }
        
        .checkbox-row {
            flex-direction: column;
            align-items: flex-start;
            gap: 12px;
        }
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Main login container
    st.markdown("""
    <div class="login-main-container">
        <div class="login-container">
            <div class="login-left">
                <div class="login-header">
                    <h2>Welcome back</h2>
                    <p>Login to your account</p>
                </div>
    """, unsafe_allow_html=True)
    
    /* Full screen container for login */
    .main .block-container {
        padding-top: 0 !important;
        padding-bottom: 0 !important;
        max-width: 100% !important;
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
                        st.session_state['logged_in'] = True
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

# Registration UI with Modern Design
def registration_page():
    # Same CSS as login page (already included above)
    
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

# Main Application UI (shown after login)
def main_app():
    # Custom CSS to show sidebar and reset styling
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Reset login page CSS - show sidebar */
    .css-1d391kg, .css-1lcbmhc, .css-17eq0hr, .css-k7vsyb, .css-1y0tadw {
        display: block !important;
    }
    
    /* Show sidebar toggle button */
    .css-1rs6os.edgvbvh3, .css-17eq0hr.edgvbvh10 {
        display: block !important;
    }
    
    /* Show main menu button */
    .css-14xtw13.e8zbici0, .css-10trblm.e16nr0p30 {
        display: block !important;
    }
    
    /* Show Streamlit header */
    header[data-testid="stHeader"] {
        display: block !important;
    }
    
    /* Main app styling */
    .stApp {
        background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
        font-family: 'Inter', sans-serif;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
    }
    
    .sidebar-title {
        color: #fff;
        font-size: 1.5rem;
        font-weight: 700;
        margin-bottom: 20px;
        text-align: center;
        padding: 10px;
        border-bottom: 2px solid rgba(255, 255, 255, 0.1);
    }
    
    .user-info {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 20px;
        color: #fff;
        text-align: center;
    }
    
    .logout-button {
        background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%) !important;
        color: white !important;
        border: none !important;
        padding: 10px 20px !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        width: 100% !important;
        margin-top: 20px !important;
        transition: all 0.3s ease !important;
        cursor: pointer !important;
    }
    
    .logout-button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(239, 68, 68, 0.3) !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Sidebar content
    with st.sidebar:
        st.markdown('<div class="sidebar-title">🩺 Health AI</div>', unsafe_allow_html=True)
        
        # User info
        if 'user' in st.session_state:
            user = st.session_state['user']
            st.markdown(f"""
            <div class="user-info">
                <div style="font-size: 1.1rem; font-weight: 600; margin-bottom: 5px;">
                    👤 {user['username']}
                </div>
                <div style="font-size: 0.9rem; opacity: 0.8;">
                    Role: {user['role'].title()}
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # Navigation menu
        st.markdown("### 📋 Navigation")
        page = st.selectbox(
            "Choose a page:",
            ["Dashboard", "Disease Prediction", "Prediction History", "Profile Settings"],
            key="page_selector"
        )
        
        # Logout button
        if st.button("🚪 Logout", key="logout_btn", help="Sign out of your account"):
            logout()
    
    # Main content area
    st.title("🏥 Multiple Disease Prediction System")
    
    if page == "Dashboard":
        user_dashboard()
    elif page == "Disease Prediction":
        st.header("🔬 Disease Prediction Tools")
        st.info("Disease prediction functionality will be integrated here from your main application.")
        
        # Placeholder for disease prediction options
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            <div style="background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%); padding: 20px; border-radius: 10px; text-align: center; color: white;">
                <h3>💓 Heart Disease</h3>
                <p>Predict heart disease risk based on medical parameters</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div style="background: linear-gradient(135deg, #10b981 0%, #059669 100%); padding: 20px; border-radius: 10px; text-align: center; color: white;">
                <h3>🩸 Diabetes</h3>
                <p>Assess diabetes risk using health indicators</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
            <div style="background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%); padding: 20px; border-radius: 10px; text-align: center; color: white;">
                <h3>🧠 Parkinson's</h3>
                <p>Evaluate Parkinson's disease probability</p>
            </div>
            """, unsafe_allow_html=True)
        
    elif page == "Prediction History":
        st.header("📊 Your Prediction History")
        user_dashboard()
        
    elif page == "Profile Settings":
        st.header("⚙️ Profile Settings")
        st.info("Profile management features coming soon!")
        
        if 'user' in st.session_state:
            user = st.session_state['user']
            
            with st.form("profile_form"):
                st.subheader("Account Information")
                
                col1, col2 = st.columns(2)
                with col1:
                    st.text_input("Username", value=user['username'], disabled=True)
                    st.text_input("Role", value=user['role'].title(), disabled=True)
                
                with col2:
                    st.text_input("User ID", value=str(user['id']), disabled=True)
                    st.text_input("Account Type", value="Standard User", disabled=True)
                
                st.subheader("Change Password")
                current_password = st.text_input("Current Password", type="password")
                new_password = st.text_input("New Password", type="password")
                confirm_password = st.text_input("Confirm New Password", type="password")
                
                if st.form_submit_button("Update Profile"):
                    st.info("Profile update functionality will be implemented soon!")

# App Controller Function
def app_controller():
    """Main controller to handle login state and page routing"""
    
    # Initialize session state
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False
    
    # Check login status and route accordingly
    if not st.session_state['logged_in']:
        login_page()
    else:
        main_app()

# Logout function
def logout():
    """Clear session state and return to login page"""
    st.session_state.pop('user', None)
    st.session_state['logged_in'] = False
    st.rerun()

# Initialize the database
init_db()
