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

# Admin functions
def get_all_users():
    conn = sqlite3.connect('users.db')
    df = pd.read_sql_query("""
        SELECT id, username, email, role, created_at
        FROM users
        WHERE role != 'admin'
        ORDER BY created_at DESC
    """, conn)
    conn.close()
    return df

def get_all_predictions():
    conn = sqlite3.connect('users.db')
    df = pd.read_sql_query("""
        SELECT p.*, u.username
        FROM predictions p
        JOIN users u ON p.user_id = u.id
        ORDER BY p.created_at DESC
    """, conn)
    conn.close()
    return df

def delete_user(user_id):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("DELETE FROM predictions WHERE user_id = ?", (user_id,))
    c.execute("DELETE FROM users WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()

# Initialize the database
init_db()

# Login UI
def login_page():
    st.title("Login")
    
    # Initialize session state variables for login if they don't exist
    if 'login_username' not in st.session_state:
        st.session_state.login_username = ""
    if 'login_password' not in st.session_state:
        st.session_state.login_password = ""
    
    # Create a form for login
    with st.form("login_form", clear_on_submit=False):
        # Use session state to store input values
        username = st.text_input(
            "Username", 
            value=st.session_state.login_username,
            key="login_username_input"
        )
        password = st.text_input(
            "Password", 
            value=st.session_state.login_password,
            type="password",
            key="login_password_input"
        )
        
        # Update session state when form is submitted
        st.session_state.login_username = username
        st.session_state.login_password = password
        
        submitted = st.form_submit_button("Login")
        
        if submitted:
            if username and password:  # Check if fields are not empty
                user = authenticate_user(username, password)
                if user:
                    st.session_state['user'] = user
                    # Clear login credentials from session state for security
                    st.session_state.login_username = ""
                    st.session_state.login_password = ""
                    st.success(f"Welcome back, {username}!")
                    st.rerun()
                else:
                    st.error("Invalid username or password")
            else:
                st.warning("Please enter both username and password")
    
    # Add a note about the default admin account
    st.info("Default admin account: Username: admin, Password: admin123")

# Registration UI
def registration_page():
    st.title("Register")
    
    # Initialize session state variables for registration if they don't exist
    if 'reg_username' not in st.session_state:
        st.session_state.reg_username = ""
    if 'reg_email' not in st.session_state:
        st.session_state.reg_email = ""
    if 'reg_password' not in st.session_state:
        st.session_state.reg_password = ""
    if 'reg_confirm_password' not in st.session_state:
        st.session_state.reg_confirm_password = ""
    
    # Create a form for registration
    with st.form("registration_form", clear_on_submit=False):
        # Use session state to store input values
        username = st.text_input(
            "Username", 
            value=st.session_state.reg_username,
            key="reg_username_input"
        )
        email = st.text_input(
            "Email", 
            value=st.session_state.reg_email,
            key="reg_email_input"
        )
        password = st.text_input(
            "Password", 
            value=st.session_state.reg_password,
            type="password",
            key="reg_password_input"
        )
        confirm_password = st.text_input(
            "Confirm Password", 
            value=st.session_state.reg_confirm_password,
            type="password",
            key="reg_confirm_password_input"
        )
        
        # Update session state when form is submitted
        st.session_state.reg_username = username
        st.session_state.reg_email = email
        st.session_state.reg_password = password
        st.session_state.reg_confirm_password = confirm_password
        
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
                    # Clear registration data from session state for security
                    st.session_state.reg_username = ""
                    st.session_state.reg_email = ""
                    st.session_state.reg_password = ""
                    st.session_state.reg_confirm_password = ""
                    st.success("Registration successful! Please login.")
                    st.session_state['show_registration'] = False
                    st.rerun()
                else:
                    st.error("Username or email already exists")

# Admin Panel UI
def admin_panel():
    st.title("Admin Panel")
    
    # Sidebar for admin navigation
    admin_choice = st.sidebar.radio(
        "Admin Menu",
        ["User Management", "Prediction History", "System Statistics"]
    )
    
    if admin_choice == "User Management":
        st.subheader("User Management")
        users_df = get_all_users()
        st.dataframe(users_df)
        
        # User deletion
        user_to_delete = st.selectbox("Select user to delete", users_df['username'].tolist())
        if st.button("Delete User"):
            user_id = users_df[users_df['username'] == user_to_delete]['id'].iloc[0]
            delete_user(user_id)
            st.success(f"User {user_to_delete} deleted successfully")
            st.rerun()
    
    elif admin_choice == "Prediction History":
        st.subheader("All Predictions")
        predictions_df = get_all_predictions()
        st.dataframe(predictions_df)
        
        # Download predictions
        if not predictions_df.empty:
            csv = predictions_df.to_csv(index=False)
            st.download_button(
                "Download Predictions CSV",
                csv,
                "predictions.csv",
                "text/csv",
                key='download-csv'
            )
    
    elif admin_choice == "System Statistics":
        st.subheader("System Statistics")
        
        # Get statistics
        users_df = get_all_users()
        predictions_df = get_all_predictions()
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Users", len(users_df))
        
        with col2:
            st.metric("Total Predictions", len(predictions_df))
        
        with col3:
            if not predictions_df.empty:
                avg_confidence = predictions_df['confidence'].mean()
                st.metric("Avg. Confidence", f"{avg_confidence:.2f}%")
        
        # Show predictions by disease type
        if not predictions_df.empty:
            st.subheader("Predictions by Disease Type")
            disease_counts = predictions_df['disease_type'].value_counts()
            st.bar_chart(disease_counts)

# User Dashboard UI
def user_dashboard(user):
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
            try:
                st.dataframe(predictions_df)
            except Exception as e:
                # Fallback to a simpler display method
                st.write("Your predictions:")
                for _, row in predictions_df.iterrows():
                    st.write(f"Disease: {row['Disease Type']}")
                    st.write(f"Prediction: {row['Prediction']}")
                    st.write(f"Confidence: {row['Confidence']:.2f}%")
                    st.write(f"Date: {row['Date']}")
                    st.write("---")
        except Exception as e:
            st.error("Error displaying prediction history. Please try refreshing the page.")
            print(f"Error in user_dashboard: {e}")
    else:
        st.info("You haven't made any predictions yet. Try out our disease prediction tools!")

# Logout function
def logout():
    st.session_state.pop('user', None)
    st.rerun() 