import streamlit as st
import sqlite3
import hashlib
import pandas as pd
import time

# Initialize database tables on import
def init_database():
    """Initialize database tables"""
    create_user_table()
    create_prediction_table()
    create_admin_user()

# Database functions
def create_user_table():
    """Create users table if it doesn't exist"""
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT DEFAULT 'user',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def create_prediction_table():
    """Create predictions table if it doesn't exist"""
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS predictions(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            prediction_type TEXT NOT NULL,
            input_data TEXT NOT NULL,
            result TEXT NOT NULL,
            confidence REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    conn.commit()
    conn.close()

def hash_password(password):
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def create_admin_user():
    """Create default admin user if not exists"""
    create_user_table()
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    
    # Check if admin exists
    c.execute("SELECT * FROM users WHERE username = 'admin'")
    if not c.fetchone():
        # Create admin user
        admin_password = hash_password('admin123')
        c.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                 ('admin', admin_password, 'admin'))
        conn.commit()
    
    conn.close()

def authenticate_user(username, password):
    """Authenticate user login"""
    create_user_table()
    create_admin_user()
    
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    
    hashed_password = hash_password(password)
    c.execute("SELECT * FROM users WHERE username = ? AND password = ?", 
             (username, hashed_password))
    user = c.fetchone()
    conn.close()
    
    if user:
        return {
            'id': user[0],
            'username': user[1],
            'role': user[3]
        }
    return None

def register_user(username, password, role='user'):
    """Register a new user"""
    create_user_table()
    
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    
    try:
        hashed_password = hash_password(password)
        c.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                 (username, hashed_password, role))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        conn.close()
        return False

def save_prediction(user_id, prediction_type, input_data, result, confidence):
    """Save prediction to database"""
    create_prediction_table()
    
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    
    c.execute("""INSERT INTO predictions 
                (user_id, prediction_type, input_data, result, confidence) 
                VALUES (?, ?, ?, ?, ?)""",
             (user_id, prediction_type, str(input_data), result, confidence))
    conn.commit()
    conn.close()

def get_user_predictions(user_id):
    """Get user's prediction history"""
    create_prediction_table()
    
    conn = sqlite3.connect('users.db')
    df = pd.read_sql_query("""
        SELECT prediction_type, result, confidence, created_at 
        FROM predictions 
        WHERE user_id = ? 
        ORDER BY created_at DESC
    """, conn, params=(user_id,))
    conn.close()
    return df

def logout():
    """Logout user"""
    for key in ['logged_in', 'user', 'show_registration']:
        if key in st.session_state:
            del st.session_state[key]
    st.rerun()

# Modern Login UI with Purple-to-Blue Gradient
def login_page():
    # Initialize login state if not exists
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False
    
    # Modern CSS Styling with Purple-to-Blue Gradient
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');
        @import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css');
        
        /* Ensure proper font rendering */
        * {
            font-family: 'Inter', 'Poppins', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
        }
        
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
            font-size: 2.5rem !important;
            font-weight: 700 !important;
            color: #1a202c !important;
            margin-bottom: 8px !important;
            font-family: 'Poppins', sans-serif !important;
            display: block !important;
            visibility: visible !important;
        }
        }
        
        .login-header p {
            color: #718096 !important;
            font-size: 1.1rem !important;
            font-weight: 400 !important;
            margin: 8px 0 24px 0 !important;
            line-height: 1.5 !important;
            display: block !important;
            visibility: visible !important;
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
        }
        
        .error-message {
            background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
            color: white;
            padding: 16px 20px;
            border-radius: 12px;
            margin: 20px 0;
            font-weight: 500;
        }
        
        .warning-message {
            background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
            color: white;
            padding: 16px 20px;
            border-radius: 12px;
            margin: 20px 0;
            font-weight: 500;
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
                    <p>Please login to your account</p>
                </div>
    """, unsafe_allow_html=True)
    
    # Login form
    with st.form("login_form", clear_on_submit=False):
        # Email field with icon
        st.markdown('<div class="input-group"><i class="fas fa-envelope input-icon"></i></div>', unsafe_allow_html=True)
        username = st.text_input("Email address", placeholder="Email address", label_visibility="collapsed", key="username_input")
        
        # Password field with icon
        st.markdown('<div class="input-group"><i class="fas fa-lock input-icon"></i></div>', unsafe_allow_html=True)
        password = st.text_input("Password", placeholder="Password", type="password", label_visibility="collapsed", key="password_input")
        
        # Remember me and forgot password row
        col1, col2 = st.columns([1, 1])
        with col1:
            remember_me = st.checkbox("✅ Remember me", key="remember_checkbox")
        with col2:
            st.markdown('<div style="text-align: right; margin-top: 8px;"><a href="#" class="forgot-password">🔗 Forgot password?</a></div>', unsafe_allow_html=True)
        
        # Login button
        submitted = st.form_submit_button("Login", use_container_width=True)
        
        if submitted:
            if username and password:
                user = authenticate_user(username, password)
                if user:
                    st.session_state['user'] = user
                    st.session_state['logged_in'] = True
                    st.markdown('<div class="success-message">✅ Login successful! Redirecting...</div>', unsafe_allow_html=True)
                    time.sleep(1)
                    st.rerun()
                else:
                    st.markdown('<div class="error-message">❌ Invalid email or password. Please try again.</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="warning-message">⚠️ Please enter both email and password.</div>', unsafe_allow_html=True)
    
    # Divider
    st.markdown('<div class="divider"><span>or</span></div>', unsafe_allow_html=True)
    
    # Google sign-in button (styled to match design)
    col1, col2, col3 = st.columns([0.5, 2, 0.5])
    with col2:
        if st.button("🔵 Sign in with Google", key="google_signin", use_container_width=True):
            st.info("Google Sign-In integration coming soon!")
    
    # Sign up link
    st.markdown('<div class="signup-link">Don\'t have an account? <a href="#">Sign Up</a></div>', unsafe_allow_html=True)
    
    # Close containers and add right side illustration
    st.markdown("""
            </div>
            <div class="login-right">
                <div class="illustration">
                    <i class="fas fa-user-check"></i>
                    <h3>Secure Health Platform</h3>
                    <p>Access your personalized health predictions and medical insights with our advanced AI-powered system.</p>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# Registration page (placeholder)
def registration_page():
    st.title("Registration Page")
    st.write("Registration functionality coming soon!")

# Admin panel (placeholder)
def admin_panel():
    st.title("Admin Panel")
    st.write("Admin functionality placeholder")

# User dashboard (placeholder)
def user_dashboard():
    if 'user' not in st.session_state:
        st.error("Please login to access your dashboard.")
        return
    
    user = st.session_state.user
    st.title("User Dashboard")
    st.write(f"Welcome, {user['username']}!")
