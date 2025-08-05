import streamlit as st
from auth import app_controller, init_db

# Configure Streamlit page
st.set_page_config(
    page_title="Health AI - Disease Prediction System",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="auto"
)

# Initialize database
init_db()

# Main application entry point
if __name__ == "__main__":
    # Run the app controller which handles login/main app routing
    app_controller()
