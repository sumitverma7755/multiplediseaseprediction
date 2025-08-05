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

# Login UI
def login_page():
    st.title("Login")
    
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")
        
        if submitted:
            if username and password:
                user = authenticate_user(username, password)
                if user:
                    st.session_state['user'] = user
                    st.success(f"Welcome back, {username}!")
                    st.rerun()
                else:
                    st.error("Invalid username or password")
            else:
                st.warning("Please enter both username and password")
    
    st.info("Default admin account: Username: admin, Password: admin123")

# Registration UI
def registration_page():
    st.title("Register")
    
    with st.form("registration_form"):
        username = st.text_input("Username")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")
        
        submitted = st.form_submit_button("Register")
        
        if submitted:
            if not username or not email or not password or not confirm_password:
                st.warning("Please fill in all fields")
            elif password != confirm_password:
                st.error("Passwords do not match")
            elif len(password) < 6:
                st.error("Password must be at least 6 characters long")
            else:
                if register_user(username, password, email):
                    st.success("Registration successful! Please login.")
                    st.session_state['show_registration'] = False
                    st.rerun()
                else:
                    st.error("Username or email already exists")

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
