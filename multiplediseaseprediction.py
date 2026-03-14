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
    """Show an animated full-width result banner."""
    if is_positive:
        bg   = "linear-gradient(135deg, #450a0a 0%, #7f1d1d 55%, #991b1b 100%)"
        border_color = "rgba(239, 68, 68, 0.60)"
        glow  = "0 0 0 1px rgba(239,68,68,0.18), 0 24px 60px rgba(185, 28, 28, 0.28)"
        icon  = "⚠️"
        badge = "HIGH RISK"
        badge_bg = "rgba(239,68,68,0.22)"
        badge_color = "#fca5a5"
        text_color = "#fff1f1"
        anim = "pulseBorder 2.2s ease-in-out infinite"
        extra_css = """
            @keyframes pulseBorder {
                0%, 100% { box-shadow: 0 0 0 1px rgba(239,68,68,0.18), 0 24px 60px rgba(185,28,28,0.28); }
                50%       { box-shadow: 0 0 0 4px rgba(239,68,68,0.30), 0 28px 70px rgba(185,28,28,0.38); }
            }"""
    else:
        bg   = "linear-gradient(135deg, #052e16 0%, #14532d 55%, #166534 100%)"
        border_color = "rgba(34, 197, 94, 0.50)"
        glow  = "0 0 0 1px rgba(34,197,94,0.18), 0 24px 60px rgba(22, 101, 52, 0.28)"
        icon  = "✅"
        badge = "LOW RISK"
        badge_bg = "rgba(34,197,94,0.18)"
        badge_color = "#86efac"
        text_color = "#f0fdf4"
        anim = "shimmerResult 2.8s linear infinite"
        extra_css = """
            @keyframes shimmerResult {
                0%   { background-position: -600px 0; }
                100% { background-position: 600px 0; }
            }"""

    conf_pct = min(100, max(0, confidence))
    conf_bar_color = "#86efac" if not is_positive else "#fca5a5"

    st.markdown(f"""
<style>
    {extra_css}
    .result-banner {{
        animation: riseIn 0.45s ease both;
    }}
</style>
<div class="result-banner" style="
        background: {bg};
        border: 1px solid {border_color};
        border-radius: 20px;
        padding: 22px 26px;
        margin: 16px 0 20px;
        box-shadow: {glow};
        animation: riseIn 0.45s ease both;
    ">
<div style="display:flex; align-items:center; justify-content:space-between; flex-wrap:wrap; gap:1rem;">
<div style="display:flex; align-items:center; gap:0.75rem;">
<span style="font-size:2rem; line-height:1;">{icon}</span>
<div>
<span style="
                        display:inline-block;
                        background:{badge_bg};
                        color:{badge_color};
                        border:1px solid {badge_color}33;
                        border-radius:999px;
                        padding:0.25rem 0.75rem;
                        font-size:0.7rem;
                        font-weight:800;
                        letter-spacing:0.10em;
                        text-transform:uppercase;
                        margin-bottom:6px;
                    ">{badge}</span>
<p style="margin:0; color:{text_color}; font-size:1.3rem; font-weight:700; font-family:'Space Grotesk',sans-serif; letter-spacing:-0.02em;">{diagnosis}</p>
</div>
</div>
<div style="text-align:right;">
<p style="margin:0 0 6px; color:{badge_color}; font-size:0.78rem; font-weight:700; letter-spacing:0.06em; text-transform:uppercase;">Model Confidence</p>
<p style="margin:0; color:{text_color}; font-size:2rem; font-weight:800; font-family:'Space Grotesk',sans-serif; letter-spacing:-0.04em;">{confidence:.1f}%</p>
<div style="margin-top:6px; height:6px; border-radius:6px; background:rgba(255,255,255,0.12); overflow:hidden;">
<div style="height:100%; width:{conf_pct}%; background:{conf_bar_color}; border-radius:6px; transition:width 0.6s ease;"></div>
</div>
</div>
</div>
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
        margin={"l": 20, "r": 20, "t": 40, "b": 20},
        title_font={"size": 20, "color": '#1e3a8a'},
        font={"family": 'Segoe UI, Arial, sans-serif', "color": '#333333'},
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
        title={"text": "Prediction Probability", "font": {"size": 24, "color": '#1e3a8a'}},
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
        title_font={"size": 20, "color": '#1e3a8a'},
        xaxis={"title": {"text": "Metrics", "font": {"size": 14}}, "tickfont": {"size": 12}},
        yaxis={"title": {"text": "Value", "font": {"size": 14}}, "tickfont": {"size": 12}}
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
            line={"color": '#1e40af', "width": 2}
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
        margin={"l": 20, "r": 20, "t": 50, "b": 20},
        title_font={"size": 18, "color": '#1e3a8a'},
        font={"family": 'Segoe UI, Arial, sans-serif', "color": '#333333'},
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
        title_font={"size": 18, "color": '#1e3a8a'},
        xaxis={"title": {"text": "Metrics", "font": {"size": 14}}, "tickfont": {"size": 12}},
        yaxis={"title": {"text": "Value", "font": {"size": 14}}, "tickfont": {"size": 12}},
        height=350,
        margin={"l": 20, "r": 20, "t": 50, "b": 20},
        font={"family": 'Segoe UI, Arial, sans-serif', "color": '#333333'},
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
        line={"color": '#3b82f6', "width": 2}
    ))
    
    # Customize layout
    fig.update_layout(
        title=f"{y_label} vs {x_label}",
        title_font={"size": 18, "color": '#1e3a8a'},
        xaxis={"title": {"text": x_label, "font": {"size": 14}}, "tickfont": {"size": 12}},
        yaxis={"title": {"text": y_label, "font": {"size": 14}}, "tickfont": {"size": 12}},
        height=300,
        margin=dict(l=20, r=20, t=50, b=20),
        font=dict(family='Segoe UI, Arial, sans-serif', color='#333333')
    )
    
    return fig

# Load the saved models
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

try:
    diabetes_model = pickle.load(open(os.path.join(BASE_DIR, 'diabetes_model.sav'), 'rb'))
except Exception as e:
    st.error(f"Error loading diabetes model: {str(e)}")
    diabetes_model = DummyModel("Diabetes")

try:
    heart_disease_model = pickle.load(open(os.path.join(BASE_DIR, 'heart_disease_model.sav'), 'rb'))
except Exception as e:
    st.error(f"Error loading heart disease model: {str(e)}")
    heart_disease_model = DummyModel("Heart Disease")

try:
    parkinsons_model = pickle.load(open(os.path.join(BASE_DIR, 'parkinsons_model.sav'), 'rb'))
except Exception as e:
    st.error(f"Error loading parkinsons model: {str(e)}")
    parkinsons_model = DummyModel("Parkinsons")

# Set page configuration with light background and dark text
st.set_page_config(
    page_title="Health AI - Disease Prediction",
    page_icon="H",
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
    html, body, .stApp, [data-testid="stAppViewContainer"] {
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

# Lightweight baseline styles. Page-level themes are applied later.
st.markdown("""
<style>
    body {
        color: #0f172a;
        background-color: #f4f8fb;
    }

    .stApp {
        background-color: #f4f8fb;
    }

    [data-testid="stText"],
    [data-testid="stMarkdown"] {
        color: inherit;
    }

    .js-plotly-plot .plotly text {
        fill: #102033 !important;
    }
</style>
""", unsafe_allow_html=True)

def apply_interface_theme():
    """Apply a cohesive interface theme after authentication."""
    st.markdown("""
<style>
        @import url('https://fonts.googleapis.com/css2?family=Manrope:wght@500;600;700;800&family=Source+Sans+3:wght@400;500;600&display=swap');

        :root {
            --bg-top: #f1f8f6;
            --bg-bottom: #dfeee8;
            --surface: #ffffff;
            --surface-soft: #f3faf7;
            --ink: #1b2b36;
            --muted: #5b7280;
            --brand: #0f766e;
            --brand-strong: #115e59;
            --accent: #f59e0b;
            --line: #d4e6df;
            --shadow-soft: 0 10px 30px rgba(16, 36, 46, 0.08);
            --shadow-card: 0 16px 45px rgba(16, 36, 46, 0.11);
        }

        .stApp {
            color: var(--ink);
            background:
                radial-gradient(circle at 12% 14%, rgba(15, 118, 110, 0.12), transparent 42%),
                radial-gradient(circle at 84% 20%, rgba(245, 158, 11, 0.16), transparent 36%),
                linear-gradient(180deg, var(--bg-top) 0%, var(--bg-bottom) 100%);
            min-height: 100vh;
        }

        html, body, .stApp, [data-testid="stAppViewContainer"] {
            font-family: 'Source Sans 3', sans-serif;
        }

        h1, h2, h3, h4, h5, h6 {
            font-family: 'Manrope', sans-serif !important;
            color: var(--ink) !important;
            letter-spacing: -0.02em;
        }

        .main .block-container {
            max-width: 1240px;
            padding-top: 1.25rem;
            padding-right: 1.3rem;
            padding-left: 1.3rem;
            padding-bottom: 2.5rem;
        }

        @media (max-width: 900px) {
            .main .block-container {
                padding-right: 0.8rem;
                padding-left: 0.8rem;
                padding-top: 0.9rem;
                padding-bottom: 2rem;
            }
        }

        [data-testid="stSidebar"] {
            background: linear-gradient(165deg, #ffffff 0%, #eef8f4 50%, #e4f2ec 100%);
            border-right: 1px solid var(--line);
        }

        [data-testid="stSidebar"] .block-container {
            padding-top: 1.05rem;
            padding-right: 0.7rem;
            padding-left: 0.7rem;
        }

        .brand-card {
            background: linear-gradient(145deg, #0f766e 0%, #0ea5a0 62%, #14b8a6 100%);
            color: #f4fffd;
            border-radius: 16px;
            padding: 16px 14px;
            box-shadow: var(--shadow-card);
            margin-bottom: 14px;
            animation: riseIn .45s ease both;
        }

        .brand-card .eyebrow {
            margin: 0 0 4px 0;
            color: rgba(244, 255, 253, 0.78) !important;
            font-size: 0.75rem !important;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            font-weight: 700;
        }

        .brand-card h1 {
            margin: 0 !important;
            color: #f4fffd !important;
            font-size: 1.35rem !important;
            line-height: 1.2;
        }

        .brand-card p {
            margin: 8px 0 0 0;
            color: rgba(244, 255, 253, 0.88) !important;
            line-height: 1.4 !important;
            font-size: 0.95rem !important;
        }

        .user-chip {
            background: var(--surface);
            border: 1px solid var(--line);
            border-radius: 12px;
            padding: 10px 12px;
            margin-bottom: 8px;
            box-shadow: var(--shadow-soft);
        }

        .user-chip .name {
            margin: 0;
            color: var(--ink) !important;
            font-size: 1rem !important;
            font-weight: 700;
        }

        .user-chip .role {
            margin: 2px 0 0 0;
            color: var(--muted) !important;
            font-size: 0.84rem !important;
            font-weight: 600;
            text-transform: capitalize;
            letter-spacing: 0.02em;
        }

        .sidebar-section {
            margin: 14px 2px 7px 4px;
            color: var(--muted) !important;
            font-size: 0.8rem !important;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.08em;
        }

        .helper-card {
            background: var(--surface);
            border: 1px solid var(--line);
            border-radius: 12px;
            padding: 12px;
            margin-top: 14px;
            box-shadow: var(--shadow-soft);
        }

        .helper-card h4 {
            margin: 0 0 6px 0;
            color: var(--ink) !important;
            font-size: 1rem !important;
        }

        .helper-card p {
            margin: 0;
            color: var(--muted) !important;
            line-height: 1.45 !important;
            font-size: 0.95rem !important;
        }

        .helper-card.warn {
            background: #fff8e9;
            border-color: #f6d88b;
        }

        .helper-card.warn h4 {
            color: #7a4f00 !important;
        }

        .helper-card.warn p {
            color: #6a4b15 !important;
        }

        .stButton > button {
            background: linear-gradient(135deg, var(--brand) 0%, var(--brand-strong) 100%);
            color: #ffffff !important;
            border: none;
            border-radius: 12px;
            font-weight: 700;
            box-shadow: 0 8px 18px rgba(15, 118, 110, 0.28);
            transition: transform .18s ease, box-shadow .18s ease;
        }

        .stButton > button:hover {
            transform: translateY(-1px);
            box-shadow: 0 12px 22px rgba(15, 118, 110, 0.34);
        }

        .stTextInput > div > div > input,
        .stNumberInput > div > div > input,
        .stTextArea textarea {
            border-radius: 10px;
            border: 1px solid var(--line) !important;
            background: #ffffff;
        }

        [data-baseweb="select"] > div {
            border-radius: 10px !important;
            border: 1px solid var(--line) !important;
        }

        [data-testid="stExpander"] {
            border: 1px solid var(--line);
            border-radius: 14px;
            background: rgba(255, 255, 255, 0.84);
            box-shadow: var(--shadow-soft);
            overflow: hidden;
        }

        .stTabs [data-baseweb="tab-list"] {
            gap: 0.45rem;
            padding-bottom: 0.55rem;
        }

        .stTabs [data-baseweb="tab"] {
            border-radius: 999px;
            border: 1px solid transparent;
            background: rgba(15, 118, 110, 0.10);
            color: #2e4651 !important;
            height: auto;
            padding: 0.42rem 0.9rem;
        }

        .stTabs [aria-selected="true"] {
            background: #ffffff;
            border-color: var(--line);
            box-shadow: var(--shadow-soft);
            color: var(--ink) !important;
            font-weight: 700;
        }

        .page-hero {
            background: linear-gradient(115deg, #0f766e 0%, #0ea5a0 52%, #f59e0b 150%);
            color: #f8fffe;
            border-radius: 18px;
            padding: 18px 20px;
            margin-bottom: 18px;
            box-shadow: var(--shadow-card);
            animation: riseIn .45s ease both;
        }

        .page-hero .tag {
            display: inline-block;
            background: rgba(255, 255, 255, 0.18);
            border: 1px solid rgba(255, 255, 255, 0.35);
            border-radius: 999px;
            padding: 4px 10px;
            font-size: 0.75rem;
            font-weight: 700;
            letter-spacing: 0.07em;
            text-transform: uppercase;
            margin-bottom: 8px;
        }

        .page-hero h1 {
            margin: 0 !important;
            color: #f8fffe !important;
            font-size: clamp(1.5rem, 2.3vw, 2.2rem) !important;
            line-height: 1.14;
        }

        .page-hero p {
            margin: 8px 0 0 0;
            color: rgba(248, 255, 254, 0.90) !important;
            font-size: 1.04rem !important;
            line-height: 1.42 !important;
        }

        .prediction-card {
            background: var(--surface);
            border: 1px solid var(--line);
            border-left: 4px solid var(--brand);
            border-radius: 14px;
            box-shadow: var(--shadow-soft);
        }

        .home-panel {
            background: var(--surface);
            border: 1px solid var(--line);
            border-radius: 16px;
            padding: 18px;
            box-shadow: var(--shadow-soft);
            margin-bottom: 14px;
        }

        .home-panel-soft {
            background: linear-gradient(165deg, #eef8f4 0%, #ffffff 60%);
        }

        .home-panel h3 {
            margin: 0 0 10px 0;
            color: var(--ink) !important;
            font-size: 1.25rem !important;
        }

        .home-panel p {
            margin: 0 0 8px 0;
            color: var(--muted) !important;
            line-height: 1.48 !important;
            font-size: 1rem !important;
        }

        .home-list {
            margin: 10px 0 0 0;
            padding-left: 18px;
            color: var(--muted);
        }

        .home-list li {
            margin-bottom: 6px;
            line-height: 1.4;
        }

        .home-kpi {
            display: flex;
            justify-content: space-between;
            align-items: baseline;
            padding: 9px 0;
            border-bottom: 1px dashed var(--line);
        }

        .home-kpi:last-child {
            border-bottom: none;
        }

        .home-kpi .label {
            color: var(--muted);
            font-size: 0.9rem;
            font-weight: 600;
        }

        .home-kpi .value {
            color: var(--ink);
            font-family: 'Manrope', sans-serif;
            font-size: 1.3rem;
            font-weight: 800;
            letter-spacing: -0.02em;
        }

        .path-card {
            background: var(--surface);
            border: 1px solid var(--line);
            border-radius: 14px;
            padding: 14px;
            box-shadow: var(--shadow-soft);
            min-height: 185px;
        }

        .path-card .tag {
            display: inline-block;
            font-size: 0.75rem;
            font-weight: 700;
            letter-spacing: 0.06em;
            text-transform: uppercase;
            color: var(--brand-strong);
            background: #dff1eb;
            border-radius: 999px;
            padding: 3px 9px;
            margin-bottom: 8px;
        }

        .path-card h4 {
            margin: 0 0 6px 0;
            color: var(--ink) !important;
            font-size: 1.08rem !important;
        }

        .path-card p {
            margin: 0;
            color: var(--muted) !important;
            font-size: 0.95rem !important;
            line-height: 1.45 !important;
        }

        .workflow-row {
            display: grid;
            grid-template-columns: repeat(4, minmax(0, 1fr));
            gap: 10px;
            margin-top: 10px;
        }

        .workflow-step {
            background: #f6fbf9;
            border: 1px solid var(--line);
            border-radius: 12px;
            padding: 10px 11px;
        }

        .workflow-step .num {
            display: inline-block;
            font-family: 'Manrope', sans-serif;
            font-weight: 800;
            color: var(--brand-strong);
            margin-bottom: 5px;
        }

        .workflow-step p {
            margin: 0;
            font-size: 0.9rem !important;
            color: var(--muted) !important;
            line-height: 1.35 !important;
        }

        .disclaimer-note {
            background: #fff8e9;
            border: 1px solid #f4d99a;
            border-left: 5px solid #d08a00;
            border-radius: 12px;
            padding: 12px 14px;
            color: #6a4b15;
            font-size: 0.95rem !important;
            line-height: 1.45 !important;
            margin-top: 10px;
        }

        @media (max-width: 900px) {
            .workflow-row {
                grid-template-columns: repeat(2, minmax(0, 1fr));
            }
            .path-card {
                min-height: 0;
            }
        }

        @keyframes riseIn {
            from {
                opacity: 0;
                transform: translateY(10px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
</style>
    """, unsafe_allow_html=True)

def apply_bold_interface_overrides():
    """Layer a premium visual system on top of the legacy theme."""
    st.markdown("""
<style>
        @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&family=DM+Sans:wght@400;500;600;700&display=swap');

        :root {
            --ui-ink: #0b1523;
            --ui-muted: #4e5f72;
            --ui-line: rgba(120, 145, 175, 0.20);
            --ui-surface: rgba(255, 255, 255, 0.97);
            --ui-surface-dark: #080f1d;
            --ui-surface-dark-2: #0e1c31;
            --ui-brand: #00d4c8;
            --ui-brand-2: #3b6cff;
            --ui-brand-3: #7c3aed;
            --ui-accent: #f59e0b;
            --ui-positive: #22c55e;
            --ui-negative: #ef4444;
            --ui-shadow: 0 20px 52px rgba(5, 12, 27, 0.14);
            --ui-shadow-glow: 0 0 0 4px rgba(0, 212, 200, 0.15);
        }

        html, body, .stApp, [data-testid="stAppViewContainer"] {
            font-family: 'DM Sans', 'Segoe UI', sans-serif !important;
        }
        h1, h2, h3, h4, h5, h6 { font-family: 'Space Grotesk', sans-serif !important; letter-spacing: -0.03em; }

        @keyframes gradShift {
            0%   { background-position: 0% 50%; }
            50%  { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }

        @keyframes pulseRing {
            0%   { box-shadow: 0 0 0 0 rgba(0, 212, 200, 0.50); }
            70%  { box-shadow: 0 0 0 10px rgba(0, 212, 200, 0.00); }
            100% { box-shadow: 0 0 0 0 rgba(0, 212, 200, 0.00); }
        }

        @keyframes shimmerSlide {
            0%   { background-position: -400px 0; }
            100% { background-position: 400px 0; }
        }

        @keyframes riseIn {
            from { opacity: 0; transform: translateY(14px); }
            to   { opacity: 1; transform: translateY(0); }
        }

        @keyframes scaleIn {
            from { opacity: 0; transform: scale(0.94); }
            to   { opacity: 1; transform: scale(1); }
        }

        .stApp {
            background:
                radial-gradient(ellipse at 5% 8%, rgba(0, 212, 200, 0.13), transparent 26%),
                radial-gradient(ellipse at 92% 6%, rgba(59, 108, 255, 0.16), transparent 26%),
                radial-gradient(ellipse at 50% 95%, rgba(124, 58, 237, 0.08), transparent 30%),
                linear-gradient(180deg, #07101e 0%, #0d1b30 18%, #edf2f8 18.2%, #f4f8ff 100%) !important;
        }

        [data-testid="stSidebar"] {
            background:
                radial-gradient(circle at 20% 15%, rgba(0, 212, 200, 0.12), transparent 40%),
                radial-gradient(circle at 80% 80%, rgba(59, 108, 255, 0.10), transparent 40%),
                linear-gradient(175deg, #060e1c 0%, #0a1626 55%, #0c1d35 100%) !important;
            border-right: 1px solid rgba(255,255,255,0.05) !important;
        }

        .brand-card {
            background: linear-gradient(145deg, #091a2f 0%, #0f2848 50%, #1a3a6e 100%) !important;
            border: 1px solid rgba(0, 212, 200, 0.20) !important;
            border-radius: 22px !important;
            box-shadow: 0 20px 50px rgba(0,0,0,0.30), 0 0 30px rgba(0, 212, 200, 0.06) !important;
            position: relative;
            overflow: hidden;
        }

        .brand-card::after {
            content: "";
            position: absolute;
            inset: 0;
            border-radius: 22px;
            background: linear-gradient(135deg, rgba(0,212,200,0.10) 0%, transparent 60%);
            pointer-events: none;
        }

        .beacon {
            display: inline-flex;
            align-items: center;
            gap: 0.4rem;
        }

        .beacon-dot {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: #00d4c8;
            animation: pulseRing 2s ease-out infinite;
        }

        .brand-card .eyebrow, .sidebar-section { color: rgba(200, 230, 255, 0.65) !important; letter-spacing: 0.09em; }
        .brand-card h1 { color: #f0faff !important; text-shadow: 0 1px 12px rgba(0,212,200,0.25); }
        .brand-card p { color: rgba(224, 240, 255, 0.80) !important; }
        .user-chip .name { color: #e8f4ff !important; }
        .helper-card h4 { color: #dbeeff !important; }

        .user-chip {
            background: rgba(255,255,255,0.07) !important;
            border: 1px solid rgba(255,255,255,0.10) !important;
            border-radius: 18px !important;
            backdrop-filter: blur(12px);
            display: flex;
            align-items: center;
            gap: 0.65rem;
        }

        .avatar-circle {
            flex-shrink: 0;
            width: 38px;
            height: 38px;
            border-radius: 50%;
            background: linear-gradient(135deg, var(--ui-brand) 0%, var(--ui-brand-2) 100%);
            color: #ffffff;
            font-family: 'Space Grotesk', sans-serif;
            font-weight: 700;
            font-size: 1rem;
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: 0 4px 14px rgba(0,212,200,0.35);
        }

        .avatar-info .name { color: #e8f4ff !important; font-weight: 700; font-size: 0.96rem; margin: 0; }
        .avatar-info .role {
            color: rgba(200,230,255,0.65) !important;
            font-size: 0.76rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.07em;
            margin: 1px 0 0;
        }

        .helper-card {
            background: rgba(255,255,255,0.05) !important;
            border: 1px solid rgba(255,255,255,0.08) !important;
            border-radius: 16px !important;
            backdrop-filter: blur(12px);
        }

        .helper-card.warn {
            background: rgba(245, 158, 11, 0.08) !important;
            border-color: rgba(245, 158, 11, 0.22) !important;
        }

        .helper-card.warn h4 { color: #fde68a !important; }
        .helper-card.warn p  { color: rgba(253,230,138,0.85) !important; }

        .stButton > button, .stDownloadButton > button {
            border: none !important;
            border-radius: 14px !important;
            background: linear-gradient(135deg, #00c4b8 0%, var(--ui-brand-2) 100%) !important;
            color: #ffffff !important;
            font-weight: 700 !important;
            font-family: 'Space Grotesk', sans-serif !important;
            letter-spacing: 0.01em;
            box-shadow: 0 10px 28px rgba(59, 108, 255, 0.24) !important;
            transition: transform 0.18s ease, box-shadow 0.18s ease !important;
        }

        .stButton > button:hover, .stDownloadButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 16px 36px rgba(59, 108, 255, 0.32) !important;
        }

        .stTextInput > div > div > input,
        .stNumberInput > div > div > input,
        .stTextArea textarea,
        [data-baseweb="select"] > div {
            border-radius: 12px !important;
            border: 1.5px solid rgba(140, 165, 200, 0.28) !important;
            background: rgba(255, 255, 255, 0.98) !important;
            transition: border-color 0.18s ease, box-shadow 0.18s ease !important;
        }

        .stTextInput > div > div > input:focus,
        .stNumberInput > div > div > input:focus,
        .stTextArea textarea:focus {
            border-color: var(--ui-brand) !important;
            box-shadow: 0 0 0 4px rgba(0, 212, 200, 0.14) !important;
            background: #ffffff !important;
            outline: none;
        }

        [data-testid="stExpander"] {
            border-radius: 16px !important;
            border: 1.5px solid var(--ui-line) !important;
            background: rgba(255, 255, 255, 0.96) !important;
            box-shadow: var(--ui-shadow) !important;
        }

        .stTabs [data-baseweb="tab-list"] {
            gap: 0.4rem;
            border-bottom: 2px solid rgba(140,165,200,0.22) !important;
            padding-bottom: 0.1rem;
        }

        .stTabs [data-baseweb="tab"] {
            border-radius: 8px 8px 0 0 !important;
            background: transparent !important;
            border: none !important;
            font-weight: 600 !important;
            color: var(--ui-muted) !important;
            padding-bottom: 0.6rem !important;
            position: relative;
        }

        .stTabs [aria-selected="true"] {
            background: transparent !important;
            color: var(--ui-brand) !important;
            font-weight: 700 !important;
            border: none !important;
            box-shadow: none !important;
        }

        .stTabs [aria-selected="true"]::after {
            content: "";
            position: absolute;
            bottom: -2px;
            left: 0;
            right: 0;
            height: 3px;
            border-radius: 3px 3px 0 0;
            background: linear-gradient(90deg, var(--ui-brand), var(--ui-brand-2));
        }

        .page-hero {
            background:
                radial-gradient(ellipse at top right, rgba(0, 212, 200, 0.18), transparent 30%),
                radial-gradient(ellipse at bottom left, rgba(59, 108, 255, 0.12), transparent 40%),
                linear-gradient(135deg, #060d1c 0%, #0a1932 55%, #122244 100%) !important;
            border: 1px solid rgba(0, 212, 200, 0.15) !important;
            border-radius: 22px !important;
            box-shadow: 0 28px 72px rgba(4, 10, 25, 0.22), 0 0 0 1px rgba(0,212,200,0.08) !important;
            animation: riseIn 0.5s ease both;
        }

        .page-hero .tag {
            background: rgba(0, 212, 200, 0.15) !important;
            border: 1px solid rgba(0, 212, 200, 0.28) !important;
            color: #a0f5ee !important;
            font-weight: 700;
            letter-spacing: 0.08em;
        }

        .prediction-card, .home-panel, .path-card, .section-card, .doc-card, .feature-card, .history-entry, .footer-shell, .feedback-note {
            background: var(--ui-surface) !important;
            border: 1px solid var(--ui-line) !important;
            border-radius: 20px !important;
            box-shadow: var(--ui-shadow) !important;
        }

        .home-panel-soft {
            background: linear-gradient(145deg, rgba(0, 212, 200, 0.08) 0%, rgba(255, 255, 255, 0.98) 70%) !important;
        }

        /* Path cards: emoji hover lift + coloured top border */
        .path-card {
            border-top: 3px solid transparent !important;
            transition: transform 0.22s ease, box-shadow 0.22s ease, border-color 0.22s ease;
            animation: riseIn 0.5s ease both;
        }

        .path-card:nth-child(1) { border-top-color: var(--ui-brand) !important; animation-delay: 0.05s; }
        .path-card:nth-child(2) { border-top-color: var(--ui-brand-2) !important; animation-delay: 0.12s; }
        .path-card:nth-child(3) { border-top-color: var(--ui-brand-3) !important; animation-delay: 0.20s; }

        .path-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 28px 60px rgba(5, 14, 32, 0.16) !important;
        }

        .path-card .tag, .mini-tag {
            background: rgba(0, 212, 200, 0.10) !important;
            border: 1px solid rgba(0, 212, 200, 0.20) !important;
            color: #007f7a !important;
            border-radius: 999px;
            padding: 0.32rem 0.70rem;
            display: inline-block;
            font-size: 0.73rem;
            font-weight: 700;
            letter-spacing: 0.07em;
            text-transform: uppercase;
        }

        .feature-card {
            animation: riseIn 0.5s ease both;
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }

        .feature-card:hover {
            transform: translateY(-3px);
            box-shadow: 0 24px 52px rgba(5, 14, 32, 0.14) !important;
        }

        /* Staggered card reveal */
        .feature-card:nth-child(1), .doc-card:nth-child(1) { animation-delay: 0.05s; }
        .feature-card:nth-child(2), .doc-card:nth-child(2) { animation-delay: 0.12s; }
        .feature-card:nth-child(3), .doc-card:nth-child(3) { animation-delay: 0.20s; }

        .workflow-step {
            background: rgba(240, 246, 255, 0.90) !important;
            border: 1px solid var(--ui-line) !important;
            border-radius: 14px !important;
        }

        .workflow-step .num {
            background: linear-gradient(135deg, var(--ui-brand), var(--ui-brand-2));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            font-family: 'Space Grotesk', sans-serif !important;
            font-weight: 700;
        }

        .home-kpi .value {
            color: var(--ui-brand-2) !important;
            font-family: 'Space Grotesk', sans-serif !important;
        }

        .disclaimer-note, .feedback-note {
            background: rgba(245, 158, 11, 0.10) !important;
            border-left: 4px solid var(--ui-accent) !important;
            color: #7c4c00 !important;
        }

        [data-testid="stMetric"] {
            background: linear-gradient(145deg, rgba(255,255,255,0.98) 0%, rgba(240,248,255,0.95) 100%) !important;
            border: 1.5px solid var(--ui-line) !important;
            border-top: 3px solid var(--ui-brand) !important;
            border-radius: 18px !important;
            box-shadow: var(--ui-shadow) !important;
            transition: transform 0.2s ease;
        }

        [data-testid="stMetric"]:hover {
            transform: translateY(-2px);
            box-shadow: 0 26px 60px rgba(5, 14, 32, 0.16) !important;
        }

        [data-testid="stDataFrame"] {
            border-radius: 14px !important;
            overflow: hidden;
            border: 1.5px solid var(--ui-line) !important;
            box-shadow: var(--ui-shadow) !important;
        }

        .history-entry {
            padding: 18px 20px;
            margin-bottom: 14px;
            border-left: 4px solid rgba(0, 212, 200, 0.40) !important;
            animation: riseIn 0.42s ease both;
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }
        .history-entry:hover { transform: translateX(3px); box-shadow: 0 22px 50px rgba(5, 14, 32, 0.15) !important; }
        .history-entry.positive { border-left-color: rgba(239, 68, 68, 0.65) !important; }
        .history-entry.negative { border-left-color: rgba(34, 197, 94, 0.65) !important; }
        .history-head { display: flex; justify-content: space-between; gap: 1rem; align-items: flex-start; margin-bottom: 0.75rem; }
        .history-stamp { color: var(--ui-muted) !important; font-size: 0.88rem !important; background: rgba(240,246,255,0.85); padding: 0.25rem 0.6rem; border-radius: 999px; border: 1px solid var(--ui-line); }
        .history-summary { color: var(--ui-muted) !important; font-size: 0.97rem !important; line-height: 1.55 !important; }
        .history-meta { display: flex; flex-wrap: wrap; gap: 0.55rem; margin-top: 0.9rem; }
        .history-pill { display: inline-flex; align-items: center; gap: 0.3rem; padding: 0.35rem 0.75rem; border-radius: 999px; background: rgba(240, 248, 255, 0.95); border: 1px solid rgba(15, 23, 42, 0.08); color: var(--ui-ink) !important; font-size: 0.82rem; font-weight: 700; }
        .history-pill.alert { background: rgba(254, 226, 226, 0.92); color: #991b1b !important; border-color: rgba(239,68,68,0.18); }
        .history-pill.alert::before { content: "⚠"; }
        .history-pill.safe  { background: rgba(220, 252, 231, 0.92); color: #166534 !important; border-color: rgba(34,197,94,0.18); }
        .history-pill.safe::before  { content: "✓"; }

        .doc-grid, .feature-grid, .stat-grid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 14px; }
        .feature-card { padding: 20px; }
        .feature-card h4 { margin: 0.45rem 0 0.4rem 0; color: var(--ui-ink) !important; }
        .feature-card p { margin: 0; color: var(--ui-muted) !important; line-height: 1.6 !important; }
        .section-card, .doc-card { padding: 22px; margin-bottom: 14px; }
        .section-card.dark { background: linear-gradient(135deg, #060d1c 0%, #0d1b30 100%) !important; border-color: rgba(0, 212, 200, 0.12) !important; }
        .section-card.dark h3, .section-card.dark p, .section-card.dark li,
        .section-card.dark ol, .section-card.dark ul { color: #dae9ff !important; }
        .doc-card pre, .code-card { background: #07111f; color: #c9e8ff !important; border-radius: 14px; padding: 14px 18px; border: 1px solid rgba(0,212,200,0.12); }
        .doc-card code, .code-card code { color: #7ff5ef !important; font-family: 'DM Mono', 'Fira Code', monospace; }

        /* ── Streamlit Sidebar & Menu ────────────────────────────────────── */
        [data-testid="stSidebar"] > div:first-child {
            background: linear-gradient(180deg, #050b14 0%, #0a1932 100%) !important;
            border-right: 1px solid rgba(0, 212, 200, 0.12) !important;
        }

        /* Force high-contrast readable text for ALL states */
        [data-testid="stSidebar"] .nav-link {
            color: rgba(210, 235, 255, 0.82) !important;
            border-radius: 12px !important;
            margin: 0 !important;
            padding: 0.55rem 0.9rem !important;
            font-size: 0.93rem !important;
            font-weight: 500 !important;
            transition: background 0.18s ease, color 0.18s ease !important;
        }

        [data-testid="stSidebar"] .nav-link:hover {
            background: rgba(255, 255, 255, 0.09) !important;
            color: #ffffff !important;
        }

        [data-testid="stSidebar"] .nav-link.active,
        [data-testid="stSidebar"] .nav-link[aria-selected="true"] {
            background: linear-gradient(135deg, #00c4b8 0%, #3b6cff 100%) !important;
            color: #ffffff !important;
            font-weight: 700 !important;
            box-shadow: 0 8px 20px rgba(59, 108, 255, 0.28) !important;
        }

        [data-testid="stSidebar"] .nav-link-icon {
            color: inherit !important;
        }

        [data-testid="stSidebar"] .nav-link .nav-link-icon {
            opacity: 1 !important;
        }

        /* ── section label above navigation ──────────────────────────────── */
        [data-testid="stSidebar"] small,
        [data-testid="stSidebar"] .sidebar-section {
            color: rgba(160, 210, 255, 0.55) !important;
            font-size: 0.71rem !important;
            letter-spacing: 0.10em !important;
            text-transform: uppercase;
            font-weight: 700;
        }

        /* ── Logout / secondary buttons in sidebar ────────────────────────── */
        [data-testid="stSidebar"] .stButton > button {
            background: rgba(255,255,255,0.08) !important;
            color: rgba(210,235,255,0.90) !important;
            border: 1px solid rgba(255,255,255,0.12) !important;
            box-shadow: none !important;
        }

        [data-testid="stSidebar"] .stButton > button:hover {
            background: rgba(255,255,255,0.14) !important;
            color: #ffffff !important;
        }

        /* ── Form section group headers ───────────────────────────────────── */
        .input-group-header {
            display: flex;
            align-items: center;
            gap: 0.55rem;
            margin: 1.4rem 0 0.6rem;
            padding-bottom: 0.45rem;
            border-bottom: 1.5px solid rgba(120,145,175,0.22);
        }

        .input-group-header .group-icon {
            color: #00c4b8;
            font-size: 1rem;
            line-height: 1;
        }

        .input-group-header span:not(.group-icon) {
            font-family: 'Space Grotesk', sans-serif;
            font-weight: 700;
            font-size: 0.78rem;
            letter-spacing: 0.09em;
            text-transform: uppercase;
            color: #4e5f72;
        }

        .footer-shell {
            background: linear-gradient(145deg, rgba(240, 248, 255, 0.95) 0%, rgba(255, 255, 255, 0.98) 100%) !important;
            border: 1px solid var(--ui-line) !important;
            color: var(--ui-ink) !important;
            padding: 24px 26px;
            border-radius: 22px !important;
            box-shadow: var(--ui-shadow) !important;
        }

        .footer-shell h3 { color: var(--ui-ink) !important; font-size: 1.15rem; margin-bottom: 0.4rem; }
        .footer-shell p { color: var(--ui-muted) !important; margin: 0; }
        .footer-links { display: flex; flex-wrap: wrap; gap: 1rem; margin-top: 1.25rem; }
        .footer-links span {
            padding: 0.28rem 0.72rem;
            border-radius: 999px;
            background: rgba(0, 212, 200, 0.08);
            border: 1px solid rgba(0, 212, 200, 0.15);
            font-size: 0.84rem;
            color: var(--ui-brand-2);
            font-weight: 500;
        }

        @media (max-width: 900px) {
            .doc-grid, .feature-grid, .stat-grid, .workflow-row { grid-template-columns: 1fr !important; }
            .history-head { flex-direction: column; }
        }
</style>
    """, unsafe_allow_html=True)

def render_page_hero(title, subtitle, tag_text=""):
    """Render a consistent page hero banner."""
    badge_html = f"<span class='tag'>{tag_text}</span>" if tag_text else ""
    st.markdown(
        f"""
<section class="page-hero">
    {badge_html}
<h1>{title}</h1>
<p>{subtitle}</p>
</section>
        """,
        unsafe_allow_html=True
    )

def render_feature_grid(items):
    """Render a responsive feature-card grid."""
    cards_html: list[str] = []
    for item in items:
        tag = item.get("tag", "")
        tag_html = f"<span class='tag'>{tag}</span>" if tag else ""
        cards_html.append(
            str(f"""
<article class="feature-card">
    {tag_html}
<h4>{item['title']}</h4>
<p>{item['body']}</p>
</article>
            """)
        )
    st.markdown(f"<section class='feature-grid'>{''.join(cards_html)}</section>", unsafe_allow_html=True)

def render_doc_grid(items):
    """Render documentation-style content cards."""
    cards_html: list[str] = []
    for item in items:
        title = item["title"]
        body = item["body"]
        cards_html.append(
            str(f"""
<article class="doc-card">
<h3>{title}</h3>
<p>{body}</p>
</article>
            """)
        )
    st.markdown(f"<section class='doc-grid'>{''.join(cards_html)}</section>", unsafe_allow_html=True)

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

# Keep background consistent with the theme to preserve readability.

# Function to display a styled header
def styled_header(text, level=1):
    if level == 1:
        st.markdown(f"<h1 style='text-align: center; color: var(--ui-ink); padding-bottom: 14px; font-size: 2.2rem; letter-spacing:-0.03em;'>{text}</h1>", unsafe_allow_html=True)
    elif level == 2:
        st.markdown(f"<h2 style='color: var(--ui-ink); padding-bottom: 6px; font-size: 1.7rem; letter-spacing:-0.02em;'>{text}</h2>", unsafe_allow_html=True)
    elif level == 3:
        st.markdown(f"<h3 style='color: var(--ui-ink); padding-bottom: 4px; font-size: 1.25rem;'>{text}</h3>", unsafe_allow_html=True)

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
def styled_card(title, content, icon=""):
    icon_markup = f"<span style='margin-right:6px;'>{icon}</span>" if icon else ""
    st.markdown(f"""
<div class="prediction-card" style="padding: 16px;">
<h3 style="color: var(--ui-ink); font-size: 1.3rem; margin-bottom: 8px;">{icon_markup}{title}</h3>
<p style="color: var(--ui-muted); font-size: 1rem; line-height: 1.5; margin: 0;">{content}</p>
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

apply_interface_theme()
apply_bold_interface_overrides()

# Add a sidebar for navigation
with st.sidebar:
    st.markdown("""
<div class="brand-card">
<div class="beacon" style="margin-bottom:8px;">
<div class="beacon-dot"></div>
<span class="eyebrow" style="margin:0;">AI Screening Console</span>
</div>
<h1 style="margin-bottom:6px;">Health AI Studio</h1>
<p style="margin:0;">Guided disease screening, saved sessions &amp; confidence-led interpretation.</p>
</div>
    """, unsafe_allow_html=True)

    user = st.session_state.get('user')
    if user:
        initials = (user['username'][:2]).upper()
        st.markdown(f"""
<div class="user-chip" style="padding:10px 12px;">
<div class="avatar-circle">{initials}</div>
<div class="avatar-info">
<p class="name">{user['username']}</p>
<p class="role">{user['role']}</p>
</div>
</div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
<div class="user-chip" style="padding:10px 12px;">
<div class="avatar-circle">U</div>
<div class="avatar-info">
<p class="name">Signed In</p>
<p class="role">Session Active</p>
</div>
</div>
        """, unsafe_allow_html=True)

    if st.button("Logout", key="logout_button", help="Sign out of your account", use_container_width=True):
        logout()

    st.markdown("<p class='sidebar-section'>Navigation</p>", unsafe_allow_html=True)

    selected = option_menu(
        menu_title=None,
        options=["Welcome", "Diabetes Prediction", "Heart Disease Prediction", "Parkinson's Prediction", "History", "Requirements", "About"],
        icons=["house", "activity", "heart", "person", "clock-history", "info-circle", "file-earmark-text"],
        menu_icon="cast",
        default_index=0,
        styles={
            "container": {"padding": "10px", "background-color": "#0b1727", "border-radius": "16px", "border": "1px solid rgba(0,212,200,0.15)"},
            "icon": {"color": "#00d4c8", "font-size": "19px"},
            "nav-link": {
                "font-size": "0.95rem",
                "text-align": "left",
                "margin": "4px 0",
                "padding": "10px 12px",
                "--hover-color": "rgba(0,212,200,0.1) !important",
                "transition": "all 0.3s",
                "border-radius": "12px",
                "color": "#ffffff !important",
                "font-weight": "600"
            },
            "nav-link-selected": {
                "background": "linear-gradient(135deg, #00d4c8 0%, #3b6cff 100%)",
                "color": "white",
                "font-weight": "700",
                "box-shadow": "0 8px 16px rgba(59,108,255,0.2)"
            },
        }
    )

    st.markdown("""
<div class="helper-card" style="padding:12px 14px;">
<h4 style="margin:0 0 5px;">📋 How it works</h4>
<p style="margin:0;">Select a module, enter clinical inputs, then review the prediction confidence and supporting charts.</p>
</div>
    """, unsafe_allow_html=True)

    st.markdown("""
<div class="helper-card warn" style="padding:12px 14px;">
<h4 style="margin:0 0 5px;">⚕️ Clinical note</h4>
<p style="margin:0;">For educational screening only. Always confirm decisions with a licensed healthcare professional.</p>
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
<h2 style="color: #1e3a8a; margin-bottom: 20px;">Welcome to Health AI</h2>
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
<h4 style="color: #1e3a8a; margin: 0 0 10px 0;">{tip_title}</h4>
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
        if st.button("Help", key="help_button"):
            st.session_state.help_popup_shown = not st.session_state.help_popup_shown
            st.rerun()
        
        # Show help content if button was clicked
        if st.session_state.help_popup_shown:
            st.markdown("""
<div class="helper-card" style="margin-top: 0.75rem;">
<h4>Need help?</h4>
<ul style="margin: 0; padding-left: 20px;">
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
    show_help_button()

    render_page_hero(
        "Welcome to Health AI Studio",
        "A unified workspace for disease-risk screening, confidence tracking, and medical insight exploration.",
        "Overview"
    )

    predictions_df = get_user_predictions(st.session_state['user']['id'])
    if predictions_df.empty:
        total_predictions = 0
        diseases_covered = 0
        average_confidence = 0.0
        latest_activity = "No predictions yet"
    else:
        total_predictions = int(len(predictions_df))
        diseases_covered = int(predictions_df["prediction_type"].nunique())
        average_confidence = float(predictions_df["confidence"].fillna(0).mean())
        latest_timestamp = pd.to_datetime(predictions_df["created_at"], errors="coerce").max()
        latest_activity = latest_timestamp.strftime("%d %b %Y") if pd.notna(latest_timestamp) else "Unavailable"

    lead_col, stats_col = st.columns([2.15, 1], gap="large")
    with lead_col:
        st.markdown("""
<section class="home-panel">
<h3>What You Can Do Here</h3>
<p>
                Run guided predictions for diabetes, heart disease, and Parkinson's disease.
                Every result includes confidence scoring and visual interpretation to support early awareness.
</p>
<ul class="home-list">
<li>Use validated input ranges for each clinical parameter.</li>
<li>Review confidence and analytics before interpreting results.</li>
<li>Track all runs in History and compare trends over time.</li>
</ul>
</section>
        """, unsafe_allow_html=True)

    with stats_col:
        st.markdown(f"""
<section class="home-panel home-panel-soft">
<h3>Workspace Snapshot</h3>
<div class="home-kpi">
<span class="label">Total Predictions</span>
<span class="value">{total_predictions}</span>
</div>
<div class="home-kpi">
<span class="label">Modules Used</span>
<span class="value">{diseases_covered}</span>
</div>
<div class="home-kpi">
<span class="label">Average Confidence</span>
<span class="value">{average_confidence:.1f}%</span>
</div>
<div class="home-kpi">
<span class="label">Latest Activity</span>
<span class="value" style="font-size:1rem;">{latest_activity}</span>
</div>
</section>
        """, unsafe_allow_html=True)

    styled_header("Choose Your Screening Path", level=2)
    mod_col1, mod_col2, mod_col3 = st.columns(3, gap="large")

    with mod_col1:
        st.markdown("""
<article class="path-card">
<span class="tag">Module 01</span>
<h4>🩸 Diabetes Risk</h4>
<p>Eight metabolic indicators including glucose, BMI, insulin, and family-risk score.</p>
</article>
        """, unsafe_allow_html=True)

    with mod_col2:
        st.markdown("""
<article class="path-card">
<span class="tag">Module 02</span>
<h4>❤️ Heart Disease Risk</h4>
<p>Thirteen cardiovascular markers including ECG profile, cholesterol, and exertion response.</p>
</article>
        """, unsafe_allow_html=True)

    with mod_col3:
        st.markdown("""
<article class="path-card">
<span class="tag">Module 03</span>
<h4>🧠 Parkinson's Risk</h4>
<p>Twenty-two voice biomarkers analyzing shimmer, jitter, entropy, and nonlinear signal traits.</p>
</article>
        """, unsafe_allow_html=True)

    st.markdown("""
<section class="home-panel">
<h3>Quick Start Workflow</h3>
<div class="workflow-row">
<div class="workflow-step">
<span class="num">1. Select Module</span>
<p>Open a prediction module from the sidebar.</p>
</div>
<div class="workflow-step">
<span class="num">2. Enter Inputs</span>
<p>Fill all required values using guided fields.</p>
</div>
<div class="workflow-step">
<span class="num">3. Run Prediction</span>
<p>Generate model output with confidence.</p>
</div>
<div class="workflow-step">
<span class="num">4. Review History</span>
<p>Track outcomes and export as CSV when needed.</p>
</div>
</div>
</section>
    """, unsafe_allow_html=True)

    styled_header("Recent Activity", level=2)
    if predictions_df.empty:
        st.info("No predictions yet. Start with any module from the sidebar.")
    else:
        recent_df = predictions_df.copy()
        recent_df["created_at"] = pd.to_datetime(recent_df["created_at"], errors="coerce")
        recent_df["confidence"] = pd.to_numeric(recent_df["confidence"], errors="coerce")
        recent_df = recent_df.sort_values("created_at", ascending=False)
        recent_df["created_at"] = recent_df["created_at"].dt.strftime("%Y-%m-%d %H:%M")
        recent_df["confidence"] = recent_df["confidence"].apply(
            lambda value: f"{value:.1f}%" if pd.notna(value) else "N/A"
        )
        recent_df = recent_df.rename(
            columns={
                "created_at": "Date",
                "prediction_type": "Disease",
                "result": "Prediction Result",
                "confidence": "Confidence"
            }
        )
        st.dataframe(
            recent_df[["Date", "Disease", "Prediction Result", "Confidence"]].head(6),
            use_container_width=True,
            hide_index=True
        )

    st.markdown("""
<div class="disclaimer-note">
<strong>Medical disclaimer:</strong> Predictions are informational and should not replace professional diagnosis or treatment decisions.
</div>
    """, unsafe_allow_html=True)

# Enhanced Diabetes Prediction Page
if (selected == 'Diabetes Prediction'):
    # Show help button
    show_help_button()
    
    render_page_hero(
        "Diabetes Prediction",
        "Enter metabolic indicators to evaluate diabetes likelihood and confidence score.",
        "Prediction Module"
    )
    
    # Add tooltips for input fields
    add_tooltip("glucose", "Fasting blood sugar level in mg/dL")
    add_tooltip("bmi", "Body Mass Index - weight (kg) / height (m)^2")
    add_tooltip("age", "Age in years")
    add_tooltip("insulin", "2-Hour serum insulin (mu U/ml)")
    add_tooltip("skin", "Triceps skin fold thickness (mm)")
    add_tooltip("bp", "Diastolic blood pressure (mm Hg)")
    add_tooltip("dpf", "Diabetes Pedigree Function")
    add_tooltip("pregnancies", "Number of pregnancies")
    
    # Getting the input data from the user
    st.markdown('<div class="input-group-header"><span class="group-icon">📊</span><span>Reproductive &amp; Metabolic</span></div>', unsafe_allow_html=True)
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

    st.markdown('<div class="input-group-header"><span class="group-icon">🧪</span><span>Lab Values</span></div>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
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

    st.markdown('<div class="input-group-header"><span class="group-icon">👤</span><span>Demographics &amp; Family History</span></div>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
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
<section class="section-card">
<span class="mini-tag">Ranges</span>
<h4>Parameter normal ranges</h4>
<ul>
<li><strong>Glucose Level</strong>: 70-140 mg/dL (fasting)</li>
<li><strong>Blood Pressure</strong>: 60-90 mm Hg (diastolic)</li>
<li><strong>Skin Thickness</strong>: 10-50 mm (triceps fold)</li>
<li><strong>Insulin</strong>: 16-166 mu U/ml (2-hour serum)</li>
<li><strong>BMI</strong>: 18.5-24.9 (normal weight)</li>
<li><strong>Diabetes Pedigree Function</strong>: Scores likelihood of diabetes based on family history</li>
</ul>
<p><em>Note: Values outside normal ranges may indicate higher risk for diabetes.</em></p>
</section>
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
<section class="section-card" style="margin-top: 20px;">
<span class="mini-tag">Interpretation</span>
<h4>Understanding your metrics</h4>
                        
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
</section>
                    """, unsafe_allow_html=True)
                
                if diab_diagnosis:
                    save_prediction(
                        st.session_state['user']['id'],
                        "Diabetes",
                        input_data.tolist()[0],
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
    
    render_page_hero(
        "Heart Disease Prediction",
        "Assess cardiovascular risk using vitals, lipid profile, and symptom-linked parameters.",
        "Prediction Module"
    )
    
    # Add information about heart parameters
    with st.expander("Understanding Heart Health Parameters"):
        st.markdown("""
        ### Normal Ranges for Heart Health Parameters:
        - **Age**: Adult patients (29-77 years)
        - **Blood Pressure**: 90/60-120/80 mmHg (Normal)
        - **Cholesterol**: < 200 mg/dL (Desirable)
        - **Heart Rate**: 60-100 beats per minute (Rest)
        - **Blood Sugar**: < 140 mg/dL (Fasting)
        """)

    st.markdown('<div class="input-group-header"><span class="group-icon">👤</span><span>Demographics</span></div>', unsafe_allow_html=True)
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

    st.markdown('<div class="input-group-header"><span class="group-icon">❤️</span><span>Cardiovascular Vitals</span></div>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
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
                              - High: >= 240 mg/dL
                              """)
    with col3:
        fbs = st.selectbox('Fasting Blood Sugar > 120 mg/dl',
                          options=['No', 'Yes'],
                          help="Fasting blood sugar > 120 mg/dl")
        fbs = 1 if fbs == 'Yes' else 0

    st.markdown('<div class="input-group-header"><span class="group-icon">🧪</span><span>Lab Results</span></div>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
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

    st.markdown('<div class="input-group-header"><span class="group-icon">📈</span><span>Exercise &amp; Stress Test</span></div>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
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
    col1, col2, col3 = st.columns(3)
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
                heart_input_data = [age, sex, cp, trestbps, chol, fbs, restecg,
                                    thalach, exang, oldpeak, slope, ca, thal]
                heart_prediction = heart_disease_model.predict([heart_input_data])
                prediction_proba = get_prediction_probability(heart_disease_model, [heart_input_data])
                
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
                    st.error("High risk of heart disease detected")
                    risk_level = "High Risk"
                else:
                    st.success("Low risk of heart disease")
                    risk_level = "Low Risk"
                
                # Create three columns for metrics
                col1, col2, col3 = st.columns([1,2,1])
                
                with col2:
                    st.markdown(f"""
<section class="section-card">
<span class="mini-tag">Result</span>
<h3 style="text-align: center;">Heart health analysis</h3>
<p style="text-align: center; font-size: 1.2rem;">Risk level: {risk_level}</p>
<p style="text-align: center;">Confidence: {calculate_confidence(prediction_proba):.1f}%</p>
</section>
                    """, unsafe_allow_html=True)
                
                # Create tabs for different visualizations
                analysis_tab, metrics_tab = st.tabs(["Analysis", "Health Metrics"])
                
                with analysis_tab:
                    # Show risk factors
                    if risk_messages:
                        st.warning("Risk Factors Identified:")
                        for msg in risk_messages:
                            st.write(f"- {msg}")
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
                        heart_input_data,
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
    
    render_page_hero(
        "Parkinson's Disease Prediction",
        "Analyze voice biomarkers and nonlinear features for early Parkinson's risk screening.",
        "Prediction Module"
    )
    
    # Add information about voice parameters
    with st.expander("Understanding Voice Parameters"):
        st.markdown("""
        ### Voice Parameter Ranges:
        - **Jitter (%)**: 0.0-1.0% (Normal < 1.0%)
        - **Shimmer (%)**: 0.0-3.0% (Normal < 3.0%)
        - **HNR**: 15-25 dB (Higher values indicate better voice quality)
        - **RPDE**: 0.0-1.0 (Lower values indicate more regular voice)
        - **DFA**: 0.5-0.8 (Measure of signal complexity)
        - **PPE**: 0.0-0.5 (Lower values indicate more regular voice)
        """)
    
    st.markdown('<div class="input-group-header"><span class="group-icon">🎙️</span><span>Fundamental Frequency</span></div>', unsafe_allow_html=True)
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
        
    st.markdown('<div class="input-group-header"><span class="group-icon">〰️</span><span>Jitter (Frequency Variation)</span></div>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
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
        
    st.markdown('<div class="input-group-header"><span class="group-icon">📶</span><span>Shimmer (Amplitude Variation)</span></div>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
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
        
    st.markdown('<div class="input-group-header"><span class="group-icon">🔊</span><span>Noise Ratios & Nonlinear Measures</span></div>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
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
                    st.error("Indicators of Parkinson's disease detected")
                    risk_level = "High Risk"
                else:
                    st.success("No significant indicators detected")
                    risk_level = "Low Risk"
                
                # Create three columns for metrics
                col1, col2, col3 = st.columns([1,2,1])
                
                with col2:
                    st.markdown(f"""
<section class="section-card">
<span class="mini-tag">Result</span>
<h3 style="text-align: center;">Voice analysis results</h3>
<p style="text-align: center; font-size: 1.2rem;">Risk level: {risk_level}</p>
<p style="text-align: center;">Confidence: {calculate_confidence(prediction_proba):.1f}%</p>
</section>
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
<section class="section-card">
<span class="mini-tag">Interpretation</span>
<h4>Understanding voice metrics</h4>
<ul>
<li><strong>Jitter</strong>: Variation in fundamental frequency (normal range: 0-0.01)</li>
<li><strong>Shimmer</strong>: Variation in amplitude (normal range: 0-0.1)</li>
<li><strong>HNR</strong>: Harmonics-to-noise ratio (normal range: 15-25)</li>
<li><strong>DFA</strong>: Detrended fluctuation analysis (normal range: 0.5-0.8)</li>
</ul>
</section>
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
                        input_values,
                        result,
                        calculate_confidence(prediction_proba)
                    )
        
        except Exception as e:
            st.error(f"An error occurred: {e}")
            st.info("Please ensure all fields contain valid numeric values.")

# About Page
if (selected == 'About'):
    render_page_hero(
        "About Health AI Studio",
        "Understand how the platform structures screening workflows, interprets model output, and keeps account-linked history organized.",
        "Reference"
    )

    render_feature_grid([
        {
            "tag": "Scope",
            "title": "Three integrated screening modules",
            "body": "The workspace brings diabetes, heart disease, and Parkinson's screening into one account-linked interface."
        },
        {
            "tag": "Output",
            "title": "Confidence-aware interpretation",
            "body": "Results are shown with supporting visual context so users can review both model direction and confidence."
        },
        {
            "tag": "Continuity",
            "title": "History stays tied to the account",
            "body": "Saved assessments remain grouped by user, making repeat screening and follow-up review easier."
        }
    ])

    overview_col, workflow_col = st.columns([1.35, 1], gap="large")
    with overview_col:
        st.markdown("""
<section class="section-card">
<span class="mini-tag">Platform overview</span>
<h3>Built for structured screening, not final diagnosis</h3>
<p>
                Health AI Studio is a machine-learning-assisted screening workspace designed to organize patient-style inputs,
                generate model predictions, and keep outcomes visible across multiple modules. It is intended to support early
                awareness, education, and workflow continuity rather than replace clinical judgment.
</p>
<p>
                Each prediction workflow is centered on guided data entry, confidence scoring, and saved account history so
                users can revisit prior assessments without losing context.
</p>
</section>
        """, unsafe_allow_html=True)

    with workflow_col:
        st.markdown("""
<section class="section-card dark">
<span class="mini-tag">Workflow</span>
<h3>How the platform handles a screening run</h3>
<ol>
<li>Validate numeric or structured input fields for the selected module.</li>
<li>Apply the trained model for that disease-specific screening task.</li>
<li>Estimate confidence and present a readable risk-oriented summary.</li>
<li>Store the result in the signed-in user's prediction history.</li>
</ol>
</section>
        """, unsafe_allow_html=True)

    render_doc_grid([
        {
            "title": "Modeling approach",
            "body": "The platform uses supervised classification models such as random forests, support vector machines, and boosting-based methods depending on the screening dataset."
        },
        {
            "title": "Data processing",
            "body": "Inputs pass through validation, scaling, and disease-specific feature handling before prediction and confidence presentation."
        },
        {
            "title": "Visual interpretation",
            "body": "Probability charts, confidence indicators, distribution views, and contextual tips help users interpret output more clearly."
        }
    ])

    st.markdown("""
<section class="section-card">
<span class="mini-tag">Disease reference</span>
<h3>Condition summaries and prevention context</h3>
<p>Use the tabs below for a high-level review of what each module is screening for, which factors matter most, and which preventive habits remain broadly useful.</p>
</section>
    """, unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["Diabetes", "Heart Disease", "Parkinson's Disease"])

    with tab1:
        render_feature_grid([
            {
                "tag": "Definition",
                "title": "Glucose regulation disorder",
                "body": "Diabetes involves impaired insulin production, insulin response, or both, which can lead to consistently elevated blood glucose."
            },
            {
                "tag": "Risk factors",
                "title": "Metabolic and family history signals",
                "body": "High glucose, obesity, inactivity, high blood pressure, abnormal lipids, age, and family history all increase screening concern."
            },
            {
                "tag": "Prevention",
                "title": "Lifestyle remains the first lever",
                "body": "Weight control, regular movement, balanced nutrition, and repeat health checks remain central to prevention and monitoring."
            }
        ])

    with tab2:
        render_feature_grid([
            {
                "tag": "Definition",
                "title": "Broad cardiovascular disease category",
                "body": "Heart disease includes coronary artery disease, rhythm disorders, and other conditions that affect heart function or circulation."
            },
            {
                "tag": "Risk factors",
                "title": "Pressure, lipids, and lifestyle profile",
                "body": "Blood pressure, cholesterol, smoking, diabetes, age, family history, inactivity, obesity, and stress are major contributors."
            },
            {
                "tag": "Prevention",
                "title": "Control the modifiable drivers",
                "body": "Regular exercise, balanced diet, weight management, limited alcohol intake, smoking avoidance, and routine checkups lower risk."
            }
        ])

    with tab3:
        render_feature_grid([
            {
                "tag": "Definition",
                "title": "Progressive movement disorder",
                "body": "Parkinson's disease affects the nervous system and commonly presents with tremor, slowed movement, rigidity, and balance changes."
            },
            {
                "tag": "Risk factors",
                "title": "Age, heredity, and exposure history",
                "body": "Increasing age, family history, toxin exposure, sex distribution, and past head injury can shape the screening context."
            },
            {
                "tag": "Early signs",
                "title": "Voice and movement changes matter",
                "body": "Tremor, bradykinesia, rigidity, speech changes, posture shifts, and altered handwriting are common early warning signs."
            }
        ])

    st.markdown("""
<section class="section-card">
<span class="mini-tag">Sources</span>
<h3>Data references and further reading</h3>
<p>Datasets include the UCI diabetes dataset, the Cleveland heart disease dataset, and a Parkinson's disease classification dataset. For public health information, review the American Diabetes Association, American Heart Association, Parkinson's Foundation, and World Health Organization websites.</p>
</section>
<div class="disclaimer-note">
<strong>Clinical note:</strong> This application supports screening and education only. It does not replace medical advice, diagnosis, or treatment from a licensed clinician.
</div>
    """, unsafe_allow_html=True)

# History Page
if (selected == 'History'):
    render_page_hero(
        "Your Prediction History",
        "Review previous assessments, filter by disease type, and track confidence trends over time.",
        "History"
    )
    
    # Get user predictions from the database
    predictions_df = get_user_predictions(st.session_state['user']['id'])
    
    if predictions_df.empty:
        st.markdown("""
<section class="section-card">
<h3>No saved assessments yet</h3>
<p>Run any screening module to start building an account-linked prediction history.</p>
</section>
        """, unsafe_allow_html=True)
    else:
        history_df = predictions_df.copy()
        history_df["prediction_type"] = history_df["prediction_type"].fillna("Unknown")
        history_df["result"] = history_df["result"].fillna("No result recorded")
        history_df["created_at"] = pd.to_datetime(history_df["created_at"], errors="coerce")
        history_df["confidence"] = pd.to_numeric(history_df["confidence"], errors="coerce")
        history_df["is_positive"] = history_df["result"].str.contains("positive|has|is diabetic", case=False, na=False)

        latest_stamp = history_df["created_at"].max()
        latest_text = latest_stamp.strftime("%d %b %Y") if pd.notna(latest_stamp) else "Unavailable"
        avg_confidence = history_df["confidence"].mean()
        avg_confidence_text = f"{avg_confidence:.1f}%" if pd.notna(avg_confidence) else "N/A"

        st.markdown(f"""
<section class="stat-grid" style="margin-bottom: 1rem;">
<article class="feature-card">
<span class="tag">Volume</span>
<h4>{len(history_df)}</h4>
<p>Total predictions stored for the current account.</p>
</article>
<article class="feature-card">
<span class="tag">Coverage</span>
<h4>{history_df["prediction_type"].nunique()}</h4>
<p>Distinct screening modules represented in saved history.</p>
</article>
<article class="feature-card">
<span class="tag">Confidence</span>
<h4>{avg_confidence_text}</h4>
<p>Average confidence across all completed assessments.</p>
</article>
</section>
<section class="section-card dark">
<h3>History overview</h3>
<p>Latest recorded activity: {latest_text}. Use the filters below to isolate disease modules and export the current dataset when needed.</p>
</section>
        """, unsafe_allow_html=True)

        tab1, tab2 = st.tabs(["Predictions", "Analysis"])
        
        with tab1:
            col1, col2 = st.columns(2)
            with col1:
                module_options = sorted(history_df["prediction_type"].dropna().unique().tolist())
                disease_filter = st.multiselect(
                    "Filter by Disease Type",
                    options=module_options,
                    default=module_options
                )
            
            with col2:
                date_min = history_df["created_at"].dropna().min()
                date_max = history_df["created_at"].dropna().max()
                date_range = st.date_input(
                    "Date Range",
                    value=(date_min.date(), date_max.date()) if pd.notna(date_min) and pd.notna(date_max) else None
                )

            if isinstance(date_range, tuple) and len(date_range) == 2:
                date_start, date_end = date_range
            else:
                date_start = date_end = date_range
            
            filtered_df = history_df[
                history_df["prediction_type"].isin(disease_filter)
            ].copy()

            if date_start and date_end:
                filtered_df = filtered_df[
                    (filtered_df["created_at"].dt.date >= date_start) &
                    (filtered_df["created_at"].dt.date <= date_end)
                ]

            filtered_df = filtered_df.sort_values("created_at", ascending=False, na_position="last")

            if filtered_df.empty:
                st.info("No saved assessments match the current filters.")
            else:
                for _, row in filtered_df.iterrows():
                    confidence_text = f"{row['confidence']:.1f}%" if pd.notna(row["confidence"]) else "N/A"
                    stamp = row["created_at"].strftime("%Y-%m-%d %H:%M") if pd.notna(row["created_at"]) else "Unavailable"
                    status_class = "positive" if row["is_positive"] else "negative"
                    tone_class = "alert" if row["is_positive"] else "safe"
                    signal_text = "Positive signal" if row["is_positive"] else "No positive signal"
                    st.markdown(f"""
<article class="history-entry {status_class}">
<div class="history-head">
<div>
<span class="mini-tag">{row['prediction_type']}</span>
<h3>{row['result']}</h3>
</div>
<span class="history-stamp">{stamp}</span>
</div>
<p class="history-summary">Saved account-linked prediction record from the selected screening workflow.</p>
<div class="history-meta">
<span class="history-pill {tone_class}">{signal_text}</span>
<span class="history-pill">Confidence {confidence_text}</span>
</div>
</article>
                    """, unsafe_allow_html=True)
        
        with tab2:
            st.subheader("Prediction Analysis")
            
            disease_counts = history_df["prediction_type"].value_counts()
            fig_pie = px.pie(
                values=disease_counts.values,
                names=disease_counts.index,
                title="Distribution of Predictions by Disease Type",
                color_discrete_sequence=["#19c6b3", "#3f7cff", "#ffb74d", "#ef4444", "#8b5cf6"]
            )
            fig_pie.update_traces(textinfo='percent+label')
            st.plotly_chart(fig_pie, use_container_width=True)
            
            st.subheader("Summary Statistics")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric(
                    "Total Predictions",
                    len(history_df),
                    help="Total number of predictions made"
                )
            
            with col2:
                st.metric(
                    "Average Confidence",
                    avg_confidence_text,
                    help="Average confidence across all predictions"
                )
            
            with col3:
                positive_predictions = int(history_df["is_positive"].sum())
                st.metric(
                    "Positive Predictions",
                    f"{positive_predictions}",
                    f"{(positive_predictions/len(history_df)*100):.1f}%",
                    help="Number of positive disease predictions"
                )
            
            st.markdown("---")
            
            st.subheader("Disease-wise Breakdown")
            breakdown_cards = []
            for disease in history_df["prediction_type"].unique():
                disease_df = history_df[history_df["prediction_type"] == disease]
                positive_count = int(disease_df["is_positive"].sum())
                total_count = len(disease_df)
                disease_avg = disease_df["confidence"].mean()
                disease_avg_text = f"{disease_avg:.1f}%" if pd.notna(disease_avg) else "N/A"
                breakdown_cards.append(
                    f"""
<article class="doc-card">
<span class="mini-tag">{disease}</span>
<h3>{total_count} saved assessments</h3>
<p>{positive_count} positive signals recorded. Average confidence: {disease_avg_text}.</p>
</article>
                    """
                )

            st.markdown(f"<section class='doc-grid'>{''.join(breakdown_cards)}</section>", unsafe_allow_html=True)

            export_df = history_df.rename(
                columns={
                    "prediction_type": "Disease",
                    "result": "Prediction Result",
                    "created_at": "Created At",
                    "confidence": "Confidence"
                }
            )[["Disease", "Prediction Result", "Confidence", "Created At"]]
            csv = export_df.to_csv(index=False)
            st.download_button(
                label="Download prediction history CSV",
                data=csv,
                file_name="prediction_history.csv",
                mime="text/csv"
            )

# Add the Requirements page
elif (selected == 'Requirements'):
    render_page_hero(
        "Project Requirements",
        "Dependencies, setup steps, and environment prerequisites for running the application locally.",
        "Setup"
    )
    
    requirements_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "requirements.txt")
    try:
        with open(requirements_path, "r", encoding="utf-8") as req_file:
            requirements_content = req_file.read().strip()
    except OSError:
        requirements_content = ""

    requirement_lines = [
        line.strip() for line in requirements_content.splitlines()
        if line.strip() and not line.strip().startswith("#")
    ]

    render_feature_grid([
        {
            "tag": "Python",
            "title": "Runtime target",
            "body": "Python 3.8 or higher is required. A current Python 3.11 environment is the recommended baseline for local development."
        },
        {
            "tag": "Launch",
            "title": "Root app entry point",
            "body": "The active Streamlit app starts from multiplediseaseprediction.py and should be launched from the project root virtual environment."
        },
        {
            "tag": "Browser",
            "title": "Desktop-first testing",
            "body": "Current layout is optimized for modern Chrome, Edge, and Firefox with responsive stacking for narrower widths."
        }
    ])

    dependency_cards = []
    for line in requirement_lines:
        package_name = line.split("==")[0].split(">=")[0].strip()
        dependency_cards.append({
            "title": line,
            "body": f"{package_name} is part of the current root environment definition for the Streamlit application."
        })

    if dependency_cards:
        if len(dependency_cards) <= 6:
            render_doc_grid(dependency_cards)
        else:
            first_six = []
            for i in range(6):
                first_six.append(dependency_cards[i])
            render_doc_grid(first_six)
            rest = []
            for i in range(6, len(dependency_cards)):
                rest.append(dependency_cards[i])
            render_doc_grid(rest)

    setup_col, support_col = st.columns([1.2, 1], gap="large")
    with setup_col:
        st.markdown("""
<section class="section-card dark">
<span class="mini-tag">Setup flow</span>
<h3>Recommended local run sequence</h3>
<div class="code-card"><code>python -m venv .venv</code></div>
<div class="code-card" style="margin-top: 0.7rem;"><code>.venv\\Scripts\\python.exe -m pip install -r requirements.txt</code></div>
<div class="code-card" style="margin-top: 0.7rem;"><code>.venv\\Scripts\\python.exe -m streamlit run multiplediseaseprediction.py</code></div>
</section>
        """, unsafe_allow_html=True)

    with support_col:
        st.markdown("""
<section class="section-card">
<span class="mini-tag">System baseline</span>
<h3>Minimum operating assumptions</h3>
<p>Supported environments include Windows 10 or later, recent macOS versions, and modern Linux distributions.</p>
<p>A practical baseline is 4 GB RAM, roughly 1 GB of free disk space, and a modern browser with JavaScript enabled.</p>
</section>
        """, unsafe_allow_html=True)

    render_doc_grid([
        {
            "title": "Tools",
            "body": "Git for source control, pip for dependency resolution, and the standard library venv module for isolated environments."
        },
        {
            "title": "Model compatibility",
            "body": "The bundled models were trained against scikit-learn 1.6.1, so that version should stay aligned with the runtime environment."
        },
        {
            "title": "Port management",
            "body": "If port 8501 is already occupied, run the Streamlit command with --server.port 8502 or another free port."
        }
    ])

    with st.expander("Troubleshooting common issues"):
        st.markdown("""
        1. `ModuleNotFoundError` after install usually means the app is running outside the intended virtual environment.
        2. Scikit-learn version warnings indicate the local environment does not match the version used when the models were serialized.
        3. If Streamlit reports a busy port, rerun with `--server.port 8502`.
        4. If a page looks stale after edits, refresh the browser or restart the Streamlit process.
        5. If dependencies drift, recreate `.venv` and reinstall from `requirements.txt`.
        """)

    st.markdown("""
<div class="feedback-note">
<strong>Download:</strong> Use the button below to export the current root <code>requirements.txt</code> file directly from this workspace.
</div>
    """, unsafe_allow_html=True)

    st.download_button(
        label="Download current requirements.txt",
        data=requirements_content or "requirements.txt is not available.",
        file_name="requirements.txt",
        mime="text/plain"
    )

# Enhanced footer with modern design
st.markdown("---")
st.markdown("""
<section class="footer-shell">
<span class="mini-tag">Health AI Studio</span>
<h3>Professional disease screening workflows in one Streamlit workspace</h3>
<p>Designed for guided data entry, model-backed prediction modules, account-linked history, and cleaner visual interpretation.</p>
<div class="footer-links">
<span>Modules: Diabetes, Heart Disease, Parkinson's</span>
<span>History: Saved per account</span>
<span>Version: 2.0.0</span>
</div>
</section>
""", unsafe_allow_html=True)

# Add a feedback form
with st.expander("Provide feedback"):
    st.markdown("""
<div class="feedback-note">
        Help improve the interface by reporting friction points, visual issues, or feature requests from the current root Streamlit app.
</div>
    """, unsafe_allow_html=True)
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
    st.markdown("### Support")
    if st.button("Open support chat", key="chat_button"):
        st.session_state.chat_open = not st.session_state.chat_open
        st.rerun()

# Show chat popup if open
if st.session_state.chat_open:
    with st.sidebar.container():
        st.markdown("""
<div class="helper-card" style="margin-top: 0.75rem;">
<h4>Support chat</h4>
<p>Send a short message about a bug, access issue, or workflow question.</p>
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
    if st.button("Back to top"):
        st.markdown('<script>window.scrollTo(0, 0);</script>', unsafe_allow_html=True)
        st.rerun()

# Remove the background image setting at the end of the file
# Comment out or remove the set_bg_from_url function call
# set_bg_from_url("https://images.everydayhealth.com/homepage/health-topics-2.jpg?w=768", opacity=0.875)


