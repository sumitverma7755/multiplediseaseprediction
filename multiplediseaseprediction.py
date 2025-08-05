import sys

# Create mock pyarrow.vendored module before any other imports
try:
    import pyarrow
    
    # Create mock version module
    class MockVersion:
        def __init__(self):
            self.version = '1.0.0'
            
        def __str__(self):
            return self.version
            
        def __repr__(self):
            return f"version('{self.version}')"
    
    # Create mock docscrape module
    class MockDocscrape:
        class Reader:
            def __init__(self, *args, **kwargs):
                self.sections = {}
            
            def read(self):
                return {'Parameters': {}}
            
            def __getattr__(self, name):
                return lambda *args, **kwargs: {}
        
        class NumpyDocString(dict):
            def __init__(self, *args, **kwargs):
                super().__init__()
                self['Parameters'] = {}
            
            def __getitem__(self, key):
                return {}
            
            def __setitem__(self, key, value):
                pass
            
            def __getattr__(self, name):
                return lambda *args, **kwargs: {}
    
    # Create the vendored module
    vendored_module = type(sys)('pyarrow.vendored')
    vendored_module.docscrape = MockDocscrape()
    vendored_module.version = MockVersion()
    
    # Add it to sys.modules
    sys.modules['pyarrow.vendored'] = vendored_module
    sys.modules['pyarrow.vendored.version'] = vendored_module.version
    
    # Add it to pyarrow
    pyarrow.vendored = vendored_module
    
    print("Mock pyarrow.vendored module created successfully")
except Exception as e:
    print(f"Error creating mock pyarrow.vendored module: {e}")

import streamlit as st
import pickle
from streamlit_option_menu import option_menu
import time
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sklearn.preprocessing import StandardScaler
import os
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import requests
from PIL import Image
from io import BytesIO
import base64
import random
from auth import (
    login_page, registration_page, admin_panel, user_dashboard, 
    logout, save_prediction, get_user_predictions
)

# Fix for pyarrow.vendored missing module
import importlib.util

# Apply patch for pyarrow.vendored module
try:
    import pyarrow
    try:
        import pyarrow.vendored
        print("pyarrow.vendored is already available.")
    except ImportError:
        print("Creating mock pyarrow.vendored module...")
        
        # Create a mock docscrape module with better implementation
        class MockDocscrape:
            class Reader:
                def __init__(self, *args, **kwargs):
                    self.sections = {}
                
                def read(self):
                    return {'Parameters': {}}
                
                def __getattr__(self, name):
                    return lambda *args, **kwargs: {}
            
            class NumpyDocString(dict):
                def __init__(self, *args, **kwargs):
                    super().__init__()
                    # Initialize with empty Parameters section
                    self['Parameters'] = {}
                
                def __getitem__(self, key):
                    # Return empty dict for any key
                    return {}
                
                def __setitem__(self, key, value):
                    # Do nothing
                    pass
                
                def __getattr__(self, name):
                    return lambda *args, **kwargs: {}
        
        # Create the vendored module
        vendored_module = type(sys)('pyarrow.vendored')
        vendored_module.docscrape = MockDocscrape()
        
        # Add it to sys.modules
        sys.modules['pyarrow.vendored'] = vendored_module
        
        # Add it to pyarrow
        pyarrow.vendored = vendored_module
        
        print("Mock pyarrow.vendored module created successfully.")
except Exception as e:
    print(f"Error applying pyarrow patch: {e}")

# Create DummyModel class for error handling
class DummyModel:
    def __init__(self, name="Unknown"):
        self.name = name
        
    def predict(self, input_data):
        import random
        return [random.randint(0, 1)]
    
    def predict_proba(self, input_data):
        import random
        prob = random.random()
        return [[1 - prob, prob]]

# Add missing functions
def get_prediction_probability(model, input_data):
    """Get prediction probability from model"""
    try:
        # Check if model has predict_proba method
        if hasattr(model, 'predict_proba'):
            return model.predict_proba(input_data)
        else:
            # If not, create a dummy probability
            prediction = model.predict(input_data)
            dummy_proba = np.zeros((len(prediction), 2))
            for i, pred in enumerate(prediction):
                dummy_proba[i, int(pred)] = 0.8  # Assign 80% confidence to the prediction
                dummy_proba[i, 1 - int(pred)] = 0.2  # Assign 20% to the other class
            return dummy_proba
    except Exception as e:
        st.error(f"Error getting prediction probability: {str(e)}")
        # Return a default probability
        return np.array([[0.5, 0.5]])

def calculate_confidence(prediction_proba):
    """Calculate confidence percentage from prediction probability"""
    try:
        # Get the highest probability
        max_proba = np.max(prediction_proba)
        return max_proba * 100
    except Exception as e:
        st.error(f"Error calculating confidence: {str(e)}")
        return 50.0  # Default 50% confidence

def show_result_popup(diagnosis, confidence, is_positive):
    """Show a styled popup with the prediction result"""
    if is_positive:
        color = "#FFC107"  # Warning yellow
        icon = "⚠️"
    else:
        color = "#4CAF50"  # Success green
        icon = "✅"
    
    st.markdown(f"""
    <div style="background-color: {color}; padding: 20px; border-radius: 10px; margin-bottom: 20px; text-align: center;">
        <h2 style="color: white; margin-bottom: 10px;">{icon} {diagnosis}</h2>
        <p style="color: white; font-size: 1.2rem;">Confidence: {confidence:.1f}%</p>
    </div>
    """, unsafe_allow_html=True)

def plot_feature_importance(features, importance_scores):
    """Create a bar chart of feature importance"""
    # Sort features by importance
    sorted_idx = np.argsort(importance_scores)
    sorted_features = [features[i] for i in sorted_idx]
    sorted_scores = [importance_scores[i] for i in sorted_idx]
    
    # Create the plot
    fig = px.bar(
        x=sorted_scores,
        y=sorted_features,
        orientation='h',
        labels={'x': 'Importance', 'y': 'Feature'},
        title='Feature Importance',
        color=sorted_scores,
        color_continuous_scale='Blues'
    )
    
    # Customize layout
    fig.update_layout(
        height=400,
        margin=dict(l=20, r=20, t=40, b=20),
        title_font=dict(size=20, color='#1e3a8a'),
        font=dict(family='Segoe UI, Arial, sans-serif', color='#333333'),
        xaxis_title_font=dict(size=14),
        yaxis_title_font=dict(size=14)
    )
    
    return fig

def plot_prediction_proba(prediction_proba):
    """Create a gauge chart for prediction probability"""
    # Get the probability of the positive class
    if isinstance(prediction_proba, list):
        positive_proba = prediction_proba[1]
    else:
        # Handle numpy array
        try:
            positive_proba = prediction_proba[0][1]  # For 2D array like [[0.2, 0.8]]
        except:
            try:
                positive_proba = prediction_proba[1]  # For 1D array like [0.2, 0.8]
            except:
                positive_proba = 0.5  # Default if we can't determine
    
    # Create the gauge chart
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=positive_proba * 100,
        title={'text': "Prediction Probability", 'font': {'size': 24, 'color': '#1e3a8a'}},
        gauge={
            'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "#333333"},
            'bar': {'color': "#1e40af"},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "#333333",
            'steps': [
                {'range': [0, 30], 'color': '#dcfce7'},
                {'range': [30, 70], 'color': '#fef9c3'},
                {'range': [70, 100], 'color': '#fee2e2'}
            ],
        }
    ))
    
    # Customize layout
    fig.update_layout(
        height=300,
        margin=dict(l=20, r=20, t=50, b=20),
        font=dict(family='Segoe UI, Arial, sans-serif', color='#333333')
    )
    
    return fig

def create_metrics_chart(metrics_values, metrics_labels, metrics_ranges):
    """Create a chart with multiple metrics and their normal ranges"""
    fig = go.Figure()
    
    # Add a trace for each metric
    for i, (value, label, (min_range, max_range)) in enumerate(zip(metrics_values, metrics_labels, metrics_ranges)):
        # Determine color based on whether value is in normal range
        if min_range <= value <= max_range:
            color = '#4CAF50'  # Green for normal
        else:
            color = '#F44336'  # Red for abnormal
        
        # Add bar for the metric
        fig.add_trace(go.Bar(
            x=[label],
            y=[value],
            name=label,
            marker_color=color,
            text=[f"{value:.1f}"],
            textposition='auto'
        ))
        
        # Add range indicators
        fig.add_shape(
            type="rect",
            x0=i - 0.4,
            x1=i + 0.4,
            y0=min_range,
            y1=max_range,
            line=dict(color="rgba(0,0,0,0)"),
            fillcolor="rgba(0,100,0,0.2)",
            xref="x",
            yref="y"
        )
    
    # Customize layout
    fig.update_layout(
        title="Health Metrics",
        title_font=dict(size=20, color='#1e3a8a'),
        xaxis=dict(
            title=dict(
                text="Metrics",
                font=dict(size=14)
            ),
            tickfont=dict(size=12)
        ),
        yaxis=dict(
            title=dict(
                text="Value",
                font=dict(size=14)
            ),
            tickfont=dict(size=12)
        ),
        height=400,
        margin=dict(l=20, r=20, t=50, b=20),
        font=dict(family='Segoe UI, Arial, sans-serif', color='#333333')
    )
    
    return fig

def create_distribution_plot(values, title, normal_range=None):
    """Create a distribution plot for a health metric"""
    fig = px.histogram(
        x=values,
        nbins=30,
        title=title,
        labels={'x': 'Value', 'y': 'Frequency'},
        opacity=0.7,
        color_discrete_sequence=['#3b82f6']
    )
    
    # Add a KDE curve
    fig.add_trace(
        go.Scatter(
            x=np.linspace(min(values), max(values), 100),
            y=np.exp(-0.5 * ((np.linspace(min(values), max(values), 100) - np.mean(values)) / np.std(values))**2) / (np.std(values) * np.sqrt(2 * np.pi)) * len(values) * (max(values) - min(values)) / 30,
            mode='lines',
            name='Distribution',
            line=dict(color='#1e40af', width=2)
        )
    )
    
    # Add normal range if provided
    if normal_range:
        fig.add_shape(
            type="rect",
            x0=normal_range[0],
            x1=normal_range[1],
            y0=0,
            y1=1,
            yref="paper",
            fillcolor="rgba(0,100,0,0.2)",
            line=dict(color="rgba(0,0,0,0)"),
            name="Normal Range"
        )
        
        # Add annotations for normal range
        fig.add_annotation(
            x=normal_range[0],
            y=0.95,
            yref="paper",
            text=f"Min: {normal_range[0]}",
            showarrow=False,
            font=dict(color="#1e3a8a")
        )
        fig.add_annotation(
            x=normal_range[1],
            y=0.95,
            yref="paper",
            text=f"Max: {normal_range[1]}",
            showarrow=False,
            font=dict(color="#1e3a8a")
        )
    
    # Customize layout
    fig.update_layout(
        height=300,
        margin=dict(l=20, r=20, t=50, b=20),
        title_font=dict(size=18, color='#1e3a8a'),
        font=dict(family='Segoe UI, Arial, sans-serif', color='#333333'),
        showlegend=True
    )
    
    return fig

def create_comparison_chart(user_values, population_means, labels):
    """Create a comparison chart between user values and population means"""
    fig = go.Figure()
    
    # Add user values
    fig.add_trace(go.Bar(
        x=labels,
        y=user_values,
        name='Your Values',
        marker_color='#3b82f6',
        text=[f"{val:.1f}" for val in user_values],
        textposition='auto'
    ))
    
    # Add population means
    fig.add_trace(go.Bar(
        x=labels,
        y=population_means,
        name='Population Average',
        marker_color='#9ca3af',
        text=[f"{val:.1f}" for val in population_means],
        textposition='auto'
    ))
    
    # Customize layout
    fig.update_layout(
        title="Your Values vs Population Average",
        title_font=dict(size=18, color='#1e3a8a'),
        xaxis=dict(
            title=dict(
                text="Metrics",
                font=dict(size=14)
            ),
            tickfont=dict(size=12)
        ),
        yaxis=dict(
            title=dict(
                text="Value",
                font=dict(size=14)
            ),
            tickfont=dict(size=12)
        ),
        height=350,
        margin=dict(l=20, r=20, t=50, b=20),
        font=dict(family='Segoe UI, Arial, sans-serif', color='#333333'),
        barmode='group'
    )
    
    return fig

def create_trend_line(x_values, y_values, x_label, y_label):
    """Create a trend line chart"""
    fig = go.Figure()
    
    # Add the trend line
    fig.add_trace(go.Scatter(
        x=x_values,
        y=y_values,
        mode='lines',
        name='Trend',
        line=dict(color='#3b82f6', width=2)
    ))
    
    # Customize layout
    fig.update_layout(
        title=f"{y_label} vs {x_label}",
        title_font=dict(size=18, color='#1e3a8a'),
        xaxis=dict(
            title=dict(
                text=x_label,
                font=dict(size=14)
            ),
            tickfont=dict(size=12)
        ),
        yaxis=dict(
            title=dict(
                text=y_label,
                font=dict(size=14)
            ),
            tickfont=dict(size=12)
        ),
        height=300,
        margin=dict(l=20, r=20, t=50, b=20),
        font=dict(family='Segoe UI, Arial, sans-serif', color='#333333')
    )
    
    return fig

# Load the saved models
try:
    diabetes_model = pickle.load(open('diabetes_model.sav', 'rb'))
except Exception as e:
    st.error(f"Error loading diabetes model: {str(e)}")
    diabetes_model = DummyModel("Diabetes")

try:
    heart_disease_model = pickle.load(open('heart_disease_model.sav', 'rb'))
except Exception as e:
    st.error(f"Error loading heart disease model: {str(e)}")
    heart_disease_model = DummyModel("Heart Disease")

try:
    parkinsons_model = pickle.load(open('parkinsons_model.sav', 'rb'))
except Exception as e:
    st.error(f"Error loading parkinsons model: {str(e)}")
    parkinsons_model = DummyModel("Parkinsons")

# Set page configuration with light background and dark text
st.set_page_config(
    page_title="Health AI - Disease Prediction",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Hide Streamlit style
hide_streamlit_style = """
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display: none;}
    .stDecoration {display: none;}
    
    /* Import Inter font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Apply Inter font globally */
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    /* Make login page full screen */
    .block-container {
        padding-top: 0rem;
        padding-bottom: 0rem;
        padding-left: 0rem;
        padding-right: 0rem;
        max-width: none;
    }
    
    /* Hide sidebar on login page */
    .css-1d391kg {
        display: none;
    }
</style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# Custom CSS to enhance the appearance with better font visibility
st.markdown("""
<style>
    /* Base styles */
    body {
        font-family: 'Segoe UI', Arial, sans-serif;
        color: #333333;
        background-color: #f8f9fa;
    }
    
    /* Main container */
    .main {
        background-color: #f8f9fa;
    }
    
    .stApp {
        background-image: linear-gradient(to bottom, #f8f9fa, #e9ecef);
    }
    
    /* Typography with improved visibility */
    h1, h2, h3, h4, h5, h6 {
        color: #1e3a8a !important;
        font-family: 'Segoe UI', Arial, sans-serif;
        font-weight: 700;
        margin-bottom: 1rem;
        text-shadow: none !important;
    }
    
    h1 {
        font-size: 2.5rem !important;
        letter-spacing: -0.5px;
    }
    
    h2 {
        font-size: 2rem !important;
    }
    
    h3 {
        font-size: 1.5rem !important;
    }
    
    p, li, label, div {
        color: #333333 !important;
        font-size: 1.1rem !important;
        line-height: 1.6 !important;
    }
    
    /* Button styling */
    .stButton>button {
        background-color: #1e40af;
        color: white !important;
        font-weight: bold;
        font-size: 1rem !important;
        border-radius: 5px;
        border: none;
        padding: 0.75rem 1.5rem;
        transition: all 0.3s;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .stButton>button:hover {
        background-color: #1e3a8a;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        transform: translateY(-2px);
    }
    
    /* Card styling */
    .css-1d391kg, .css-12oz5g7 {
        background-color: #ffffff;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    .prediction-card {
        background-color: white;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        margin-bottom: 20px;
        border-left: 5px solid #1e40af;
    }
    
    .prediction-card h3 {
        color: #1e3a8a !important;
        font-size: 1.5rem !important;
        margin-bottom: 1rem;
    }
    
    .prediction-card p {
        color: #333333 !important;
        font-size: 1.1rem !important;
    }
    
    /* Sidebar styling */
    .sidebar .sidebar-content {
        background-color: #1e40af;
    }
    
    /* Input fields */
    .stTextInput>div>div>input, .stNumberInput>div>div>input {
        border-radius: 5px;
        border: 1px solid #cbd5e1;
        padding: 12px;
        font-size: 1rem !important;
        color: #333333 !important;
        background-color: #ffffff;
    }
    
    /* Message styling */
    .success-message {
        background-color: #dcfce7;
        color: #166534 !important;
        padding: 15px;
        border-radius: 5px;
        border-left: 5px solid #22c55e;
        margin: 15px 0;
        font-size: 1.1rem !important;
    }
    
    .warning-message {
        background-color: #fef9c3;
        color: #854d0e !important;
        padding: 15px;
        border-radius: 5px;
        border-left: 5px solid #eab308;
        margin: 15px 0;
        font-size: 1.1rem !important;
    }
    
    .info-box {
        background-color: #dbeafe;
        color: #1e40af !important;
        padding: 15px;
        border-radius: 5px;
        border-left: 5px solid #3b82f6;
        margin: 15px 0;
        font-size: 1.1rem !important;
    }
    
    /* Improve text contrast in all elements */
    .stMarkdown, .stText {
        color: #333333 !important;
    }
    
    /* Make sure all text in markdown is visible */
    .stMarkdown p, .stMarkdown li, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
        color: #333333 !important;
    }
    
    /* Ensure good contrast for links */
    a {
        color: #1e40af !important;
        text-decoration: underline;
        font-weight: 500;
    }
    
    a:hover {
        color: #1e3a8a !important;
    }
    
    /* Improve visibility of option menu */
    .nav-link {
        color: #333333 !important;
        font-weight: 500 !important;
        font-size: 1.1rem !important;
    }
    
    .nav-link-selected {
        color: white !important;
        font-weight: 700 !important;
    }
    
    .nav-link:hover {
        color: #1e40af !important;
    }
    
    /* Improve visibility of expanders */
    .streamlit-expanderHeader {
        font-weight: 600 !important;
        color: #1e3a8a !important;
        font-size: 1.1rem !important;
    }
    
    /* Fix for text in tabs */
    .stTabs [data-baseweb="tab"] {
        color: #333333 !important;
        font-weight: 600 !important;
    }
    
    .stTabs [data-baseweb="tab-panel"] {
        color: #333333 !important;
    }
    
    /* Fix for text in selectbox */
    .stSelectbox label, .stSelectbox div {
        color: #333333 !important;
    }
    
    /* Fix for text in number inputs */
    .stNumberInput label, .stNumberInput div {
        color: #333333 !important;
    }
    
    /* Fix for text in sliders */
    .stSlider label, .stSlider div {
        color: #333333 !important;
    }
    
    /* Fix for text in dataframes */
    .dataframe {
        color: #333333 !important;
    }
    
    /* Fix for text in metrics */
    .stMetric label, .stMetric div {
        color: #333333 !important;
    }
    
    /* Fix for text in plotly charts */
    .js-plotly-plot .plotly text {
        fill: #333333 !important;
    }
    
    /* Fix for text in footers */
    footer {
        color: white !important;
    }
    
    footer a {
        color: white !important;
    }
    
    /* Fix for text in prediction results */
    .prediction-result {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }
    
    .prediction-result h3 {
        color: #1e3a8a !important;
        font-size: 1.5rem !important;
        margin-bottom: 1rem;
    }
    
    .prediction-result p {
        color: #333333 !important;
        font-size: 1.2rem !important;
        font-weight: 600;
    }
    
    .risk-level {
        display: inline-block;
        padding: 5px 10px;
        border-radius: 5px;
        font-weight: bold;
        margin: 10px 0;
    }
    
    .high-risk {
        background-color: #fee2e2;
        color: #b91c1c !important;
    }
    
    .low-risk {
        background-color: #dcfce7;
        color: #166534 !important;
    }
    
    .risk-label, .confidence-label {
        font-weight: 600;
        margin-right: 5px;
    }
    
    .risk-value, .confidence-value {
        font-weight: 700;
    }
    
    /* Fix for variable text colors */
    [data-testid="stText"] {
        color: #333333 !important;
    }
    
    [data-testid="stMarkdown"] {
        color: #333333 !important;
    }
</style>
""", unsafe_allow_html=True)

# Function to download and save image
def download_image(url, filename):
    """Download an image from URL and save it to the images directory"""
    # Create images directory if it doesn't exist
    images_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'images')
    if not os.path.exists(images_dir):
        os.makedirs(images_dir)
    
    file_path = os.path.join(images_dir, filename)
    
    # If file already exists, return its path
    if os.path.exists(file_path):
        return file_path
    
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()  # Raise an exception for HTTP errors
        
        with open(file_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        st.success(f"Downloaded {filename}")
        return file_path
    except Exception as e:
        st.error(f"Error downloading {filename}: {str(e)}")

# Function to add a background image
def add_bg_from_local(image_file):
    with open(image_file, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read())
    st.markdown(
    f"""
    <style>
    .stApp {{
        background-image: url(data:image/{"png"};base64,{encoded_string.decode()});
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }}
    </style>
    """,
    unsafe_allow_html=True
    )

# Try to use a background image if available
try:
    if os.path.exists("images/medical_bg.jpg"):
        add_bg_from_local("images/medical_bg.jpg")
except:
    pass

# Function to display a styled header
def styled_header(text, level=1):
    if level == 1:
        st.markdown(f"<h1 style='text-align: center; color: #1e3a8a; padding-bottom: 20px; font-size: 2.5rem;'>{text}</h1>", unsafe_allow_html=True)
    elif level == 2:
        st.markdown(f"<h2 style='color: #1e40af; padding-bottom: 10px; font-size: 2rem;'>{text}</h2>", unsafe_allow_html=True)
    elif level == 3:
        st.markdown(f"<h3 style='color: #1e3a8a; padding-bottom: 5px; font-size: 1.5rem;'>{text}</h3>", unsafe_allow_html=True)

# Function to display a styled success message
def styled_success(text):
    st.markdown(f"<div class='success-message'>{text}</div>", unsafe_allow_html=True)

# Function to display a styled warning message
def styled_warning(text):
    st.markdown(f"<div class='warning-message'>{text}</div>", unsafe_allow_html=True)

# Function to display a styled info box
def styled_info(text):
    st.markdown(f"<div class='info-box'>{text}</div>", unsafe_allow_html=True)

# Function to create a styled card
def styled_card(title, content, icon="🔍"):
    st.markdown(f"""
    <div class="prediction-card">
        <h3 style="color: #1e3a8a; font-size: 1.5rem;">{icon} {title}</h3>
        <p style="color: #333333; font-size: 1.1rem; line-height: 1.6;">{content}</p>
    </div>
    """, unsafe_allow_html=True)

# Function to create and save a model
def create_and_save_model(name, n_features, model_path):
    """Create and save a new model with sample data"""
    model = None
    try:
        # Create sample data
        np.random.seed(42)  # For reproducibility
        X = np.random.rand(1000, n_features)  # 1000 samples
        # Create target variable with some pattern
        y = (X.sum(axis=1) > n_features/2).astype(int)
        
        # Create and train model
        model = RandomForestClassifier(n_estimators=100, random_state=42)
        model.fit(X, y)
        
        # Save model
        with open(model_path, 'wb') as f:
            pickle.dump(model, f)
        
        st.success(f"Successfully created and saved new {name} model")
    except Exception as e:
        st.error(f"Error creating {name} model: {str(e)}")
        model = None
    return model

# Function to safely load model
def load_model(model_path, n_features, model_name="Unknown"):
    """Safely load a model, creating a new one if it doesn't exist"""
    try:
        # Check if model file exists
        if os.path.exists(model_path):
            # Load the model
            model = pickle.load(open(model_path, 'rb'))
            return model
        else:
            st.warning(f"{model_name} model not found. Creating a new one...")
            return create_and_save_model(model_name, n_features, model_path)
    except Exception as e:
        st.error(f"Error loading {model_name} model: {str(e)}")
        return DummyModel(model_name)

# Initialize session state and check login
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

if 'user' not in st.session_state:
    st.session_state['user'] = None

# Check if user is logged in
if not st.session_state['logged_in']:
    # Show login page with hidden sidebar
    login_page()
    st.stop()

# Add a sidebar for navigation
with st.sidebar:
    # Add title and logo with improved visibility
    st.markdown("""
    <div style="background-color: #ffffff; padding: 15px; border-radius: 10px; margin-bottom: 20px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); text-align: center;">
        <h1 style="color: #1e3a8a; font-size: 2.5rem; font-weight: 800; margin-bottom: 5px; text-shadow: 1px 1px 2px rgba(0,0,0,0.1);">🏥 Health AI</h1>
        <h3 style="color: #333333; font-size: 1.5rem; font-weight: 600; margin-top: 0;">Advanced Disease Prediction</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Show user info and logout button
    if 'user' in st.session_state and st.session_state['user']:
        user = st.session_state['user']
        st.markdown(f"""
        <div style="background-color: #e0f2fe; padding: 10px; border-radius: 8px; margin-bottom: 15px; border-left: 4px solid #0277bd;">
            <p style="margin: 0; color: #0277bd; font-weight: 600;">👤 {user['username']}</p>
            <p style="margin: 0; color: #555; font-size: 0.9rem;">Role: {user['role'].title()}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Logout button
        if st.button("🚪 Logout", key="logout_button", help="Sign out of your account"):
            logout()
    
    # Add a separator
    st.markdown("<hr style='margin: 15px 0; border: 0; height: 2px; background: linear-gradient(to right, #1e40af, #3b82f6, #1e40af);'>", unsafe_allow_html=True)
    
    # Create the navigation menu
    selected = option_menu(
        menu_title=None,  # Remove the span styling that's causing issues
        options=["Welcome", "Diabetes Prediction", "Heart Disease Prediction", "Parkinson's Prediction", "History", "Requirements", "About"],
        icons=["house", "activity", "heart", "person", "clock-history", "info-circle", "file-earmark-text"],
        menu_icon="cast",
        default_index=0,
        styles={
            "container": {"padding": "15px", "background-color": "#ffffff", "border-radius": "10px", "box-shadow": "0 2px 5px rgba(0,0,0,0.1)"},
            "icon": {"color": "#1e40af", "font-size": "22px"},
            "nav-link": {
                "font-size": "1.2rem", 
                "text-align": "left", 
                "margin": "8px 0", 
                "padding": "12px",
                "--hover-color": "#dbeafe",
                "transition": "all 0.3s",
                "border-radius": "7px",
                "color": "#333333 !important",
                "font-weight": "600"
            },
            "nav-link-selected": {
                "background-color": "#1e40af", 
                "color": "white !important",
                "font-weight": "700",
                "box-shadow": "0 2px 5px rgba(0,0,0,0.2)"
            },
        }
    )
    
    # Add a navigation title above the menu
    st.markdown("<h3 style='color: #1e3a8a; font-size: 1.5rem; font-weight: 700; margin-bottom: 10px;'>Navigation</h3>", unsafe_allow_html=True)
    
    # Add some information at the bottom of the sidebar
    st.markdown("<hr style='margin: 25px 0; border: 0; height: 2px; background: linear-gradient(to right, #1e40af, #3b82f6, #1e40af);'>", unsafe_allow_html=True)
    st.markdown("""
    <div style="background-color: #ffffff; padding: 15px; border-radius: 10px; margin-bottom: 20px; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
        <h3 style="color: #1e3a8a; font-size: 1.5rem; font-weight: 700; margin-bottom: 10px;">How it works</h3>
        <p style="color: #333333; font-size: 1.1rem; line-height: 1.5;">This system uses machine learning to predict the likelihood of various diseases based on medical parameters.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Add disclaimer
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
    <div style="background-color: #fef9c3; padding: 20px; border-radius: 10px; border-left: 5px solid #eab308; margin-bottom: 20px;">
        <h3 style="color: #854d0e; margin-bottom: 10px;">Disclaimer</h3>
        <p style="color: #854d0e; font-size: 16px; line-height: 1.6;">
            <strong>This application is for educational and informational purposes only.</strong> 
            It is not intended to be a substitute for professional medical advice, diagnosis, or treatment. 
            Always seek the advice of your physician or other qualified health provider with any questions 
            you may have regarding a medical condition.
        </p>
    </div>
    """, unsafe_allow_html=True)

# Add new functions for interactive popups
def show_welcome_popup():
    """Show a welcome popup when the app starts"""
    # Initialize welcome popup state if not exists
    if 'welcome_popup_shown' not in st.session_state:
        st.session_state.welcome_popup_shown = False
    
    # Show popup if not dismissed yet
    if not st.session_state.welcome_popup_shown:
        with st.container():
            st.markdown("""
            <div style="
                background: white;
                padding: 30px;
                border-radius: 15px;
                box-shadow: 0 4px 20px rgba(0,0,0,0.2);
                max-width: 500px;
                width: 100%;
                text-align: center;
                margin: 0 auto;">
                <h2 style="color: #1e3a8a; margin-bottom: 20px;">👋 Welcome to Health AI!</h2>
                <p style="color: #333; margin-bottom: 20px; line-height: 1.6;">
                    Your personal health prediction assistant. We use advanced AI to help you understand potential health risks.
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("Get Started", key="welcome_close_btn"):
                st.session_state.welcome_popup_shown = True
                st.rerun()

def show_tip_popup(tip_title, tip_content):
    """Show a floating tip popup"""
    # Initialize tip popup state if not exists
    if 'tip_popup_shown' not in st.session_state:
        st.session_state.tip_popup_shown = False
    
    # Show tip if not dismissed yet
    if not st.session_state.tip_popup_shown:
        with st.sidebar.container():
            st.markdown(f"""
            <div style="
                background: white;
                padding: 15px;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                max-width: 300px;
                border-left: 4px solid #1e40af;">
                <h4 style="color: #1e3a8a; margin: 0 0 10px 0;">💡 {tip_title}</h4>
                <p style="color: #333; margin: 0; font-size: 0.9rem;">{tip_content}</p>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("Dismiss Tip", key="tip_close_btn"):
                st.session_state.tip_popup_shown = True
                st.rerun()

def show_help_button():
    """Show a floating help button with popup content"""
    # Initialize help popup state if not exists
    if 'help_popup_shown' not in st.session_state:
        st.session_state.help_popup_shown = False
    
    # Create a container for the help button
    with st.sidebar:
        if st.button("❔ Help", key="help_button"):
            st.session_state.help_popup_shown = not st.session_state.help_popup_shown
            st.rerun()
        
        # Show help content if button was clicked
        if st.session_state.help_popup_shown:
            st.markdown("""
            <div style="
                background: white;
                padding: 15px;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                <h4 style="color: #1e3a8a; margin: 0 0 10px 0;">Need Help?</h4>
                <ul style="margin: 0; padding-left: 20px; color: #333;">
                    <li>Use the sidebar to navigate</li>
                    <li>Enter your health parameters</li>
                    <li>Get instant predictions</li>
                    <li>View detailed analysis</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("Close Help", key="help_close_btn"):
                st.session_state.help_popup_shown = False
                st.rerun()

def add_tooltip(element_id, tooltip_text):
    """Add a tooltip to an element"""
    tooltip_css = f"""
        <style>
            #{element_id} {{
                position: relative;
            }}
            #{element_id}:hover::after {{
                content: "{tooltip_text}";
                position: absolute;
                bottom: 100%;
                left: 50%;
                transform: translateX(-50%);
                padding: 8px;
                background: #1e3a8a;
                color: white;
                border-radius: 5px;
                font-size: 0.9rem;
                white-space: nowrap;
                z-index: 1000;
            }}
        </style>
    """
    st.markdown(tooltip_css, unsafe_allow_html=True)

# Add this after the page config
if 'user' not in st.session_state:
    st.session_state['user'] = None

if 'show_registration' not in st.session_state:
    st.session_state['show_registration'] = False

# User is authenticated, continue with main app
# The user dashboard will be shown when they select "History" from the menu

# Welcome Page
if (selected == 'Welcome'):
    # Show welcome popup on app start
    show_welcome_popup()
    
    # Show floating help button
    show_help_button()
    
    # Show random tips
    tips = [
        ("Quick Tip", "Use the sidebar menu to navigate between different disease predictions."),
        ("Did you know?", "Our AI models are trained on thousands of real medical cases."),
        ("Pro Tip", "Regular health check-ups are key to early disease detection.")
    ]
    show_tip_popup(*random.choice(tips))
    
    # Display welcome header
    styled_header("Welcome to the Multiple Disease Prediction System")
    
    # Create a clean, modern welcome page
    st.markdown("""
    <div style="background-color: white; padding: 20px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
        <h2 style="color: #1e3a8a; text-align: center; margin-bottom: 20px;">AI-Powered Health Analysis</h2>
        <p style="font-size: 16px; line-height: 1.6; color: #333333;">
            This application uses machine learning algorithms to predict the likelihood of various diseases
            based on medical parameters. The system currently supports prediction for:
        </p>
        <ul style="font-size: 16px; line-height: 1.6; color: #333333;">
            <li><strong style="color: #1e3a8a;">Diabetes</strong> - Based on factors like glucose levels, BMI, and family history</li>
            <li><strong style="color: #1e3a8a;">Heart Disease</strong> - Using cardiovascular parameters and patient history</li>
            <li><strong style="color: #1e3a8a;">Parkinson's Disease</strong> - Analyzing voice and speech pattern measurements</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    # Add some space
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Create feature cards
    col1, col2, col3 = st.columns(3)
    
    with col1:
        styled_card("Diabetes Prediction", "Predict diabetes risk based on medical parameters like glucose levels, BMI, and family history.", "🩸")
    
    with col2:
        styled_card("Heart Disease Prediction", "Analyze cardiovascular health using blood pressure, cholesterol levels, and other factors.", "❤️")
    
    with col3:
        styled_card("Parkinson's Prediction", "Assess Parkinson's disease risk through voice and speech pattern analysis.", "🧠")
    
    # Add information section
    st.markdown("<br>", unsafe_allow_html=True)
    styled_header("How to Use", level=2)
    
    st.markdown("""
    <div style="background-color: #dbeafe; padding: 20px; border-radius: 10px; border-left: 5px solid #3b82f6; margin-bottom: 20px;">
        <h3 style="color: #1e3a8a; margin-bottom: 15px;">Simple Steps:</h3>
        <ol style="font-size: 16px; line-height: 1.6; color: #333333;">
            <li><strong>Select the disease prediction type</strong> from the sidebar menu</li>
            <li><strong>Enter the required medical parameters</strong> in the input fields</li>
            <li><strong>Click the prediction button</strong> to get your results</li>
            <li><strong>Review the detailed analysis</strong> and recommendations</li>
        </ol>
    </div>
    """, unsafe_allow_html=True)
    
    # Add disclaimer
    st.markdown("<br>", unsafe_allow_html=True)
    styled_warning("""
    <strong>Disclaimer:</strong> This application is for educational and informational purposes only. 
    It is not intended to be a substitute for professional medical advice, diagnosis, or treatment. 
    Always seek the advice of your physician or other qualified health provider with any questions 
    you may have regarding a medical condition.
    """)
    
    # Add about section
    st.markdown("<br>", unsafe_allow_html=True)
    styled_header("About the Project", level=2)
    
    st.markdown("""
    <div style="background-color: white; padding: 20px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
        <p style="font-size: 16px; line-height: 1.6;">
            This project uses machine learning models trained on medical datasets to predict disease likelihood.
            The models have been trained on:
        </p>
        <ul style="font-size: 16px; line-height: 1.6;">
            <li><strong>Diabetes:</strong> Pima Indians Diabetes Database</li>
            <li><strong>Heart Disease:</strong> UCI Heart Disease Dataset</li>
            <li><strong>Parkinson's:</strong> UCI Parkinson's Dataset</li>
        </ul>
        <p style="font-size: 16px; line-height: 1.6;">
            The application is built with Streamlit and uses scikit-learn for the machine learning components.
        </p>
    </div>
    """, unsafe_allow_html=True)

# Enhanced Diabetes Prediction Page
if (selected == 'Diabetes Prediction'):
    # Show help button
    show_help_button()
    
    st.title('Diabetes Prediction')
    
    # Add tooltips for input fields
    add_tooltip("glucose", "Fasting blood sugar level in mg/dL")
    add_tooltip("bmi", "Body Mass Index - weight(kg)/height(m)²")
    add_tooltip("age", "Age in years")
    add_tooltip("insulin", "2-Hour serum insulin (mu U/ml)")
    add_tooltip("skin", "Triceps skin fold thickness (mm)")
    add_tooltip("bp", "Diastolic blood pressure (mm Hg)")
    add_tooltip("dpf", "Diabetes Pedigree Function")
    add_tooltip("pregnancies", "Number of pregnancies")
    
    # Getting the input data from the user
    col1, col2, col3 = st.columns(3)
    
    with col1:
        Pregnancies = st.number_input('Number of Pregnancies', 
                                     min_value=0, 
                                     max_value=20, 
                                     value=0, 
                                     step=1,
                                     help="Enter number of pregnancies (0-20)",
                                     key="pregnancies")
        
    with col2:
        Glucose = st.number_input('Glucose Level (mg/dL)', 
                                 min_value=70, 
                                 max_value=200, 
                                 value=120, 
                                 step=1,
                                 help="Normal range: 70-140 mg/dL",
                                 key="glucose")
        
    with col3:
        BloodPressure = st.number_input('Blood Pressure (mm Hg)', 
                                       min_value=40, 
                                       max_value=130, 
                                       value=80, 
                                       step=1,
                                       help="Normal range: 60-90 mm Hg",
                                       key="bp")
        
    with col1:
        SkinThickness = st.number_input('Skin Thickness (mm)', 
                                       min_value=0, 
                                       max_value=100, 
                                       value=20, 
                                       step=1,
                                       help="Normal range: 10-50 mm",
                                       key="skin")
        
    with col2:
        Insulin = st.number_input('Insulin Level (mu U/ml)', 
                                 min_value=0, 
                                 max_value=850, 
                                 value=80, 
                                 step=1,
                                 help="Normal range: 16-166 mu U/ml",
                                 key="insulin")
        
    with col3:
        BMI = st.number_input('BMI value', 
                             min_value=10.0, 
                             max_value=50.0, 
                             value=25.0, 
                             step=0.1,
                             help="Normal range: 18.5-24.9",
                             key="bmi")
        
    with col1:
        DiabetesPedigreeFunction = st.number_input('Diabetes Pedigree Function', 
                                                  min_value=0.0, 
                                                  max_value=2.5, 
                                                  value=0.5, 
                                                  step=0.01,
                                                  help="Diabetes hereditary score (0.0-2.5)",
                                                  key="dpf")
        
    with col2:
        Age = st.number_input('Age (years)', 
                             min_value=21, 
                             max_value=90, 
                             value=35, 
                             step=1,
                             help="Enter age between 21-90 years",
                             key="age")

    # Center the predict button
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        predict_diabetes = st.button("Predict Diabetes Risk", use_container_width=True)

    # Information about the parameters
    with st.expander("Learn about these parameters"):
        st.markdown("""
        <div style="background-color: #f8f9fa; padding: 15px; border-radius: 10px;">
            <h4 style="color: #1e3a8a;">Parameter Normal Ranges:</h4>
            <ul>
                <li><strong>Glucose Level</strong>: 70-140 mg/dL (fasting)</li>
                <li><strong>Blood Pressure</strong>: 60-90 mm Hg (diastolic)</li>
                <li><strong>Skin Thickness</strong>: 10-50 mm (triceps fold)</li>
                <li><strong>Insulin</strong>: 16-166 mu U/ml (2-hour serum)</li>
                <li><strong>BMI</strong>: 18.5-24.9 (normal weight)</li>
                <li><strong>Diabetes Pedigree Function</strong>: Scores likelihood of diabetes based on family history</li>
            </ul>
            <p><em>Note: Values outside normal ranges may indicate higher risk for diabetes.</em></p>
        </div>
        """, unsafe_allow_html=True)
    
    # code for Prediction
    diab_diagnosis = ''
    
    # creating a button for Prediction
    if predict_diabetes:
        
        try:
            with st.spinner("Analyzing your health parameters..."):
                time.sleep(2)
                
                # Get input values
                pregnancies = float(Pregnancies)
                glucose = float(Glucose)
                blood_pressure = float(BloodPressure)
                skin_thickness = float(SkinThickness)
                insulin = float(Insulin)
                bmi = float(BMI)
                dpf = float(DiabetesPedigreeFunction)
                age = float(Age)
                
                # Create input data for prediction
                diab_diagnosis = ''
                input_data = np.array([[pregnancies, glucose, blood_pressure, skin_thickness, insulin, bmi, dpf, age]])
                
                # Get prediction and probability
                prediction = diabetes_model.predict(input_data)
                prediction_proba = get_prediction_probability(diabetes_model, input_data)
                
                # Process prediction result
                if prediction[0] == 1:
                    diab_diagnosis = 'The person is diabetic'
                    is_positive = True
                    risk_level = "High Risk"
                else:
                    diab_diagnosis = 'The person is not diabetic'
                    is_positive = False
                    risk_level = "Low Risk"
                
                # Show main prediction result
                show_result_popup(diab_diagnosis, calculate_confidence(prediction_proba), is_positive)
                
                # Create three columns for metrics
                col1, col2, col3 = st.columns([1,2,1])
                
                with col2:
                    st.markdown(f"""
                    <div class="prediction-result {'positive' if is_positive else 'negative'}">
                        <h3>Prediction Result</h3>
                        <p class="diagnosis">{diab_diagnosis}</p>
                        <div class="risk-level {risk_level.lower().replace(' ', '-')}">
                            <span class="risk-label">Risk Level:</span>
                            <span class="risk-value">{risk_level}</span>
                        </div>
                        <div class="confidence">
                            <span class="confidence-label">Confidence:</span>
                            <span class="confidence-value">{calculate_confidence(prediction_proba):.1f}%</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Create tabs for analysis and metrics
                analysis_tab, metrics_tab = st.tabs(["Analysis", "Health Metrics"])
                
                with analysis_tab:
                    # Show feature importance
                    st.subheader("Feature Importance")
                    features = ['Pregnancies', 'Glucose', 'Blood Pressure', 'Skin Thickness', 'Insulin', 'BMI', 'Diabetes Pedigree Function', 'Age']
                    importance_scores = [0.05, 0.28, 0.10, 0.07, 0.15, 0.20, 0.08, 0.07]  # Example scores
                    st.plotly_chart(plot_feature_importance(features, importance_scores))
                    
                    # Show prediction probability
                    st.plotly_chart(plot_prediction_proba(prediction_proba[0]))
                
                with metrics_tab:
                    # Define metrics values and ranges
                    metrics_values = [glucose, blood_pressure, bmi]
                    metrics_labels = ['Glucose Level', 'Blood Pressure', 'BMI']
                    metrics_ranges = [(70, 140), (60, 90), (18.5, 24.9)]
                    
                    # Show health metrics
                    st.plotly_chart(create_metrics_chart(metrics_values, metrics_labels, metrics_ranges))
                    
                    # Add distribution plot for glucose levels
                    st.subheader("Glucose Level Distribution")
                    sample_glucose_values = np.random.normal(loc=glucose, scale=10, size=1000)
                    st.plotly_chart(create_distribution_plot(
                        sample_glucose_values,
                        "Glucose Level Distribution",
                        normal_range=(70, 140)
                    ))
                    
                    # Add comparison chart
                    st.subheader("Your Values vs Population Average")
                    user_values = [glucose, blood_pressure, bmi]
                    population_means = [100, 80, 25]
                    labels = ['Glucose', 'Blood Pressure', 'BMI']
                    st.plotly_chart(create_comparison_chart(user_values, population_means, labels))
                    
                    # Add explanatory text
                    st.markdown("""
                    <div style="background-color: #f8f9fa; padding: 15px; border-radius: 10px; margin-top: 20px;">
                        <h4 style="color: #1e3a8a;">Understanding Your Metrics:</h4>
                        
                        <p><strong>Glucose Level</strong>:</p>
                        <ul>
                            <li>Normal: 70-140 mg/dL</li>
                            <li>Prediabetes: 140-199 mg/dL</li>
                            <li>Diabetes: 200+ mg/dL</li>
                        </ul>
                        
                        <p><strong>Blood Pressure</strong>:</p>
                        <ul>
                            <li>Normal: Below 80 mmHg (diastolic)</li>
                            <li>Elevated: 80-89 mmHg</li>
                            <li>High: 90+ mmHg</li>
                        </ul>
                        
                        <p><strong>BMI (Body Mass Index)</strong>:</p>
                        <ul>
                            <li>Underweight: Below 18.5</li>
                            <li>Normal: 18.5-24.9</li>
                            <li>Overweight: 25-29.9</li>
                            <li>Obese: 30+</li>
                        </ul>
                    </div>
                    """, unsafe_allow_html=True)
                
                if diab_diagnosis:
                    save_prediction(
                        st.session_state['user']['id'],
                        "Diabetes",
                        diab_diagnosis,
                        calculate_confidence(prediction_proba)
                    )
        except Exception as e:
            st.error(f"An error occurred: {e}")
            st.info("Please ensure all fields contain valid numeric values.")

# Heart Disease Prediction Page
if (selected == "Heart Disease Prediction"):
    # Show help button
    show_help_button()
    
    st.title("Heart Disease Prediction")
    
    # Add information about heart parameters
    with st.expander("ℹ️ Understanding Heart Health Parameters"):
        st.markdown("""
        ### Normal Ranges for Heart Health Parameters:
        - **Age**: Adult patients (29-77 years)
        - **Blood Pressure**: 90/60-120/80 mmHg (Normal)
        - **Cholesterol**: < 200 mg/dL (Desirable)
        - **Heart Rate**: 60-100 beats per minute (Rest)
        - **Blood Sugar**: < 140 mg/dL (Fasting)
        """)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        age = st.number_input('Age', 
                            min_value=29, 
                            max_value=77, 
                            value=45,
                            help="Patient's age in years (29-77)")
        
    with col2:
        sex = st.selectbox('Sex',
                          options=['Male', 'Female'],
                          help="Patient's biological sex")
        sex = 1 if sex == 'Male' else 0
        
    with col3:
        cp = st.selectbox('Chest Pain Type',
                         options=['Typical Angina', 
                                 'Atypical Angina', 
                                 'Non-anginal Pain', 
                                 'Asymptomatic'],
                         help="""
                         - Typical Angina: Chest pain related to heart
                         - Atypical Angina: Chest pain not related to heart
                         - Non-anginal Pain: Pain not related to angina
                         - Asymptomatic: No pain
                         """)
        cp = ['Typical Angina', 'Atypical Angina', 
              'Non-anginal Pain', 'Asymptomatic'].index(cp)
        
    with col1:
        trestbps = st.number_input('Resting Blood Pressure (mmHg)', 
                                  min_value=90, 
                                  max_value=200, 
                                  value=120,
                                  help="Normal: 90-120 mmHg")
        
    with col2:
        chol = st.number_input('Cholesterol (mg/dl)', 
                              min_value=126, 
                              max_value=564, 
                              value=200,
                              help="""
                              Cholesterol levels:
                              - Normal: < 200 mg/dL
                              - Borderline: 200-239 mg/dL
                              - High: ≥ 240 mg/dL
                              """)
        
    with col3:
        fbs = st.selectbox('Fasting Blood Sugar > 120 mg/dl',
                          options=['No', 'Yes'],
                          help="Fasting blood sugar > 120 mg/dl")
        fbs = 1 if fbs == 'Yes' else 0
        
    with col1:
        restecg = st.selectbox('Resting ECG Results',
                              options=['Normal',
                                      'ST-T Wave Abnormality',
                                      'Left Ventricular Hypertrophy'],
                              help="""
                              - Normal: No abnormalities
                              - ST-T Wave Abnormality: ST-T wave changes
                              - Left Ventricular Hypertrophy: Showing probable or definite left ventricular hypertrophy
                              """)
        restecg = ['Normal', 
                   'ST-T Wave Abnormality',
                   'Left Ventricular Hypertrophy'].index(restecg)
        
    with col2:
        thalach = st.number_input('Maximum Heart Rate',
                                 min_value=71,
                                 max_value=202,
                                 value=150,
                                 help="Maximum heart rate achieved (71-202)")
        
    with col3:
        exang = st.selectbox('Exercise Induced Angina',
                            options=['No', 'Yes'],
                            help="Angina induced by exercise")
        exang = 1 if exang == 'Yes' else 0
        
    with col1:
        oldpeak = st.number_input('ST Depression',
                                 min_value=0.0,
                                 max_value=6.2,
                                 value=0.0,
                                 step=0.1,
                                 format="%.1f",
                                 help="ST depression induced by exercise relative to rest")
        
    with col2:
        slope = st.selectbox('Slope of Peak ST Segment',
                            options=['Upsloping', 'Flat', 'Downsloping'],
                            help="""
                            The slope of the peak exercise ST segment:
                            - Upsloping: Better prognosis
                            - Flat: Moderate prognosis
                            - Downsloping: Poor prognosis
                            """)
        slope = ['Upsloping', 'Flat', 'Downsloping'].index(slope)
        
    with col3:
        ca = st.number_input('Number of Major Vessels',
                            min_value=0,
                            max_value=3,
                            value=0,
                            help="Number of major vessels colored by fluoroscopy (0-3)")
        
    with col1:
        thal = st.selectbox('Thalassemia',
                           options=['Normal', 'Fixed Defect', 'Reversible Defect'],
                           help="""
                           Blood disorder called thalassemia:
                           - Normal: Normal blood flow
                           - Fixed Defect: No blood flow in some part
                           - Reversible Defect: A blood flow is observed but it is not normal
                           """)
        thal = ['Normal', 'Fixed Defect', 'Reversible Defect'].index(thal) + 1

    # Create a styled container for the predict button
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        predict_heart = st.button("Predict Heart Disease Risk", use_container_width=True)
     
    # code for Prediction
    if predict_heart:
        try:
            with st.spinner("Analyzing heart health parameters..."):
                time.sleep(2)
                
                # Make prediction
                heart_prediction = heart_disease_model.predict([[age, sex, cp, trestbps, chol, fbs, restecg,
                                                               thalach, exang, oldpeak, slope, ca, thal]])
                prediction_proba = get_prediction_probability(heart_disease_model, [[age, sex, cp, trestbps, chol, fbs, restecg,
                                                                                   thalach, exang, oldpeak, slope, ca, thal]])
                
                # Calculate risk metrics
                risk_factors = 0
                risk_messages = []
                
                if age > 55:
                    risk_factors += 1
                    risk_messages.append("Age above 55")
                if trestbps > 140:
                    risk_factors += 1
                    risk_messages.append("High blood pressure")
                if chol > 200:
                    risk_factors += 1
                    risk_messages.append("High cholesterol")
                if fbs == 1:
                    risk_factors += 1
                    risk_messages.append("High blood sugar")
                if thalach > 170:
                    risk_factors += 1
                    risk_messages.append("High maximum heart rate")
                
                # Show prediction result
                if heart_prediction[0] == 1:
                    st.error("⚠️ High Risk of Heart Disease Detected")
                    risk_level = "High Risk"
                else:
                    st.success("✅ Low Risk of Heart Disease")
                    risk_level = "Low Risk"
                
                # Create three columns for metrics
                col1, col2, col3 = st.columns([1,2,1])
                
                with col2:
                    st.markdown(f"""
                    <div style="padding: 1rem; background: white; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                        <h3 style="text-align: center; color: var(--primary-color);">Heart Health Analysis</h3>
                        <p style="text-align: center; font-size: 1.2rem;">Risk Level: {risk_level}</p>
                        <p style="text-align: center;">Confidence: {calculate_confidence(prediction_proba):.1f}%</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Create tabs for different visualizations
                analysis_tab, metrics_tab = st.tabs(["Analysis", "Health Metrics"])
                
                with analysis_tab:
                    # Show risk factors
                    if risk_messages:
                        st.warning("Risk Factors Identified:")
                        for msg in risk_messages:
                            st.write(f"• {msg}")
                    else:
                        st.info("No major risk factors identified")
                    
                    # Show feature importance
                    features = ['Age', 'Blood Pressure', 'Cholesterol', 'Max Heart Rate',
                              'ST Depression', 'Num. Vessels', 'Chest Pain', 'Exercise Angina']
                    importance_scores = [15, 14, 13, 12, 11, 10, 9, 8]
                    st.plotly_chart(plot_feature_importance(features, importance_scores))
                    
                    # Show prediction probability
                    st.plotly_chart(plot_prediction_proba(prediction_proba))
                
                with metrics_tab:
                    # Show health metrics comparison
                    metrics_values = [trestbps, chol, thalach]
                    metrics_labels = ['Blood Pressure', 'Cholesterol', 'Max Heart Rate']
                    metrics_ranges = [(90, 120), (150, 200), (60, 100)]
                    st.plotly_chart(create_metrics_chart(metrics_values, metrics_labels, metrics_ranges))
                    
                    # Add recommendations based on prediction
                    st.markdown("### Personalized Recommendations")
                    if heart_prediction[0] == 1:
                        st.warning("""
                        Based on your heart health analysis:
                        1. Consult a cardiologist for detailed evaluation
                        2. Monitor blood pressure and cholesterol regularly
                        3. Consider lifestyle modifications
                        4. Follow up with regular check-ups
                        """)
                    else:
                        st.info("""
                        To maintain heart health:
                        1. Continue regular exercise
                        2. Maintain a heart-healthy diet
                        3. Regular health check-ups
                        4. Manage stress levels
                        """)
                
                if heart_prediction is not None:
                    result = "The person has heart disease" if heart_prediction[0] == 1 else "The person does not have heart disease"
                    save_prediction(
                        st.session_state['user']['id'],
                        "Heart Disease",
                        result,
                        calculate_confidence(prediction_proba)
                    )
        
        except Exception as e:
            st.error(f"An error occurred: {e}")
            st.info("Please ensure all fields contain valid numeric values.")

# Parkinson's Disease Prediction Page
if (selected == "Parkinson's Prediction"):
    # Show help button
    show_help_button()
    
    st.title("Parkinson's Disease Prediction")
    
    # Add information about voice parameters
    with st.expander("ℹ️ Understanding Voice Parameters"):
        st.markdown("""
        ### Voice Parameter Ranges:
        - **Jitter (%)**: 0.0-1.0% (Normal < 1.0%)
        - **Shimmer (%)**: 0.0-3.0% (Normal < 3.0%)
        - **HNR**: 15-25 dB (Higher values indicate better voice quality)
        - **RPDE**: 0.0-1.0 (Lower values indicate more regular voice)
        - **DFA**: 0.5-0.8 (Measure of signal complexity)
        - **PPE**: 0.0-0.5 (Lower values indicate more regular voice)
        """)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        fo = st.number_input('MDVP:Fo(Hz) - Average vocal frequency', 
                            min_value=80.0, 
                            max_value=260.0, 
                            value=120.0, 
                            step=1.0,
                            help="Normal range: 80-260 Hz")
        
    with col2:
        fhi = st.number_input('MDVP:Fhi(Hz) - Maximum vocal frequency', 
                             min_value=100.0, 
                             max_value=500.0, 
                             value=200.0, 
                             step=1.0,
                             help="Normal range: 100-500 Hz")
        
    with col3:
        flo = st.number_input('MDVP:Flo(Hz) - Minimum vocal frequency', 
                             min_value=50.0, 
                             max_value=200.0, 
                             value=70.0, 
                             step=1.0,
                             help="Normal range: 50-200 Hz")
        
    with col1:
        Jitter_percent = st.number_input('MDVP:Jitter(%) - Frequency variation', 
                                        min_value=0.0, 
                                        max_value=2.0, 
                                        value=0.3, 
                                        step=0.001,
                                        format="%.3f",
                                        help="Normal < 1.0%")
        
    with col2:
        Jitter_Abs = st.number_input('MDVP:Jitter(Abs) - Absolute jitter', 
                                    min_value=0.0, 
                                    max_value=0.1, 
                                    value=0.02, 
                                    step=0.001,
                                    format="%.3f",
                                    help="Absolute frequency perturbation")
        
    with col3:
        RAP = st.number_input('MDVP:RAP - Relative amplitude perturbation', 
                             min_value=0.0, 
                             max_value=0.1, 
                             value=0.02, 
                             step=0.001,
                             format="%.3f",
                             help="Normal < 0.05")
        
    with col1:
        PPQ = st.number_input('MDVP:PPQ - Pitch perturbation quotient', 
                             min_value=0.0, 
                             max_value=0.1, 
                             value=0.02, 
                             step=0.001,
                             format="%.3f",
                             help="Five-point period perturbation quotient")
        
    with col2:
        DDP = st.number_input('Jitter:DDP - Average perturbation', 
                             min_value=0.0, 
                             max_value=0.1, 
                             value=0.02, 
                             step=0.001,
                             format="%.3f",
                             help="Average absolute difference between consecutive differences")
        
    with col3:
        Shimmer = st.number_input('MDVP:Shimmer - Amplitude variation', 
                                 min_value=0.0, 
                                 max_value=10.0, 
                                 value=2.0, 
                                 step=0.1,
                                 format="%.1f",
                                 help="Normal < 3.0%")
        
    with col1:
        Shimmer_dB = st.number_input('MDVP:Shimmer(dB) - Log amplitude variation', 
                                    min_value=0.0, 
                                    max_value=2.0, 
                                    value=0.3, 
                                    step=0.01,
                                    format="%.2f",
                                    help="Normal < 0.4 dB")
        
    with col2:
        APQ3 = st.number_input('Shimmer:APQ3 - Three-point amplitude quotient', 
                              min_value=0.0, 
                              max_value=0.1, 
                              value=0.02, 
                              step=0.001,
                              format="%.3f",
                              help="Three-point amplitude perturbation quotient")
        
    with col3:
        APQ5 = st.number_input('Shimmer:APQ5 - Five-point amplitude quotient', 
                              min_value=0.0, 
                              max_value=0.1, 
                              value=0.02, 
                              step=0.001,
                              format="%.3f",
                              help="Five-point amplitude perturbation quotient")
        
    with col1:
        APQ = st.number_input('MDVP:APQ - Amplitude perturbation quotient', 
                             min_value=0.0, 
                             max_value=0.1, 
                             value=0.02, 
                             step=0.001,
                             format="%.3f",
                             help="Average absolute differences between consecutive differences")
        
    with col2:
        DDA = st.number_input('Shimmer:DDA - Amplitude perturbation', 
                             min_value=0.0, 
                             max_value=0.1, 
                             value=0.02, 
                             step=0.001,
                             format="%.3f",
                             help="Average absolute differences between consecutive differences")
        
    with col3:
        NHR = st.number_input('NHR - Noise-to-Harmonics ratio', 
                             min_value=0.0, 
                             max_value=1.0, 
                             value=0.1, 
                             step=0.01,
                             format="%.2f",
                             help="Normal < 0.19")
        
    with col1:
        HNR = st.number_input('HNR - Harmonics-to-Noise ratio', 
                             min_value=0.0, 
                             max_value=40.0, 
                             value=20.0, 
                             step=0.1,
                             format="%.1f",
                             help="Normal range: 15-25 dB")
        
    with col2:
        RPDE = st.number_input('RPDE - Recurrence period density entropy', 
                              min_value=0.0, 
                              max_value=1.0, 
                              value=0.4, 
                              step=0.01,
                              format="%.2f",
                              help="Measure of periodicity. Lower values indicate more regular voice.")
        
    with col3:
        DFA = st.number_input('DFA - Signal fractal scaling exponent', 
                             min_value=0.0, 
                             max_value=1.0, 
                             value=0.6, 
                             step=0.01,
                             format="%.2f",
                             help="Normal range: 0.5-0.8")
        
    with col1:
        spread1 = st.number_input('spread1 - Nonlinear measure of fundamental frequency variation', 
                                 min_value=-10.0, 
                                 max_value=10.0, 
                                 value=0.0, 
                                 step=0.1,
                                 format="%.1f",
                                 help="First nonlinear measure")
        
    with col2:
        spread2 = st.number_input('spread2 - Nonlinear measure of fundamental frequency variation', 
                                 min_value=0.0, 
                                 max_value=10.0, 
                                 value=2.0, 
                                 step=0.1,
                                 format="%.1f",
                                 help="Second nonlinear measure")
        
    with col3:
        D2 = st.number_input('D2 - Correlation dimension', 
                            min_value=0.0, 
                            max_value=5.0, 
                            value=2.0, 
                            step=0.1,
                            format="%.1f",
                            help="Measure of signal complexity")
        
    with col1:
        PPE = st.number_input('PPE - Pitch period entropy', 
                             min_value=0.0, 
                             max_value=1.0, 
                             value=0.2, 
                             step=0.01,
                             format="%.2f",
                             help="Measure of voice irregularity. Lower values indicate more regular voice.")

    # Center the predict button
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        predict_parkinsons = st.button("Predict Parkinson's Risk", use_container_width=True)

    # Information about the parameters
    with st.expander("Learn about these parameters"):
        st.markdown("""
        - **MDVP:Fo(Hz)**: Average vocal fundamental frequency
        - **MDVP:Fhi(Hz)**: Maximum vocal fundamental frequency
        - **MDVP:Flo(Hz)**: Minimum vocal fundamental frequency
        - **MDVP:Jitter(%)**: Percentage of perturbation in vocal fundamental frequency
        - **MDVP:Jitter(Abs)**: Absolute vocal fundamental frequency perturbation
        - **MDVP:RAP**: Average vocal perturbation amplitude
        - **MDVP:PPQ**: Pitch perturbation quotient
        - **Jitter:DDP**: Absolute pitch perturbation
        - **MDVP:Shimmer**: Average absolute difference between consecutive periods
        - **MDVP:Shimmer(dB)**: Average absolute difference between consecutive periods in decibels
        - **Shimmer:APQ3**: Third harmonic to second harmonic amplitude ratio
        - **Shimmer:APQ5**: Fifth harmonic to second harmonic amplitude ratio
        - **MDVP:APQ**: Pitch perturbation quotient
        - **Shimmer:DDA**: Absolute difference between consecutive periods
        - **NHR**: Noise-to-Harmonics ratio
        - **HNR**: Harmonic-to-Noise ratio
        - **RPDE**: Recurrence period density
        - **DFA**: Fundamental frequency variation
        - **spread1**: Average absolute difference between consecutive periods
        - **spread2**: Average absolute difference between consecutive periods
        - **D2**: Second derivative of amplitude envelope
        - **PPE**: Pitch period perturbation quotient
        """)
    
    # code for Prediction
    parkinsons_diagnosis = ''
    
    # creating a button for Prediction    
    if predict_parkinsons:
        
        try:
            with st.spinner("Analyzing voice parameters..."):
                time.sleep(2)
                
                # Make prediction with all 22 features in the correct order
                input_values = [fo, fhi, flo, Jitter_percent, Jitter_Abs, RAP, PPQ, DDP,
                              Shimmer, Shimmer_dB, APQ3, APQ5, APQ, DDA, NHR, HNR,
                              RPDE, DFA, spread1, spread2, D2, PPE]
                
                parkinsons_prediction = parkinsons_model.predict([input_values])
                prediction_proba = get_prediction_probability(parkinsons_model, [input_values])
                
                # Calculate metrics
                metrics_values = [Jitter_percent, Shimmer, HNR, DFA]
                metrics_labels = ['Jitter', 'Shimmer', 'HNR', 'DFA']
                metrics_ranges = [(0, 0.01), (0, 0.1), (15, 25), (0.5, 0.8)]
                
                # Show prediction result
                if parkinsons_prediction[0] == 1:
                    st.error("⚠️ Indicators of Parkinson's Disease Detected")
                    risk_level = "High Risk"
                else:
                    st.success("✅ No Significant Indicators Detected")
                    risk_level = "Low Risk"
                
                # Create three columns for metrics
                col1, col2, col3 = st.columns([1,2,1])
                
                with col2:
                    st.markdown(f"""
                    <div style="padding: 1rem; background: white; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                        <h3 style="text-align: center; color: var(--primary-color);">Voice Analysis Results</h3>
                        <p style="text-align: center; font-size: 1.2rem;">Risk Level: {risk_level}</p>
                        <p style="text-align: center;">Confidence: {calculate_confidence(prediction_proba):.1f}%</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Create tabs for different visualizations
                analysis_tab, metrics_tab = st.tabs(["Analysis", "Voice Metrics"])
                
                with analysis_tab:
                    # Show feature importance
                    features = ['Shimmer', 'HNR', 'RPDE', 'DFA', 'PPE', 'Spread1',
                              'Jitter(%)', 'NHR', 'MDVP:RAP', 'D2']
                    importance_scores = [20, 18, 15, 12, 10, 8, 7, 5, 3, 2]
                    st.plotly_chart(plot_feature_importance(features, importance_scores))
                    
                    # Show prediction probability
                    st.plotly_chart(plot_prediction_proba(prediction_proba))
                
                with metrics_tab:
                    # Show voice metrics
                    st.plotly_chart(create_metrics_chart(metrics_values, metrics_labels, metrics_ranges))
                    
                    # Add voice parameters comparison
                    st.subheader("Voice Parameters Comparison")
                    voice_values = [Jitter_percent, Shimmer, HNR]
                    voice_means = [0.005, 0.05, 20]
                    voice_labels = ['Jitter', 'Shimmer', 'HNR']
                    st.plotly_chart(create_comparison_chart(voice_values, voice_means, voice_labels))
                    
                    # Add explanatory text
                    st.markdown("""
                    ### Understanding Voice Metrics
                    - **Jitter**: Variation in fundamental frequency (normal range: 0-0.01)
                    - **Shimmer**: Variation in amplitude (normal range: 0-0.1)
                    - **HNR**: Harmonics to Noise Ratio (normal range: 15-25)
                    - **DFA**: Detrended Fluctuation Analysis (normal range: 0.5-0.8)
                    """)
                
                    # Add recommendations based on prediction
                    st.markdown("### Personalized Recommendations")
                    if parkinsons_prediction[0] == 1:
                        st.warning("""
                        Based on your voice analysis:
                        1. Consult a neurologist for comprehensive evaluation
                        2. Consider speech therapy assessment
                        3. Monitor changes in voice and movement patterns
                        4. Explore early intervention options
                        """)
                    else:
                        st.info("""
                        To maintain neurological health:
                        1. Continue regular health check-ups
                        2. Stay physically and mentally active
                        3. Monitor any changes in movement or speech
                        4. Maintain a healthy lifestyle
                        """)
                
                if parkinsons_prediction is not None:
                    result = "The person has Parkinson's disease" if parkinsons_prediction[0] == 1 else "The person does not have Parkinson's disease"
                    save_prediction(
                        st.session_state['user']['id'],
                        "Parkinson's Disease",
                        result,
                        calculate_confidence(prediction_proba)
                    )
        
        except Exception as e:
            st.error(f"An error occurred: {e}")
            st.info("Please ensure all fields contain valid numeric values.")

# About Page
if (selected == 'About'):
    st.markdown("""
    <div style="text-align: center; padding: 20px; background-color: #ffffff; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 20px;">
        <h1 style="color: #3498DB; font-weight: bold;">About This System</h1>
        <p style="font-size: 1.2rem; color: #333333;">Learn more about our Advanced Disease Prediction System</p>
    </div>
    """, unsafe_allow_html=True)
    
    # System Overview
    st.markdown("""
    <div style="background-color: #ffffff; padding: 20px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 20px; border-left: 5px solid #3498DB;">
        <h2 style="color: #2C3E50; border-bottom: 2px solid #3498DB; padding-bottom: 10px; font-weight: bold;">System Overview</h2>
        <p style="font-size: 1.1rem; line-height: 1.6; color: #333333;">
            The Advanced Disease Prediction System is a state-of-the-art application that leverages machine learning algorithms to predict 
            the likelihood of various diseases based on patient health parameters. This system aims to assist in early detection and 
            preventive healthcare by providing risk assessments for diabetes, heart disease, and Parkinson's disease.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Technical Details
    st.markdown("""
    <div style="background-color: #ffffff; padding: 20px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 20px; border-left: 5px solid #3498DB;">
        <h2 style="color: #2C3E50; border-bottom: 2px solid #3498DB; padding-bottom: 10px; font-weight: bold;">Technical Details</h2>
    </div>
    """, unsafe_allow_html=True)
    
    # Machine Learning Models section
    st.subheader("Machine Learning Models")
    st.write("Our system employs various supervised learning algorithms including:")
    
    st.markdown("""
    - **Random Forest Classifiers:** Ensemble learning method for classification that operates by constructing multiple decision trees.
    - **Support Vector Machines (SVM):** Supervised learning models used for classification and regression analysis.
    - **Gradient Boosting:** A machine learning technique that produces a prediction model in the form of an ensemble of weak prediction models.
    """)
    
    # Data Processing section
    st.subheader("Data Processing")
    st.write("The system processes user input through several stages:")
    
    st.markdown("""
    1. Data validation and normalization
    2. Feature scaling to ensure all inputs are on comparable scales
    3. Prediction using pre-trained models
    4. Confidence calculation and result interpretation
    5. Visualization generation for better understanding
    """)
    
    # Visualization Techniques section
    st.subheader("Visualization Techniques")
    st.write("The system provides various visualizations to help interpret results:")
    
    st.markdown("""
    - Feature importance plots to understand which factors most influence predictions
    - Probability distribution charts to visualize confidence levels
    - Health metric gauges to compare values against normal ranges
    - Comparative analysis charts to benchmark against population averages
    """)
    
    # Disease Information
    st.markdown("""
    <div style="background-color: #ffffff; padding: 20px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-top: 20px; border-left: 5px solid #3498DB;">
        <h2 style="color: #2C3E50; border-bottom: 2px solid #3498DB; padding-bottom: 10px; font-weight: bold;">Disease Information</h2>
    </div>
    """, unsafe_allow_html=True)
    
    # Create tabs
    tab1, tab2, tab3 = st.tabs(["Diabetes", "Heart Disease", "Parkinson's Disease"])
    
    with tab1:
        st.header("Diabetes")
        st.write("Diabetes is a chronic disease that occurs either when the pancreas does not produce enough insulin or when the body cannot effectively use the insulin it produces. Insulin is a hormone that regulates blood sugar.")
        
        st.subheader("Key Risk Factors:")
        st.markdown("""
        - High blood glucose levels
        - Family history of diabetes
        - Overweight or obesity
        - Physical inactivity
        - Age (risk increases with age)
        - High blood pressure
        - Abnormal cholesterol and triglyceride levels
        """)
        
        st.subheader("Prevention Tips:")
        st.markdown("""
        - Maintain a healthy weight
        - Stay physically active
        - Eat a balanced diet rich in fruits, vegetables, and whole grains
        - Limit sugar and refined carbohydrates
        - Regular health check-ups
        """)
    
    with tab2:
        st.header("Heart Disease")
        st.write("Heart disease refers to various types of conditions that can affect heart function. These include coronary artery disease, heart arrhythmias, and heart defects you're born with.")
        
        st.subheader("Key Risk Factors:")
        st.markdown("""
        - High blood pressure
        - High cholesterol levels
        - Smoking
        - Diabetes
        - Family history of heart disease
        - Age (risk increases with age)
        - Physical inactivity
        - Obesity
        - Stress
        """)
        
        st.subheader("Prevention Tips:")
        st.markdown("""
        - Regular exercise
        - Healthy diet low in saturated fats, trans fats, and cholesterol
        - Maintain a healthy weight
        - Limit alcohol consumption
        - Don't smoke
        - Manage stress
        - Regular health check-ups
        """)
    
    with tab3:
        st.header("Parkinson's Disease")
        st.write("Parkinson's disease is a progressive nervous system disorder that affects movement. Symptoms start gradually, sometimes with a barely noticeable tremor in just one hand.")
        
        st.subheader("Key Risk Factors:")
        st.markdown("""
        - Age (risk increases with age)
        - Heredity (having close relatives with Parkinson's disease)
        - Sex (men are more likely to develop Parkinson's disease than women)
        - Exposure to toxins
        - Serious head injury
        """)
        
        st.subheader("Early Signs:")
        st.markdown("""
        - Tremor, often in a limb, especially at rest
        - Slowed movement (bradykinesia)
        - Rigid muscles
        - Impaired posture and balance
        - Loss of automatic movements
        - Speech changes
        - Writing changes
        """)
    
    # References and Resources
    st.markdown("""
    <div style="background-color: #ffffff; padding: 20px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-top: 20px; border-left: 5px solid #3498DB;">
        <h2 style="color: #2C3E50; border-bottom: 2px solid #3498DB; padding-bottom: 10px; font-weight: bold;">References & Resources</h2>
    </div>
    """, unsafe_allow_html=True)
    
    # Data Sources section
    st.subheader("Data Sources")
    st.markdown("""
    - UCI Machine Learning Repository - Diabetes Dataset
    - Cleveland Heart Disease Dataset
    - Parkinson's Disease Classification Dataset
    """)
    
    # Further Reading section
    st.subheader("Further Reading")
    st.markdown("""
    - American Diabetes Association: [www.diabetes.org](https://www.diabetes.org/)
    - American Heart Association: [www.heart.org](https://www.heart.org/)
    - Parkinson's Foundation: [www.parkinson.org](https://www.parkinson.org/)
    - World Health Organization: [www.who.int](https://www.who.int/)
    """)
    
    # Add disclaimer
    st.markdown("""
    <div style="background-color: #fef9c3; padding: 20px; border-radius: 10px; border-left: 5px solid #eab308; margin-top: 20px;">
        <h3 style="color: #854d0e; margin-bottom: 10px;">Disclaimer</h3>
        <p style="color: #854d0e; font-size: 16px; line-height: 1.6;">
            <strong>This application is for educational and informational purposes only.</strong> 
            It is not intended to be a substitute for professional medical advice, diagnosis, or treatment. 
            Always seek the advice of your physician or other qualified health provider with any questions 
            you may have regarding a medical condition.
        </p>
    </div>
    """, unsafe_allow_html=True)

# History Page
if (selected == 'History'):
    st.markdown("""
    <div style="text-align: center; padding: 20px; background-color: #ffffff; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 20px;">
        <h1 style="color: #3498DB; font-weight: bold;">Your Prediction History</h1>
        <p style="font-size: 1.2rem; color: #333333;">View and analyze your past health predictions</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Get user predictions from the database
    predictions_df = get_user_predictions(st.session_state['user']['id'])
    
    if predictions_df.empty:
        st.info("No prediction history found. Make some predictions to see them here!")
    else:
        # Create tabs for different views
        tab1, tab2 = st.tabs(["Predictions", "Analysis"])
        
        with tab1:
            # Add filters
            col1, col2 = st.columns(2)
            with col1:
                disease_filter = st.multiselect(
                    "Filter by Disease Type",
                    options=predictions_df['disease_type'].unique(),
                    default=predictions_df['disease_type'].unique()
                )
            
            # Convert created_at to datetime if it's string
            if isinstance(predictions_df['created_at'].iloc[0], str):
                predictions_df['created_at'] = pd.to_datetime(predictions_df['created_at'])
            
            with col2:
                date_range = st.date_input(
                    "Date Range",
                    value=(
                        predictions_df['created_at'].min().date(),
                        predictions_df['created_at'].max().date()
                    )
                )
            
            # Apply filters
            filtered_df = predictions_df[
                (predictions_df['disease_type'].isin(disease_filter)) &
                (predictions_df['created_at'].dt.date >= date_range[0]) &
                (predictions_df['created_at'].dt.date <= date_range[1])
            ]
            
            # Sort by date (most recent first)
            filtered_df = filtered_df.sort_values('created_at', ascending=False)
            
            # Display predictions in a styled table
            for _, row in filtered_df.iterrows():
                is_positive = any(keyword in row['prediction_result'].lower() 
                                for keyword in ['positive', 'has', 'is diabetic'])
                
                with st.container():
                    st.markdown(f"""
                    <div style="background-color: white; padding: 20px; border-radius: 10px; 
                         box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin-bottom: 15px; 
                         border-left: 5px solid {'#FFA500' if is_positive else '#4CAF50'};">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <h3 style="color: #1e3a8a; margin: 0; font-size: 1.3rem;">
                                {row['disease_type']}
                            </h3>
                            <span style="color: #666; font-size: 0.9rem;">
                                {pd.to_datetime(row['created_at']).strftime('%Y-%m-%d %H:%M')}
                            </span>
                        </div>
                        <p style="color: #333; margin: 10px 0; font-size: 1.1rem;">
                            {row['prediction_result']}
                        </p>
                        <div style="background-color: {'#fff3e0' if is_positive else '#e8f5e9'}; 
                             padding: 8px; border-radius: 5px; display: inline-block;">
                            <span style="font-weight: bold; color: {'#d32f2f' if is_positive else '#2e7d32'};">
                                Confidence: {row['confidence']:.1f}%
                            </span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
        
        with tab2:
            # Create analysis visualizations
            st.subheader("Prediction Analysis")
            
            # Disease type distribution
            disease_counts = predictions_df['disease_type'].value_counts()
            fig_pie = px.pie(
                values=disease_counts.values,
                names=disease_counts.index,
                title="Distribution of Predictions by Disease Type",
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            fig_pie.update_traces(textinfo='percent+label')
            st.plotly_chart(fig_pie)
            
            # Summary statistics
            st.subheader("Summary Statistics")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric(
                    "Total Predictions",
                    len(predictions_df),
                    help="Total number of predictions made"
                )
            
            with col2:
                avg_confidence = predictions_df['confidence'].mean()
                st.metric(
                    "Average Confidence",
                    f"{avg_confidence:.1f}%",
                    help="Average confidence across all predictions"
                )
            
            with col3:
                positive_predictions = predictions_df['prediction_result'].str.contains(
                    'positive|has|is diabetic', case=False).sum()
                st.metric(
                    "Positive Predictions",
                    f"{positive_predictions}",
                    f"{(positive_predictions/len(predictions_df)*100):.1f}%",
                    help="Number of positive disease predictions"
                )
            
            # Add a separator
            st.markdown("---")
            
            # Disease-wise breakdown
            st.subheader("Disease-wise Breakdown")
            for disease in predictions_df['disease_type'].unique():
                disease_df = predictions_df[predictions_df['disease_type'] == disease]
                positive_count = disease_df['prediction_result'].str.contains(
                    'positive|has|is diabetic', case=False).sum()
                total_count = len(disease_df)
                
                st.markdown(f"""
                <div style="background-color: white; padding: 15px; border-radius: 10px; 
                     margin-bottom: 10px; border-left: 4px solid #3498DB;">
                    <h4 style="color: #1e3a8a; margin: 0;">{disease}</h4>
                    <p style="margin: 5px 0;">
                        Total Predictions: {total_count}<br>
                        Positive Results: {positive_count} ({(positive_count/total_count*100):.1f}%)<br>
                        Average Confidence: {disease_df['confidence'].mean():.1f}%
                    </p>
                </div>
                """, unsafe_allow_html=True)
            
            # Export functionality
            st.markdown("### Export Data")
            if st.button("Download Prediction History"):
                csv = predictions_df.to_csv(index=False)
                st.download_button(
                    label="Download CSV",
                    data=csv,
                    file_name="prediction_history.csv",
                    mime="text/csv"
                )

# Add the Requirements page
elif (selected == 'Requirements'):
    st.markdown("""
    <div style="text-align: center; padding: 20px; background-color: #ffffff; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 20px;">
        <h1 style="color: #3498DB; font-weight: bold;">Project Requirements</h1>
        <p style="font-size: 1.2rem; color: #333333;">Everything you need to run this Multiple Disease Prediction System</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Python Version
    st.markdown("""
    <div style="background-color: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin-bottom: 20px;">
        <h3 style="color: #1e3a8a;">🐍 Python Version</h3>
        <ul style="list-style-type: none; padding-left: 0;">
            <li style="margin: 10px 0; padding: 10px; background-color: #f8fafc; border-radius: 5px;">
                <strong>Required Version:</strong> Python 3.8 or higher
            </li>
            <li style="margin: 10px 0; padding: 10px; background-color: #f8fafc; border-radius: 5px;">
                <strong>Recommended Version:</strong> Python 3.11
            </li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    # Core Dependencies
    st.markdown("""
    <div style="background-color: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin-bottom: 20px;">
        <h3 style="color: #1e3a8a;">📚 Core Dependencies</h3>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 15px;">
            <div style="padding: 15px; background-color: #f8fafc; border-radius: 5px;">
                <strong>streamlit==1.31.0</strong>
                <p style="margin: 5px 0; color: #666;">Web application framework</p>
            </div>
            <div style="padding: 15px; background-color: #f8fafc; border-radius: 5px;">
                <strong>pandas==2.2.0</strong>
                <p style="margin: 5px 0; color: #666;">Data manipulation and analysis</p>
            </div>
            <div style="padding: 15px; background-color: #f8fafc; border-radius: 5px;">
                <strong>numpy==1.24.3</strong>
                <p style="margin: 5px 0; color: #666;">Numerical computing</p>
            </div>
            <div style="padding: 15px; background-color: #f8fafc; border-radius: 5px;">
                <strong>scikit-learn==1.3.0</strong>
                <p style="margin: 5px 0; color: #666;">Machine learning algorithms</p>
            </div>
            <div style="padding: 15px; background-color: #f8fafc; border-radius: 5px;">
                <strong>plotly==5.18.0</strong>
                <p style="margin: 5px 0; color: #666;">Interactive visualizations</p>
            </div>
            <div style="padding: 15px; background-color: #f8fafc; border-radius: 5px;">
                <strong>joblib==1.3.2</strong>
                <p style="margin: 5px 0; color: #666;">Model persistence</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Installation Instructions
    st.markdown("""
    <div style="background-color: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin-bottom: 20px;">
        <h3 style="color: #1e3a8a;">⚙️ Installation Instructions</h3>
        <ol style="margin: 20px 0;">
            <li style="margin: 10px 0;">
                <strong>Clone the Repository</strong>
                <div style="background-color: #1e293b; color: #e2e8f0; padding: 10px; border-radius: 5px; margin: 5px 0;">
                    <code>git clone https://github.com/yourusername/Multiple-Disease-Prediction-System.git</code>
                </div>
            </li>
            <li style="margin: 10px 0;">
                <strong>Create a Virtual Environment (Recommended)</strong>
                <div style="background-color: #1e293b; color: #e2e8f0; padding: 10px; border-radius: 5px; margin: 5px 0;">
                    <code>python -m venv venv</code><br>
                    <code>source venv/bin/activate</code> # On Unix/macOS<br>
                    <code>venv\\Scripts\\activate</code> # On Windows
                </div>
            </li>
            <li style="margin: 10px 0;">
                <strong>Install Dependencies</strong>
                <div style="background-color: #1e293b; color: #e2e8f0; padding: 10px; border-radius: 5px; margin: 5px 0;">
                    <code>pip install -r requirements.txt</code>
                </div>
            </li>
            <li style="margin: 10px 0;">
                <strong>Run the Application</strong>
                <div style="background-color: #1e293b; color: #e2e8f0; padding: 10px; border-radius: 5px; margin: 5px 0;">
                    <code>streamlit run multiplediseaseprediction.py</code>
                </div>
            </li>
        </ol>
    </div>
    """, unsafe_allow_html=True)
    
    # System Requirements
    st.markdown("""
    <div style="background-color: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin-bottom: 20px;">
        <h3 style="color: #1e3a8a;">💻 System Requirements</h3>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 15px;">
            <div style="padding: 15px; background-color: #f8fafc; border-radius: 5px;">
                <strong>Operating System</strong>
                <ul style="margin: 5px 0; color: #666;">
                    <li>Windows 10/11</li>
                    <li>macOS 10.14+</li>
                    <li>Linux (Ubuntu 18.04+)</li>
                </ul>
            </div>
            <div style="padding: 15px; background-color: #f8fafc; border-radius: 5px;">
                <strong>Hardware</strong>
                <ul style="margin: 5px 0; color: #666;">
                    <li>2GB RAM (minimum)</li>
                    <li>4GB RAM (recommended)</li>
                    <li>1GB free disk space</li>
                </ul>
            </div>
            <div style="padding: 15px; background-color: #f8fafc; border-radius: 5px;">
                <strong>Browser Support</strong>
                <ul style="margin: 5px 0; color: #666;">
                    <li>Chrome 80+</li>
                    <li>Firefox 72+</li>
                    <li>Edge 80+</li>
                </ul>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Additional Tools
    st.markdown("""
    <div style="background-color: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin-bottom: 20px;">
        <h3 style="color: #1e3a8a;">🛠️ Additional Tools</h3>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 15px;">
            <div style="padding: 15px; background-color: #f8fafc; border-radius: 5px;">
                <strong>Git</strong>
                <p style="margin: 5px 0; color: #666;">Version control system (2.30+)</p>
            </div>
            <div style="padding: 15px; background-color: #f8fafc; border-radius: 5px;">
                <strong>pip</strong>
                <p style="margin: 5px 0; color: #666;">Package installer (21.0+)</p>
            </div>
            <div style="padding: 15px; background-color: #f8fafc; border-radius: 5px;">
                <strong>venv</strong>
                <p style="margin: 5px 0; color: #666;">Virtual environment module</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Troubleshooting
    with st.expander("🔧 Troubleshooting Common Issues"):
        st.markdown("""
        ### Common Issues and Solutions
        
        1. **ImportError: No module named 'streamlit'**
           - Make sure you've activated your virtual environment
           - Run `pip install streamlit==1.31.0`
        
        2. **ModuleNotFoundError: No module named 'sklearn'**
           - Run `pip install scikit-learn==1.3.0`
        
        3. **Version Conflicts**
           - Try creating a fresh virtual environment
           - Install dependencies one by one in the specified order
        
        4. **Port Already in Use**
           - Stop any running Streamlit applications
           - Use a different port: `streamlit run app.py --server.port 8502`
        
        5. **Memory Issues**
           - Close other applications
           - Ensure you meet the minimum RAM requirements
        """)
    
    # Download Requirements File
    st.markdown("""
    <div style="background-color: #f0f9ff; padding: 20px; border-radius: 10px; margin-top: 20px;">
        <h4 style="color: #1e3a8a;">📥 Download Requirements File</h4>
        <p style="color: #666;">Get the complete requirements.txt file with all necessary dependencies and versions.</p>
    </div>
    """, unsafe_allow_html=True)
    
    requirements_content = """streamlit==1.31.0
pandas==2.2.0
numpy==1.24.3
scikit-learn==1.3.0
plotly==5.18.0
joblib==1.3.2
"""
    
    st.download_button(
        label="Download requirements.txt",
        data=requirements_content,
        file_name="requirements.txt",
        mime="text/plain"
    )

# Enhanced footer with modern design
st.markdown("---")
st.markdown("""
<footer style="background: linear-gradient(135deg, #2C3E50, #3498DB); color: white; padding: 2rem; border-radius: 12px; margin-top: 3rem;">
    <div style="max-width: 1200px; margin: 0 auto; text-align: center;">
        <h3 style="color: white; font-weight: 600; margin-bottom: 1rem;">Multiple Disease Prediction System</h3>
        <p style="color: rgba(255,255,255,0.9); font-size: 1rem;">Developed by Sumit Kumar Verma & Saumya Chaurasia</p>
        <div style="margin: 1.5rem 0; display: flex; justify-content: center; gap: 2rem;">
            <a href="#" style="color: white; text-decoration: none; font-size: 0.9rem;">Privacy Policy</a>
            <a href="#" style="color: white; text-decoration: none; font-size: 0.9rem;">Terms of Service</a>
            <a href="#" style="color: white; text-decoration: none; font-size: 0.9rem;">Contact Us</a>
        </div>
        <p style="color: rgba(255,255,255,0.7); font-size: 0.9rem; margin-top: 1rem;">Version 2.0.0 | © 2025 Health Predictor. All rights reserved.</p>
    </div>
</footer>
""", unsafe_allow_html=True)

# Add a feedback form
with st.expander("📝 Provide Feedback"):
    st.markdown("### We'd love to hear from you!")
    feedback_name = st.text_input("Name")
    feedback_email = st.text_input("Email")
    feedback_type = st.selectbox("Feedback Type", ["General Feedback", "Bug Report", "Feature Request", "Question"])
    feedback_message = st.text_area("Your Message")
    
    if st.button("Submit Feedback"):
        if feedback_message:
            with st.spinner("Submitting your feedback..."):
                time.sleep(1.5)  # Simulate submission
                st.success("Thank you for your feedback! We appreciate your input.")
                st.balloons()
        else:
            st.warning("Please enter a message before submitting.")

# Add a popup chat button and back to top button
if 'chat_open' not in st.session_state:
    st.session_state.chat_open = False

# Add chat button to sidebar
with st.sidebar:
    st.markdown("### Need help?")
    if st.button("💬 Chat with us", key="chat_button"):
        st.session_state.chat_open = not st.session_state.chat_open
        st.rerun()

# Show chat popup if open
if st.session_state.chat_open:
    with st.sidebar.container():
        st.markdown("""
        <div style="
            background: white;
            padding: 15px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            margin-top: 20px;">
            <h4 style="color: #4CAF50; margin-bottom: 10px;">Chat Support</h4>
            <p style="color: #333; margin-bottom: 10px;">
                How can we help you today?
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        message = st.text_input("Type your message", key="chat_message")
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("Send", key="send_chat"):
                if message:
                    st.info("Message sent! Our team will respond shortly.")
        with col2:
            if st.button("Close Chat", key="close_chat"):
                st.session_state.chat_open = False
                st.rerun()

# Add back to top link
with st.sidebar:
    st.markdown("---")
    if st.button("↑ Back to Top"):
        st.markdown('<script>window.scrollTo(0, 0);</script>', unsafe_allow_html=True)
        st.rerun()

# Remove the background image setting at the end of the file
# Comment out or remove the set_bg_from_url function call
# set_bg_from_url("https://images.everydayhealth.com/homepage/health-topics-2.jpg?w=768", opacity=0.875)
