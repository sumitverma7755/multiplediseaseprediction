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
            email TEXT DEFAULT '',
            role TEXT DEFAULT 'user',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    c.execute("PRAGMA table_info(users)")
    existing_columns = {row[1] for row in c.fetchall()}
    if 'email' not in existing_columns:
        c.execute("ALTER TABLE users ADD COLUMN email TEXT DEFAULT ''")
    if 'role' not in existing_columns:
        c.execute("ALTER TABLE users ADD COLUMN role TEXT DEFAULT 'user'")
    if 'created_at' not in existing_columns:
        c.execute("ALTER TABLE users ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
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

def _get_prediction_schema(conn):
    """Return available predictions table columns and compatible field mapping."""
    c = conn.cursor()
    c.execute("PRAGMA table_info(predictions)")
    columns = {row[1] for row in c.fetchall()}

    type_col = 'prediction_type' if 'prediction_type' in columns else (
        'disease_type' if 'disease_type' in columns else None
    )
    result_col = 'result' if 'result' in columns else (
        'prediction_result' if 'prediction_result' in columns else None
    )
    input_col = 'input_data' if 'input_data' in columns else None
    confidence_col = 'confidence' if 'confidence' in columns else None
    created_at_col = 'created_at' if 'created_at' in columns else None

    return {
        'columns': columns,
        'type_col': type_col,
        'result_col': result_col,
        'input_col': input_col,
        'confidence_col': confidence_col,
        'created_at_col': created_at_col,
    }

def _get_user_schema(conn):
    """Return available users table columns."""
    c = conn.cursor()
    c.execute("PRAGMA table_info(users)")
    columns = {row[1] for row in c.fetchall()}
    return {'columns': columns}

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
        user_schema = _get_user_schema(conn)
        admin_password = hash_password('admin123')
        insert_columns = ['username', 'password']
        insert_values = ['admin', admin_password]

        if 'email' in user_schema['columns']:
            insert_columns.append('email')
            insert_values.append('admin@local')

        if 'role' in user_schema['columns']:
            insert_columns.append('role')
            insert_values.append('admin')

        placeholders = ", ".join(["?"] * len(insert_values))
        columns_sql = ", ".join(insert_columns)
        c.execute(f"INSERT INTO users ({columns_sql}) VALUES ({placeholders})", insert_values)
        conn.commit()
    
    conn.close()

def authenticate_user(username, password):
    """Authenticate user login"""
    create_user_table()
    create_admin_user()
    
    conn = sqlite3.connect('users.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    hashed_password = hash_password(password)
    c.execute("SELECT * FROM users WHERE username = ? AND password = ?", 
             (username, hashed_password))
    user = c.fetchone()
    conn.close()
    
    if user:
        return {
            'id': user['id'],
            'username': user['username'],
            'role': user['role'] if 'role' in user.keys() else 'user'
        }
    return None

def register_user(username, password, role='user', email=None):
    """Register a new user"""
    create_user_table()
    
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    
    try:
        if email is None and isinstance(role, str) and "@" in role:
            email = role
            role = 'user'

        hashed_password = hash_password(password)
        user_schema = _get_user_schema(conn)

        insert_columns = ['username', 'password']
        insert_values = [username, hashed_password]

        if 'email' in user_schema['columns']:
            normalized_email = (email or "").strip()
            if not normalized_email:
                normalized_email = f"{username}@local"
            insert_columns.append('email')
            insert_values.append(normalized_email)

        if 'role' in user_schema['columns']:
            insert_columns.append('role')
            insert_values.append(role)

        placeholders = ", ".join(["?"] * len(insert_values))
        columns_sql = ", ".join(insert_columns)
        c.execute(f"INSERT INTO users ({columns_sql}) VALUES ({placeholders})", insert_values)
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

    schema = _get_prediction_schema(conn)
    type_col = schema['type_col']
    result_col = schema['result_col']

    if not type_col or not result_col:
        conn.close()
        return

    insert_columns = ['user_id', type_col]
    insert_values = [user_id, prediction_type]

    if schema['input_col']:
        insert_columns.append(schema['input_col'])
        insert_values.append(str(input_data))

    insert_columns.append(result_col)
    insert_values.append(result)

    if schema['confidence_col']:
        insert_columns.append(schema['confidence_col'])
        insert_values.append(confidence)

    placeholders = ", ".join(["?"] * len(insert_values))
    columns_sql = ", ".join(insert_columns)
    c.execute(f"INSERT INTO predictions ({columns_sql}) VALUES ({placeholders})", insert_values)
    conn.commit()
    conn.close()

def get_user_predictions(user_id):
    """Get user's prediction history"""
    create_prediction_table()
    
    conn = sqlite3.connect('users.db')
    schema = _get_prediction_schema(conn)

    if not schema['type_col'] or not schema['result_col']:
        conn.close()
        return pd.DataFrame(columns=['prediction_type', 'result', 'confidence', 'created_at'])

    confidence_select = f"{schema['confidence_col']} AS confidence" if schema['confidence_col'] else "NULL AS confidence"
    created_at_select = f"{schema['created_at_col']} AS created_at" if schema['created_at_col'] else "NULL AS created_at"
    order_clause = "ORDER BY created_at DESC" if schema['created_at_col'] else ""

    query = f"""
        SELECT
            {schema['type_col']} AS prediction_type,
            {schema['result_col']} AS result,
            {confidence_select},
            {created_at_select}
        FROM predictions
        WHERE user_id = ?
        {order_clause}
    """
    df = pd.read_sql_query(query, conn, params=(user_id,))
    conn.close()
    return df

def logout():
    """Logout user"""
    for key in ['logged_in', 'user', 'show_registration']:
        if key in st.session_state:
            del st.session_state[key]
    st.rerun()

# Modern login and registration UI
def login_page():
    """Render authentication page with sign-in and self-registration."""
    init_database()

    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False
    if 'user' not in st.session_state:
        st.session_state['user'] = None
    if 'auth_view' not in st.session_state:
        st.session_state['auth_view'] = "Sign in"

    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@600;700;800&display=swap');
        @import url('https://fonts.googleapis.com/css2?family=Source+Sans+3:wght@400;500;600;700&display=swap');

        :root {
            --auth-ink: #0f172a;
            --auth-muted: #5f6c7b;
            --auth-line: rgba(148, 163, 184, 0.22);
            --auth-soft: rgba(255, 255, 255, 0.84);
            --auth-accent: #0f766e;
            --auth-accent-2: #2563eb;
            --auth-deep: #0d2438;
            --auth-deep-2: #16344d;
        }

        html, body, [class*="css"] {
            font-family: 'Source Sans 3', 'Segoe UI', sans-serif;
        }

        [data-testid="stSidebar"], [data-testid="collapsedControl"] {
            display: none !important;
        }

        [data-testid="stHeader"] {
            background: transparent !important;
        }

        .stApp {
            background:
                radial-gradient(circle at 8% 12%, rgba(15, 118, 110, 0.14), transparent 24%),
                radial-gradient(circle at 92% 10%, rgba(37, 99, 235, 0.14), transparent 22%),
                linear-gradient(145deg, #eff7f5 0%, #f8fbff 52%, #eef3fb 100%);
        }

        .main .block-container {
            max-width: 1180px;
            padding: 1.45rem 1.15rem 1.4rem;
        }

        .auth-kicker {
            display: inline-flex;
            align-items: center;
            gap: 0.45rem;
            padding: 0.45rem 0.82rem;
            border-radius: 999px;
            background: var(--auth-soft);
            border: 1px solid var(--auth-line);
            color: var(--auth-accent);
            font-size: 0.78rem;
            font-weight: 700;
            letter-spacing: 0.08em;
            text-transform: uppercase;
        }

        .auth-kicker::before {
            content: "";
            width: 0.48rem;
            height: 0.48rem;
            border-radius: 999px;
            background: linear-gradient(135deg, var(--auth-accent), #14b8a6);
            box-shadow: 0 0 0 5px rgba(20, 184, 166, 0.12);
        }

        .auth-stage {
            margin-bottom: 1rem;
        }

        .auth-title {
            margin: 0.9rem 0 0.3rem;
            color: var(--auth-ink);
            font-family: 'Plus Jakarta Sans', 'Segoe UI', sans-serif;
            font-size: clamp(1.15rem, 2vw, 1.5rem);
            font-weight: 700;
            letter-spacing: -0.03em;
        }

        .auth-subtitle {
            max-width: 640px;
            margin: 0;
            color: var(--auth-muted);
            font-size: 1rem;
            line-height: 1.65;
        }

        .auth-hero {
            position: relative;
            overflow: hidden;
            min-height: 100%;
            padding: 2rem;
            border-radius: 32px;
            background:
                radial-gradient(circle at top left, rgba(94, 234, 212, 0.18), transparent 24%),
                linear-gradient(160deg, var(--auth-deep) 0%, var(--auth-deep-2) 55%, #091a2b 100%);
            color: #f8fbff;
            box-shadow: 0 30px 70px rgba(15, 23, 42, 0.18);
        }

        .auth-hero::after {
            content: "";
            position: absolute;
            right: -70px;
            bottom: -90px;
            width: 220px;
            height: 220px;
            border-radius: 999px;
            background: radial-gradient(circle, rgba(59, 130, 246, 0.28), transparent 68%);
        }

        .auth-hero-badge {
            display: inline-flex;
            align-items: center;
            padding: 0.4rem 0.8rem;
            border-radius: 999px;
            background: rgba(255, 255, 255, 0.12);
            border: 1px solid rgba(255, 255, 255, 0.14);
            color: #d7f6ee;
            font-size: 0.78rem;
            font-weight: 700;
            letter-spacing: 0.08em;
            text-transform: uppercase;
        }

        .auth-hero h2,
        .auth-card h3 {
            margin: 0;
            font-family: 'Plus Jakarta Sans', 'Segoe UI', sans-serif;
            letter-spacing: -0.04em;
        }

        .auth-hero h2 {
            margin-top: 1rem;
            color: #ffffff !important;
            font-size: clamp(2rem, 3.3vw, 3.2rem);
            line-height: 1.02;
            max-width: 630px;
        }

        .auth-hero-copy {
            margin: 1rem 0 0;
            max-width: 620px;
            color: rgba(239, 246, 255, 0.82) !important;
            font-size: 1.02rem;
            line-height: 1.72;
        }

        .auth-module-grid {
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: 0.9rem;
            margin: 1.6rem 0 1.2rem;
        }

        .auth-module-card {
            padding: 1rem;
            border-radius: 20px;
            background: rgba(255, 255, 255, 0.08);
            border: 1px solid rgba(255, 255, 255, 0.12);
            backdrop-filter: blur(12px);
        }

        .auth-module-card strong {
            display: block;
            color: #b8e5ff !important;
            font-size: 0.76rem;
            font-weight: 700;
            letter-spacing: 0.08em;
            text-transform: uppercase;
        }

        .auth-module-card span {
            display: block;
            margin-top: 0.5rem;
            color: #ffffff !important;
            font-family: 'Plus Jakarta Sans', 'Segoe UI', sans-serif;
            font-size: 1.15rem;
            font-weight: 700;
        }

        .auth-module-card p {
            margin: 0.45rem 0 0 !important;
            color: rgba(239, 246, 255, 0.74) !important;
            font-size: 0.92rem !important;
            line-height: 1.5 !important;
        }

        .auth-trust {
            display: grid;
            gap: 0.75rem;
        }

        .auth-trust-item {
            padding: 0.95rem 1rem;
            border-radius: 18px;
            background: rgba(9, 26, 43, 0.26);
            border: 1px solid rgba(255, 255, 255, 0.08);
            color: rgba(239, 246, 255, 0.86) !important;
            font-size: 0.98rem;
            line-height: 1.55;
        }

        .auth-note {
            margin-top: 1.25rem;
            padding: 1rem 1.05rem;
            border-radius: 18px;
            background: rgba(245, 158, 11, 0.10);
            border: 1px solid rgba(245, 158, 11, 0.22);
            color: #ffe5b3 !important;
            font-size: 0.95rem;
            line-height: 1.58;
        }

        .auth-card {
            margin-bottom: 1rem;
            padding: 1.25rem 1.2rem;
            border-radius: 28px;
            background: rgba(255, 255, 255, 0.92);
            border: 1px solid var(--auth-line);
            box-shadow: 0 24px 64px rgba(15, 23, 42, 0.10);
        }

        .auth-card-badge {
            display: inline-flex;
            align-items: center;
            padding: 0.36rem 0.72rem;
            border-radius: 999px;
            background: #f3fbf8;
            border: 1px solid rgba(15, 118, 110, 0.16);
            color: var(--auth-accent);
            font-size: 0.76rem;
            font-weight: 700;
            letter-spacing: 0.08em;
            text-transform: uppercase;
        }

        .auth-card h3 {
            margin-top: 0.95rem;
            color: var(--auth-ink) !important;
            font-size: 2rem;
            line-height: 1.05;
        }

        .auth-card p {
            margin: 0.6rem 0 0 !important;
            color: var(--auth-muted) !important;
            font-size: 1rem !important;
            line-height: 1.6 !important;
        }

        div[data-baseweb="radio"] > div {
            margin-bottom: 1rem;
            padding: 0.34rem;
            border-radius: 999px;
            border: 1px solid var(--auth-line);
            background: rgba(255, 255, 255, 0.86);
            box-shadow: 0 12px 28px rgba(15, 23, 42, 0.05);
        }

        .stRadio label {
            border-radius: 999px !important;
            color: #244052 !important;
            font-weight: 700 !important;
        }

        [data-testid="stForm"] {
            padding: 1.45rem 1.25rem 1.2rem;
            border-radius: 28px;
            border: 1px solid rgba(148, 163, 184, 0.20);
            background: rgba(255, 255, 255, 0.95);
            box-shadow: 0 28px 72px rgba(15, 23, 42, 0.12);
        }

        .stTextInput label p,
        .stCheckbox label p {
            color: #415162 !important;
            font-size: 0.78rem !important;
            font-weight: 700 !important;
            letter-spacing: 0.09em;
            text-transform: uppercase;
        }

        .stTextInput > div > div > input {
            min-height: 3.15rem;
            border: 1px solid #d6e1ea !important;
            border-radius: 18px !important;
            padding: 0.82rem 1rem !important;
            background: #fbfcfe !important;
            color: #102033 !important;
            font-size: 1rem !important;
        }

        .stTextInput > div > div > input::placeholder {
            color: #91a0b0 !important;
        }

        .stTextInput > div > div > input:focus {
            border-color: rgba(15, 118, 110, 0.75) !important;
            box-shadow: 0 0 0 4px rgba(15, 118, 110, 0.10) !important;
            background: #ffffff !important;
        }

        .auth-inline {
            margin-top: 0.25rem;
            padding: 0.9rem 1rem;
            border-radius: 18px;
            background: linear-gradient(135deg, #f3faf8 0%, #eef4ff 100%);
            border: 1px solid rgba(15, 118, 110, 0.12);
            color: #21504b;
            font-size: 0.94rem;
            line-height: 1.55;
        }

        .auth-demo {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 0.8rem;
            margin: 0.9rem 0 0.15rem;
            padding: 0.9rem 1rem;
            border-radius: 18px;
            background: rgba(15, 118, 110, 0.05);
            border: 1px solid rgba(15, 118, 110, 0.12);
        }

        .auth-demo strong {
            color: var(--auth-ink) !important;
            font-size: 0.92rem;
            font-weight: 700;
        }

        .auth-demo-code {
            display: inline-flex;
            align-items: center;
            padding: 0.34rem 0.65rem;
            border-radius: 999px;
            background: #ffffff;
            border: 1px solid rgba(15, 23, 42, 0.08);
            color: var(--auth-accent) !important;
            font-family: 'Plus Jakarta Sans', 'Segoe UI', sans-serif;
            font-size: 0.86rem;
            font-weight: 700;
        }

        .stFormSubmitButton > button,
        .stButton > button {
            min-height: 3.15rem !important;
            border: none !important;
            border-radius: 18px !important;
            background: linear-gradient(135deg, #0f766e 0%, #2563eb 100%) !important;
            color: #ffffff !important;
            font-size: 1rem !important;
            font-weight: 700 !important;
            box-shadow: 0 18px 36px rgba(37, 99, 235, 0.18) !important;
        }

        [data-testid="stAlert"] {
            border-radius: 18px;
            border: 1px solid rgba(148, 163, 184, 0.18);
            background: rgba(255, 255, 255, 0.96);
        }

        [data-testid="stCaptionContainer"] p {
            color: #677483 !important;
            font-size: 0.93rem !important;
            line-height: 1.55 !important;
        }

        @media (max-width: 980px) {
            .auth-module-grid {
                grid-template-columns: 1fr;
            }
        }

        @media (max-width: 640px) {
            .main .block-container {
                padding-left: 0.8rem;
                padding-right: 0.8rem;
            }

            .auth-hero,
            .auth-card,
            [data-testid="stForm"] {
                border-radius: 24px;
            }

            .auth-demo {
                flex-direction: column;
                align-items: flex-start;
            }
        }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <section class="auth-stage">
        <span class="auth-kicker">Health AI Studio</span>
        <h1 class="auth-title">Secure sign-in for screening modules, saved assessments, and account-linked history.</h1>
        <p class="auth-subtitle">
            Access a single workspace for diabetes, heart, and Parkinson's disease screening with a cleaner,
            more focused login flow.
        </p>
    </section>
    """, unsafe_allow_html=True)

    info_col, form_col = st.columns([1.08, 0.92], gap="large")

    with info_col:
        st.markdown(
            """<section class="auth-hero">
<span class="auth-hero-badge">Clinical Intelligence Workspace</span>
<h2>Predict earlier. Review clearly. Keep every assessment connected.</h2>
<p class="auth-hero-copy">
Move from guided screening inputs to saved results without losing session continuity across modules or users.
</p>
<div class="auth-module-grid">
    <article class="auth-module-card">
        <strong>Module 01</strong>
        <span>Diabetes</span>
        <p>Metabolic risk screening with account-linked session history.</p>
    </article>
    <article class="auth-module-card">
        <strong>Module 02</strong>
        <span>Heart</span>
        <p>Cardiovascular assessment with confidence scoring and saved output.</p>
    </article>
    <article class="auth-module-card">
        <strong>Module 03</strong>
        <span>Parkinson's</span>
        <p>Voice-based analysis organized under the same protected workspace.</p>
    </article>
</div>
<div class="auth-trust">
    <div class="auth-trust-item">Account-linked prediction history for every screening session.</div>
    <div class="auth-trust-item">Unified access for both admin and standard users without switching workflows.</div>
    <div class="auth-trust-item">Designed to present model results in a clearer, more professional way.</div>
</div>
<div class="auth-note">
    This platform supports screening and education only. Final diagnosis must come from licensed medical professionals.
</div>
</section>""",
            unsafe_allow_html=True
        )

    with form_col:
        st.radio(
            "Account flow",
            options=["Sign in", "Create account"],
            horizontal=True,
            key="auth_view",
            label_visibility="collapsed"
        )

        current_view = st.session_state["auth_view"]

        if current_view == "Sign in":
            st.markdown("""
            <div class="auth-card">
                <span class="auth-card-badge">Workspace access</span>
                <h3>Continue to your workspace</h3>
                <p>Open the dashboard, prediction history, and saved screening sessions with one secure login.</p>
            </div>
            """, unsafe_allow_html=True)

            with st.form("login_form", clear_on_submit=False):
                username = st.text_input(
                    "Username",
                    placeholder="Enter your username",
                    key="login_username_input"
                )
                password = st.text_input(
                    "Password",
                    placeholder="Enter your password",
                    type="password",
                    key="login_password_input"
                )
                remember_col, note_col = st.columns([1.15, 1], gap="small")
                with remember_col:
                    remember_me = st.checkbox(
                        "Keep me signed in on this browser",
                        key="remember_checkbox"
                    )
                with note_col:
                    st.markdown(
                        '<div class="auth-inline">Protected local session state with account-linked prediction history.</div>',
                        unsafe_allow_html=True
                    )
                submitted = st.form_submit_button("Sign in", use_container_width=True)

            st.markdown(
                '<div class="auth-demo"><strong>Demo access</strong><span class="auth-demo-code">admin / admin123</span></div>',
                unsafe_allow_html=True
            )
            st.caption("Need account help? Contact the system administrator.")

            if submitted:
                cleaned_username = username.strip()
                if not cleaned_username or not password:
                    st.warning("Please enter both username and password.")
                else:
                    user = authenticate_user(cleaned_username, password)
                    if user:
                        st.session_state['user'] = user
                        st.session_state['logged_in'] = True
                        st.session_state['remember_me'] = bool(remember_me)
                        st.success("Login successful. Redirecting...")
                        time.sleep(0.6)
                        st.rerun()
                    else:
                        st.error("Invalid username or password.")
        else:
            st.markdown("""
            <div class="auth-card">
                <span class="auth-card-badge">New account</span>
                <h3>Set up a new workspace profile</h3>
                <p>Create a standard user account so future screening activity stays tied to one dedicated login.</p>
            </div>
            """, unsafe_allow_html=True)

            with st.form("register_form", clear_on_submit=False):
                new_username = st.text_input(
                    "Username",
                    placeholder="Choose a username",
                    key="register_username_input"
                )
                new_email = st.text_input(
                    "Email (optional)",
                    placeholder="you@example.com",
                    key="register_email_input"
                )
                new_password = st.text_input(
                    "Password",
                    placeholder="Create a password (8+ characters)",
                    type="password",
                    key="register_password_input"
                )
                confirm_password = st.text_input(
                    "Confirm password",
                    placeholder="Re-enter password",
                    type="password",
                    key="register_confirm_password_input"
                )
                st.markdown(
                    '<div class="auth-inline">Usernames must be unique. Passwords must be at least 8 characters long.</div>',
                    unsafe_allow_html=True
                )
                register_submitted = st.form_submit_button("Create account", use_container_width=True)

            st.caption("After registration, switch back to Sign in to open the dashboard.")

            if register_submitted:
                cleaned_username = new_username.strip()
                if not cleaned_username:
                    st.warning("Username is required.")
                elif len(cleaned_username) < 3:
                    st.warning("Username must be at least 3 characters.")
                elif " " in cleaned_username:
                    st.warning("Username cannot contain spaces.")
                elif len(new_password) < 8:
                    st.warning("Password must be at least 8 characters.")
                elif new_password != confirm_password:
                    st.warning("Passwords do not match.")
                else:
                    cleaned_email = new_email.strip() if new_email else None
                    if cleaned_email and "@" not in cleaned_email:
                        st.warning("Please enter a valid email address.")
                        return

                    registered = register_user(cleaned_username, new_password, email=cleaned_email)
                    if registered:
                        st.success("Account created successfully. Switch to Sign in and continue.")
                        st.session_state["auth_view"] = "Sign in"
                        st.session_state["register_username_input"] = ""
                        st.session_state["register_email_input"] = ""
                        st.session_state["register_password_input"] = ""
                        st.session_state["register_confirm_password_input"] = ""
                        st.rerun()
                    else:
                        st.error("This username already exists. Please choose another one.")

# Registration page (placeholder)
def registration_page():
    st.session_state['auth_view'] = "Create account"
    login_page()

# Admin panel (placeholder)
def admin_panel():
    st.title("Admin Panel")
    st.write("Admin functionality placeholder")

# User dashboard (placeholder)
def user_dashboard():
    if 'user' not in st.session_state:
        st.error("Please login to access your dashboard.")
        return
    
    user = st.session_state.get('user', {})
    st.title("User Dashboard")
    st.write(f"Welcome, {user.get('username', 'User')}!")

