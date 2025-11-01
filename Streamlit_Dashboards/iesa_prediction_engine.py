import mysql.connector
import pandas as pd
import streamlit as st
from streamlit_option_menu import option_menu
import altair as alt
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures, LabelEncoder, StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.ensemble import RandomForestRegressor
from sklearn.svm import SVR
import io
import os
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.utils import ImageReader
from textwrap import wrap
import math
from utils.logger import setup_logger

# Setup logger
logger = setup_logger("iesa_prediction_engine")
logger.info("IESA Prediction Engine page loaded")

# Initialize sidebar state
if 'sidebar_state' not in st.session_state:
    st.session_state.sidebar_state = 'expanded'
if 'button_text' not in st.session_state:
    st.session_state.button_text = '← Hide'
if 'needs_rerun' not in st.session_state:
    st.session_state.needs_rerun = False
if 'toggle_triggered' not in st.session_state:
    st.session_state.toggle_triggered = False

# Function to toggle sidebar
def toggle_sidebar():
    if st.session_state.sidebar_state == 'expanded':
        st.session_state.sidebar_state = 'collapsed'
        st.session_state.button_text = '→ Show'
    else:
        st.session_state.sidebar_state = 'expanded'
        st.session_state.button_text = '← Hide'
    st.session_state.needs_rerun = True
    st.session_state.toggle_triggered = True
    
st.set_page_config(
    page_title="IESA Dashboard",
    page_icon="📊",
    initial_sidebar_state=st.session_state.sidebar_state,
    layout="wide",
    menu_items={
        'Get Help': 'https://www.linkedin.com/company/104830960',
        'Report a bug': 'https://www.linkedin.com/company/104830960',
        'About': (
            "Intelligent Energy Scenario Analysis (IESA) is an AI-based business intelligence project "
            "that will revolutionize energy scenario analysis by utilizing AI and machine learning to "
            "provide accurate and efficient insights.\n\n"
            "Developers:\n\n"
            "• M. Suffian Tafoor\n\n"
            "• M. Yasir Khan\n\n"
            "• M. Farzam Baig\n\n"
        )
    }
)
# Local image path (Replace with your actual image path)
image_path = "images/iesa_white.svg"
LOGO_PATH = "images/iesa_green.png"  # For PDF

# CSS and JavaScript for dynamic button states
st.markdown("""
    <style>
    /* General Styling */
    header {
        border-bottom: 3px solid  #136a8a !important; 
        margin-bottom: 0 !important;
        position: relative !important;
        z-index: 99 !important;
        height: 2.5rem !important;
    }
    [data-testid="stSidebar"] {
        background: linear-gradient(135deg, #73C8A9, #0b8793); /* Gradient background */
        color: white;
        margin-top: -10px;
        box-shadow: 2px 0 10px rgba(0,0,0,0.2);
        z-index: 98;
        border-right: none;
    }
    .sidebar-content {
        margin-top: -60px;
        padding: 20px;
    }
    
    /* Remove grey background from navigation container */
    section[data-testid="stSectionContainer"] div[data-testid="stVerticalBlock"] {
        background-color: transparent !important;
    }
    
    /* Navigation bar styling - remove borders except bottom */
    [data-baseweb="tab-list"] {
        border-top: none !important;
        border-left: none !important;
        border-right: none !important;
        border-bottom: 2px solid #e0e5eb !important;
        background-color: transparent !important;
    }
    
    /* Remove any backgrounds */
    .stTabs {
        background-color: transparent !important;
    }
    
    .stTabs [data-baseweb="tab-list"] {
        background-color: transparent !important;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: transparent !important;
    }
    
    /* Add bottom bar to active navigation item */
    .nav-link-selected::after {
        content: '' !important;
        position: absolute !important;
        bottom: -3px !important;
        left: 10% !important;
        width: 80% !important;
        height: 4px !important;
        background-color: #73c8a9 !important; 
        border-radius: 2px !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.2) !important;
    }
    
    /* Make the active tab text color the original color */
    .nav-link-selected {
        color: #106466 !important; 
        font-weight: bold !important;
    }
              #MainMenu, footer, header {
        visibility: hidden;
    }
    
    /* Top navigation buttons styling - make all buttons consistent */
    div[data-testid="stHorizontalBlock"] > div .stButton button {
        background-color: #0b8793;
        color: white !important;
        border: 1px solid #4AC29A;
        border-radius: 5px;
        padding: 6px 12px;
        font-weight: bold;
        box-shadow: 0 2px 5px rgba(0,0,0,0.2);
        transition: all 0.3s ease;
        width: auto !important;
        min-width: 120px;
        max-width: 150px;
        margin: 5px auto;
        font-size: 14px;
        white-space: nowrap;
        display: block;
    }

    div[data-testid="stHorizontalBlock"] > div .stButton button:hover {
        background-color: #4AC29A;
        transform: translateY(-1px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    
    /* Toggle button specific styles - target the first button in the first column */
    div[data-testid="stHorizontalBlock"] > div:first-child .stButton button {
        position: relative;
        z-index: 999;
        width: auto !important;
        min-width: 60px;
        max-width: 80px;
    }
    
    /* Highlighted button (active page) */
    [data-testid="stHorizontalBlock"] div:nth-child(4) .stButton button {
        background-color: #4AC29A !important;
        box-shadow: 0 4px 8px rgba(0,0,0,0.25) !important;
        border: 2px solid #73C8A9 !important;
        position: relative;
        transform: translateY(-2px);
    }
    
    /* Add a small indicator below the active button */
    [data-testid="stHorizontalBlock"] div:nth-child(4) .stButton button::after {
        content: '';
        position: absolute;
        bottom: -8px;
        left: 50%;
        transform: translateX(-50%);
        width: 8px;
        height: 8px;
        background-color: #73C8A9;
        border-radius: 50%;
    }
    
    /* Remove extra spacing at the top */
    .block-container {
        padding-top: 0.1rem !important;
    }
    
    /* Main wrapper for streamlit app */
    .main .block-container {
        padding-top: 0.5rem !important;
        margin-top: 0 !important;
    }
    
    /* Fix for option menu container positioning */
    section[data-testid="stSectionContainer"] {
        position: relative;
        z-index: 100;
    }
    
    /* Adjust header margin */
    header {
        margin-bottom: 0 !important;
    }
    
    /* Adjust top margin for button row */
    div[data-testid="stHorizontalBlock"] {
        margin-top: 10px !important;
        margin-bottom: 20px !important;
    }

    [data-testid="stSidebar"] h2 {
        margin-top: 0 !important;
    }
    
    .logo-title-container {
        display: flex;
        flex-direction: row;
        align-items: center;
        justify-content: space-between;
    }
    .logo img {
        width: 60px;
        border-radius: 50%;
    }
    .app-name {
        font-size: 1.5em;
        font-weight: bold;
    }
    
    [data-testid="stBaseButton-secondary"]{
        background-color: #0b8793 !important;
        width:100% !important;
        border: 1px solid #4AC29A;
        border-radius: 5px;
        margin-bottom: 10px;
        color: white !important;
        font-weight: 600;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }

    [data-testid="stBaseButton-secondary"]:hover {
        background-color: #0b8793;
        color: white !important;
        transform: translateY(-2px);
        box-shadow: 0 6px 8px rgba(0, 0, 0, 0.15);
        transition: all 0.2s ease;
    }       
    /* Other sidebar buttons */
    [data-testid="stSidebar"] .stButton button {
        width:100%;
        background-color: #0b8793;
        color: white !important;
        border: 1px solid #4AC29A;
        border-radius: 5px;
        font-size: 0.9em;
        font-weight: bold;
        padding: 8px 20px;
        cursor: pointer;
        transition: all 0.3s ease;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }

    [data-testid="stSidebar"] .stButton button:hover {
        background-color: #0b8793;
        color: white !important;
        transform: translateY(-2px);
        box-shadow: 0 6px 8px rgba(0, 0, 0, 0.15);
    }
    
 
     [data-testid="stWidgetLabel"]{
            color:white !important;
            margin-bottom: 10px;
            }
    /* Sidebar header styling */
    [data-testid="stSidebar"] h2 {
        color: white;
        font-size: 24px;
        padding-bottom: 10px;
        border-bottom: 2px solid rgba(255, 255, 255, 0.2);
        margin-bottom: 20px;
        text-shadow: 1px 1px 3px rgba(0, 0, 0, 0.2);
    }
    
    .marks{
        border-radius: 15px; /* Rounded corners for the SVG canvas */
        border: 1px solid  #0b8793; /* Greenish border */
         box-shadow: 0px 8px 15px rgba(0, 0, 0, 0.2);
        margin-top: 20px; /* Add some spacing from the buttons */
        padding: 10px; /* Add padding inside the canvas */
        width: 99%; /* Full width */
    }
    
    /* Chart title styling */
    .chart-title {
        font-size: 18px;
        font-weight: bold;
        margin-bottom: 15px;
        color: #0b8793;
        text-align: center;
        padding: 5px 0;
    }
    
    /* Improve Altair chart titles */
    .marks .role-title-text {
        font-size: 20px !important;
        font-weight: bold !important;
        fill: #0b8793 !important;
    }
    
    /* Improve axis labels */
    .marks .role-axis-label text {
        font-size: 14px !important;
        font-weight: normal !important;
        fill: #000000 !important; /* Black color */
    }
    
    /* Make tick labels larger and darker */
    .marks .role-axis-domain text {
        font-size: 12px !important;
        font-weight: normal !important;
        fill: #000000 !important;
    }

    /* Main content spacing adjustments */
    .main .block-container > div:nth-child(1) {
        margin-top: 20px !important;
    }
    
    /* Content spacing */
    .main h2, .main h3, .main p {
        margin-top: 10px !important;
    }
    
    [data-testid="stSidebar"] h2 {
    </style>
""", unsafe_allow_html=True)

# # Add the toggle button at the top with a narrower column
# toggle_col1, btn_col1, btn_col2, btn_col3, btn_col4 = st.columns([1, 2, 2, 2, 2])
# with toggle_col1:
#     st.button(st.session_state.button_text, key="toggle_sidebar_button", on_click=toggle_sidebar)
# with btn_col1:
#     data_planner_button = st.button("Data Planner", key="data_planner_button")
# with btn_col2:
#     scenario_button = st.button("Scenario", key="scenario_analysis_button")
# with btn_col3:
#     prediction_button = st.button("Prediction", key="prediction_engine_button")
# with btn_col4:
#     assistant_button = st.button("IESA Assistant", key="personalized_recommendation_button")

# # Handle button clicks
# if data_planner_button:
#     os.system("streamlit run iesa_data_planner.py")
# if scenario_button:
#     os.system("streamlit run iesa_scenerio_analysis.py")
# if assistant_button:
#     os.system("streamlit run iesa_personalized_recommendations.py")

selected = option_menu(
    menu_title=None,
    options=["Dashboard","Data Planner", "Scenario","Wisdom Mining", "Prediction", "IESA Assistant"],
    icons=["clipboard-data", "bar-chart", "graph-up", "graph-up-arrow", "robot", "robot"],
    default_index=4,
    orientation="horizontal",
    styles={
        "container": {
            "padding": "0!important", 
            "background-color": "transparent", 
            "margin-top": "-15px", 
            "position": "relative", 
            "z-index": "100",
            "border-radius": "0px",
            "box-shadow": "none",
            "border": "none",
            "border-bottom": "2px solid #e0e5eb",
            "margin-bottom": "15px"
        },
        "icon": {"color": "106466", "font-size": "18px"},
        "nav-link": {
            "font-size": "16px",
            "text-align": "center",
            "--hover-color": "rgba(255,255,255,0.1)",
            "padding": "10px",
            "margin": "0 2px",
            "position": "relative",
            "border": "none",
            "background-color": "transparent"
        },
        "nav-link-selected": {
            "background-color": "transparent", 
            "color": "#106466",
            "font-weight": "600",
            "border-radius": "0px",
            "border": "none",
            "border-bottom": "3px solid #73c8a9"
        },
    }
)

# ---- Page Content Rendering ----
if selected == "Data Planner":
    logger.info("User navigated to Data Planner page from Prediction Engine")
    os.system("streamlit run iesa_data_planner.py")

elif selected == "Wisdom Mining":
    logger.info("User navigated to Wisdom Mining page from Prediction Engine")
    os.system("streamlit run iesa_wisdom_mining.py")

elif selected == "Dashboard":
    logger.info("User navigated to Dashboard page from Prediction Engine")
    os.system("streamlit run iesa_dashboard.py")

elif selected == "Scenario":
    logger.info("User navigated to Scenario Analysis page from Prediction Engine")
    os.system("streamlit run iesa_scenerio_analysis_with_k_means.py")

elif selected == "IESA Assistant":
    logger.info("User navigated to IESA Assistant page from Prediction Engine")
    os.system("streamlit run iesa_personalized_recommendations.py")

# elif selected == "Prediction":
#      os.system("streamlit run iesa_prediction_engine.py")

if "results" not in st.session_state:
    st.session_state.results = []

if "chart_paths" not in st.session_state:
    st.session_state.chart_paths = []

# Database connection
def get_connection():
    return mysql.connector.connect(
        host="localhost",
        port="3306",
        user="root",
        passwd="admin123",
        db="iesa_db"
    )

# Fetch tables
def fetch_tables():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SHOW TABLES")
        tables = [table[0] for table in cursor.fetchall()]
        conn.close()
        return tables
    except Exception as e:
        st.error(f"Error fetching tables: {e}")
        return []

# Fetch table data
def fetch_table_data(table_name):
    conn = get_connection()
    query = f"SELECT * FROM {table_name}"
    data = pd.read_sql(query, conn)
    conn.close()
    return data

# Ensure X column is numeric
def preprocess_x_column(data, x_column):
    if data[x_column].dtype == 'object':  # Check if it numeric or String for If to be yes it has to be non numeric
        try:
            data[x_column] = data[x_column].astype(str).str[:4].astype(int)# try to convert to year first 4 char from string 2000 cuz year has 4 characters and x axis has only years
        except:
            encoder = LabelEncoder()
            data[x_column] = encoder.fit_transform(data[x_column]) # if conversion fails, use LabelEncoder for giving each input a unique number
    return data

# # Regression Functions
# def perform_linear_regression(data, x_column, y_column):
#     data = preprocess_x_column(data, x_column)
#     X, y = data[[x_column]].values, data[y_column].values
#     X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
#     model = LinearRegression()
#     model.fit(X_train, y_train)
#     y_pred = model.predict(X_test)
#     future_data = pd.DataFrame({x_column: np.arange(data[x_column].max() + 1, data[x_column].max() + 6)})
#     future_data[y_column] = mmodelodel.predict(future_data[[x_column]])
#     return model, mean_squared_error(y_test, y_pred), r2_score(y_test, y_pred), future_data

def perform_linear_regression(data,x_column,y_column):
    data=preprocess_x_column(data,x_column) #
    x,y=data[[x_column]].values,data[[y_column]].values
    model=LinearRegression()
    future_data=pd.DataFrame({x_column:np.arange(data[x_column].max()+1,data[x_column].max()+6)})
    future_data[y_column]=model.fit(x,y).predict(future_data[[x_column]])
    return model,future_data

# def perform_polynomial_regression(data, x_column, y_column, degree=2):
#     data = preprocess_x_column(data, x_column)
#     X, y = data[[x_column]].values, data[y_column].values
#     poly = PolynomialFeatures(degree=degree)
#     X_poly = poly.fit_transform(X)
    
#     X_train, X_test, y_train, y_test = train_test_split(X_poly, y, test_size=0.2, random_state=42)
#     model = LinearRegression()
#     model.fit(X_train, y_train)
#     y_pred = model.predict(X_test)

#     future_data = pd.DataFrame({x_column: np.arange(data[x_column].max() + 1, data[x_column].max() + 6)})
#     future_data[y_column] = model.predict(poly.transform(future_data[[x_column]]))

#     return model, poly, mean_squared_error(y_test, y_pred), r2_score(y_test, y_pred), future_data

def perform_polynomial_regression(data,x_column,y_column):
    data=preprocess_x_column(data,x_column)
    x,y=data[[x_column]].values,data[[y_column]].values
    poly = PolynomialFeatures(degree=3)  # Degree=2 will make parabola kinda U shape curver and 3-4 makes S curve and >5 will cause overfitting
    x_poly=poly.fit_transform(x)
    model=LinearRegression().fit(x_poly,y)
    future_data=pd.DataFrame({x_column:np.arange(data[x_column].max()+1,data[x_column].max()+6)})
    future_poly=poly.transform(future_data[[x_column]])
    future_data[y_column]=model.predict(future_poly)
    return model,future_data

# def perform_random_forest_regression(data, x_column, y_column):
#     data = preprocess_x_column(data, x_column)
#     X, y = data[[x_column]].values, data[y_column].values
#     X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

#     model = RandomForestRegressor(n_estimators=100, random_state=42)
#     model.fit(X_train, y_train)
#     y_pred = model.predict(X_test)

#     future_data = pd.DataFrame({x_column: np.arange(data[x_column].max() + 1, data[x_column].max() + 6)})
#     future_data[y_column] = model.predict(future_data[[x_column]])

#     return model, mean_squared_error(y_test, y_pred), r2_score(y_test, y_pred), future_data

def perform_random_forest_regression(data,x_column,y_column):
    data=preprocess_x_column(data,x_column)
    x,y=data[[x_column]].values,data[[y_column]].values
    model=RandomForestRegressor(n_estimators=100, random_state=42).fit(x,y) # here n is no of decsion trees in the forest  and random state is data randomness
    future_data=pd.DataFrame({x_column:np.arange(data[x_column].max()+1,data[x_column].max()+6)})
    future_data[y_column]=model.predict(future_data[[x_column]])
    return model,future_data

# def perform_svr(data, x_column, y_column):
#     data = preprocess_x_column(data, x_column)
#     X, y = data[[x_column]].values, data[y_column].values

#     scaler_x, scaler_y = StandardScaler(), StandardScaler()
#     X_scaled = scaler_x.fit_transform(X)
#     y_scaled = scaler_y.fit_transform(y.reshape(-1, 1)).flatten()

#     X_train, X_test, y_train, y_test = train_test_split(X_scaled, y_scaled, test_size=0.2, random_state=42)

#     model = SVR(kernel="rbf", C=100, gamma=0.1, epsilon=0.1)
#     model.fit(X_train, y_train)
#     y_pred_scaled = model.predict(X_test)

#     y_pred = scaler_y.inverse_transform(y_pred_scaled.reshape(-1, 1)).flatten()
#     y_test_actual = scaler_y.inverse_transform(y_test.reshape(-1, 1)).flatten()

#     future_x = np.arange(data[x_column].max() + 1, data[x_column].max() + 6).reshape(-1, 1)
#     future_x_scaled = scaler_x.transform(future_x)
#     future_y_scaled = model.predict(future_x_scaled)
#     future_y = scaler_y.inverse_transform(future_y_scaled.reshape(-1, 1)).flatten()

#     future_data = pd.DataFrame({x_column: future_x.flatten(), y_column: future_y})

#     return model, mean_squared_error(y_test_actual, y_pred), r2_score(y_test_actual, y_pred), future_data
def perform_svr(data, x_column, y_column):
    data=preprocess_x_column(data, x_column)
    x,y=data[[x_column]].values, data[y_column].values
    x_scaler = StandardScaler() # to make the mean of data 0 its nromalizes it
    y_scaler = StandardScaler()
    x_scaled=x_scaler.fit_transform(x)
    y_scaled=y_scaler.fit_transform(y.reshape(-1, 1)).flatten() #RBF = good for nonlinear data
    model=SVR(kernel="rbf", C=100, gamma=0.1, epsilon=0.1) # rbg is radical basis fucntion for trade off between bias and variance and c contols smoothness and accuracy 
    # gamma defines how far the influence of a single training example reaches, with low values meaning 'far' and high values meaning 'close'
    # while epsilon defines the width of the epsilon-insensitive tube around the regression line
    # epsilon specfics  margin of error to ignore
    model.fit(x_scaled, y_scaled)

    future_x = np.arange(data[x_column].max() + 1, data[x_column].max() + 6).reshape(-1, 1)
    future_x_scaled = x_scaler.transform(future_x)
    future_y_scaled = model.predict(future_x_scaled)
    future_y = y_scaler.inverse_transform(future_y_scaled.reshape(-1, 1)).flatten()  ## inverse transform the scaled data to get the original data revert the normalized values 
    future_data = pd.DataFrame({x_column: future_x.flatten(), y_column: future_y})
    return model,future_data

# Function to create PDF report for prediction engine
def create_prediction_report(chart_paths=None):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    
    # Header with orange line and logo
    header_y = height - 45
    
    # Add orange line at top
    c.setStrokeColor(colors.HexColor("#F06C00"))  # Orange color
    c.setLineWidth(2)
    c.line(20, header_y, width - 20, header_y)
    
    # Add logo
    if os.path.exists(LOGO_PATH):
        logo = ImageReader(LOGO_PATH)
        c.drawImage(logo, width - 80, height - 42, width=60, height=24, mask='auto')
    
    # Title with proper spacing
    c.setFillColor(colors.HexColor("#504B38")) 
    c.setFont("Helvetica-Bold", 22)
    title_text = "Prediction Engine Report"
    c.drawString((width - c.stringWidth(title_text, "Helvetica-Bold", 22)) / 2, height - 100, title_text)
    
    # Add description
    c.setFillColor(colors.black)
    c.setFont("Helvetica", 11)
    description = "This report presents predictive modeling results using various regression algorithms."
    
    # Center the description
    desc_width = c.stringWidth(description, "Helvetica", 11)
    c.drawString((width - desc_width) / 2, height - 130, description)
    
    # Horizontal line
    c.setStrokeColor(colors.HexColor("#0b8793"))
    c.setLineWidth(1)
    c.line(60, height - 160, width - 60, height - 160)
    
    # Draw section title for models
    model_y = height - 190
    c.setFillColor(colors.HexColor("#0b8793"))
    c.setFont("Helvetica-Bold", 16)
    c.drawString(60, model_y, "Predictive Models Overview")
    
    # Add algorithm descriptions
    algorithm_descriptions = {
        "Linear": "Simple and fast model that assumes a linear relationship between variables.",
        "Polynomial": "Captures non-linear relationships by introducing polynomial terms.",
        "Random Forest": "Ensemble method using multiple decision trees for robust predictions.",
        "SVR": "Support Vector Regression uses kernel functions to model complex relationships."
    }
    
    # Position for charts
    chart_width = 230
    chart_height = 160
    
    # Check if we have chart images
    if chart_paths and len(chart_paths) > 0:
        # Draw algo descriptions first
        c.setFillColor(colors.black)
        c.setFont("Helvetica", 9)
        
        # Add algorithm descriptions in a single block
        algo_y = model_y - 25
        for algo, desc in algorithm_descriptions.items():
            c.setFont("Helvetica-Bold", 10)
            c.drawString(60, algo_y, f"{algo} Regression:")
            c.setFont("Helvetica", 9)
            c.drawString(80, algo_y - 15, desc)
            algo_y -= 30
        
        # Add separator line before charts
        c.setStrokeColor(colors.HexColor("#0b8793"))
        c.setLineWidth(1)
        c.line(60, algo_y - 10, width - 60, algo_y - 10)
        
        # Draw chart title
        chart_section_y = algo_y - 40
        c.setFillColor(colors.HexColor("#0b8793"))
        c.setFont("Helvetica-Bold", 16)
        c.drawString(60, chart_section_y, "Prediction Results")
        
        # Calculate positions for charts with good spacing
        charts_top_y = chart_section_y - 30
        chart1_x = 60
        chart2_x = chart1_x + chart_width + 30
        charts_bottom_y = charts_top_y - chart_height - 30
        
        # Draw charts
        for i, chart_path in enumerate(chart_paths[:4]):  # Limit to 4 charts
            if os.path.exists(chart_path) and i < len(st.session_state["results"]):
                # Calculate position based on index
                row = i // 2  # 0 for top row, 1 for bottom row
                col = i % 2    # 0 for left column, 1 for right column
                
                x_pos = chart1_x if col == 0 else chart2_x
                y_pos = charts_top_y if row == 0 else charts_bottom_y
                
                # Get result info
                result = st.session_state["results"][i]
                
                # Draw chart with border
                c.setStrokeColor(colors.HexColor("#0b8793"))
                c.roundRect(x_pos - 5, y_pos - chart_height - 5, chart_width + 10, chart_height + 10, 5, stroke=1, fill=0)
                
                # Draw the chart image
                c.drawImage(chart_path, x_pos, y_pos - chart_height, width=chart_width, height=chart_height, mask='auto')
                
                # Add chart title and metrics
                title = f"{result['type']} Regression"
                title_width = c.stringWidth(title, "Helvetica-Bold", 10)
                
                # Title centered
                c.setFillColor(colors.HexColor("#0b8793"))
                c.setFont("Helvetica-Bold", 10)
                c.drawString(x_pos + (chart_width - title_width)/2, y_pos - chart_height - 18, title)
        
        # Add page footer
        c.setStrokeColor(colors.HexColor("#4389a2"))
        c.setLineWidth(2)
        c.line(20, 30, width - 20, 30)
        
        # Footer text
        c.setFont("Helvetica", 8)
        c.setFillColor(colors.gray)
        c.drawString(40, 15, "© 2025 IESA. All rights reserved.")
        c.drawString(width - 80, 15, "Page 3")
    else:
        # No charts message
        c.setFillColor(colors.red)
        c.setFont("Helvetica", 12)
        c.drawString(60, model_y - 40, "No prediction models have been generated yet.")
    
    c.save()
    buffer.seek(0)
    return buffer

# Sidebar UI
st.sidebar.image("images/iesa_white.svg", width=150)
st.sidebar.markdown("<h2>Prediction Engine</h2>", unsafe_allow_html=True)

tables = fetch_tables()
logger.info(f"Fetched tables for sidebar: {tables}")
selected_table = st.sidebar.selectbox("Select Table", tables)

if selected_table:
    logger.info(f"User selected table: {selected_table}")
    data = fetch_table_data(selected_table)
    x_column = st.sidebar.selectbox("Select X Column (Independent)", data.columns)
    y_column = st.sidebar.selectbox("Select Y Column (Dependent)", data.columns)

    run_lr = st.sidebar.button("Run Linear Regression")
    run_pr = st.sidebar.button("Run Polynomial Regression")
    run_rf = st.sidebar.button("Run Random Forest Regression")
    run_svr = st.sidebar.button("Run Support Vector Regression")

    # Add report generation button
    if st.session_state.get("results"):
        st.sidebar.markdown("---")
        st.sidebar.download_button(
            "Download Prediction Report", 
            create_prediction_report(st.session_state.chart_paths),
            "IESA_Prediction_Report.pdf",
            "application/pdf"
        )

    # Execute Regression Based on Button Click
    if run_lr and x_column and y_column:
        logger.info(f"Linear Regression run: Table={selected_table}, X={x_column}, Y={y_column}")
        model,future_data = perform_linear_regression(data, x_column, y_column)
        st.session_state.results.append({
            "type": "Linear",
            # "mse": mse,
            # "r2": r2,
            "x_column": x_column,
            "y_column": y_column,
            "data": data.copy(),
            "future_data": future_data.copy()
        })
        st.toast("Linear Regression run!", icon="📈")

    if run_pr and x_column and y_column:
        logger.info(f"Polynomial Regression run: Table={selected_table}, X={x_column}, Y={y_column}")
        # model, poly, mse, r2, future_data = perform_polynomial_regression(data, x_column, y_column)
        model,future_data = perform_polynomial_regression(data, x_column, y_column)
        st.session_state.results.append({
            "type": "Polynomial",
            # "mse": mse,
            # "r2": r2,
            "x_column": x_column,
            "y_column": y_column,
            "data": data.copy(),
            "future_data": future_data.copy()
        })
        st.toast("Polynomial Regression run!", icon="📉")

    if run_rf and x_column and y_column:
        logger.info(f"Random Forest Regression run: Table={selected_table}, X={x_column}, Y={y_column}")
        model,future_data = perform_random_forest_regression(data, x_column, y_column)
        st.session_state.results.append({
            "type": "Random Forest",
            # "mse": mse,
            # "r2": r2,
            "x_column": x_column,
            "y_column": y_column,
            "data": data.copy(),
            "future_data": future_data.copy()
        })
        st.toast("Random Forest Regression run!", icon="🌳")

    if run_svr and x_column and y_column:
        logger.info(f"SVR Regression run: Table={selected_table}, X={x_column}, Y={y_column}")
        model, future_data = perform_svr(data, x_column, y_column)
        st.session_state.results.append({
            "type": "SVR",
            # "mse": mse,
            # "r2": r2,
            "x_column": x_column,
            "y_column": y_column,
            "data": data.copy(),
            "future_data": future_data.copy()
        })
        st.toast("SVR Regression run!", icon="🤖")

# Display Results
if st.session_state.get("results"):
    # Clear previous chart paths
    st.session_state.chart_paths = []
    
    # Create folder for chart images if it doesn't exist
    chart_folder = "chart_images"
    os.makedirs(chart_folder, exist_ok=True)
    
    col1, col2 = st.columns(2)
    for index, result in enumerate(st.session_state.results):
        with (col1 if index % 2 == 0 else col2):
            # Add a custom, more prominent title
            st.markdown(f"<div class='chart-title'>{result['type']} Regression</div>", unsafe_allow_html=True)
            
            # Create chart with improved axis formatting
            actual_chart = alt.Chart(result["data"]).mark_line().encode(
                x=alt.X(
                    result["x_column"], 
                    title=result["x_column"].upper(),
                    axis=alt.Axis(
                        labelColor='black',
                        labelFontSize=14,
                        labelFontWeight='normal',
                        titleColor='black',
                        titleFontSize=16,
                        titleFontWeight='normal'
                    )
                ),
                y=alt.Y(
                    result["y_column"], 
                    title=result["y_column"].upper(),
                    axis=alt.Axis(
                        labelColor='black',
                        labelFontSize=14,
                        labelFontWeight='normal',
                        titleColor='black',
                        titleFontSize=16,
                        titleFontWeight='normal'
                    )
                ),
                color=alt.value('blue'),
                tooltip=[result["x_column"], result["y_column"]]
            ).properties(
                title=f"{result['type']} Regression: Actual vs Predicted",
                width=500,
                height=350
            )

            prediction_chart = alt.Chart(result["future_data"]).mark_line(color='red').encode(
                x=alt.X(
                    result["x_column"], 
                    title=result["x_column"].upper(),
                    axis=alt.Axis(
                        labelColor='black',
                        labelFontSize=14,
                        labelFontWeight='normal',
                        titleColor='black',
                        titleFontSize=16,
                        titleFontWeight='normal'
                    )
                ),
                y=alt.Y(
                    result["y_column"], 
                    title=result["y_column"].upper(),
                    axis=alt.Axis(
                        labelColor='black',
                        labelFontSize=14,
                        labelFontWeight='normal',
                        titleColor='black',
                        titleFontSize=16,
                        titleFontWeight='normal'
                    )
                ),
                tooltip=[result["x_column"], result["y_column"]]
            ).properties(
                width=500,
                height=350
            )
            
            # Combined chart
            combined_chart = actual_chart + prediction_chart
            
            # Save chart for report
            chart_path = os.path.join(chart_folder, f"{result['type']}_regression_{index}.png")
            combined_chart.save(chart_path)
            st.session_state.chart_paths.append(chart_path)
            
            # Display chart
            st.altair_chart(combined_chart, use_container_width=True)

