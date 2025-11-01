import streamlit as st
import pandas as pd
import mysql.connector
import groq
import altair as alt
from smolagents import Tool
from streamlit_option_menu import option_menu
import io
import os
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.utils import ImageReader
from textwrap import wrap
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Paragraph, Spacer
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from utils.logger import setup_logger

# Setup logger
logger = setup_logger("iesa_scenerio_analysis")
logger.info("IESA Scenario Analysis page loaded")

# Initialize sidebar state
if 'sidebar_state' not in st.session_state:
    st.session_state.sidebar_state = 'expanded'
if 'button_text' not in st.session_state:
    st.session_state.button_text = '← Hide'
if 'previous_scenarios' not in st.session_state:
    st.session_state.previous_scenarios = []
if 'should_rerun' not in st.session_state:
    st.session_state.should_rerun = False
if 'scenario_analyses' not in st.session_state:
    st.session_state.scenario_analyses = {}
if 'toggle_triggered' not in st.session_state:
    st.session_state.toggle_triggered = False
if 'rendered_charts' not in st.session_state:
    st.session_state.rendered_charts = {}
if 'chart_keys' not in st.session_state:
    st.session_state.chart_keys = set()
if 'current_action' not in st.session_state:
    st.session_state.current_action = None

# Function to toggle sidebar
def toggle_sidebar():
    if st.session_state.sidebar_state == 'expanded':
        st.session_state.sidebar_state = 'collapsed'
        st.session_state.button_text = '→ Show'
    else:
        st.session_state.sidebar_state = 'expanded'
        st.session_state.button_text = '← Hide'
    st.session_state.should_rerun = True
    st.session_state.toggle_triggered = True

# Function to auto-hide sidebar
def auto_hide_sidebar():
    st.session_state.sidebar_state = 'collapsed'
    st.session_state.button_text = '→ Show'
    st.session_state.should_rerun = True
    st.session_state.toggle_triggered = False

# Function to auto-hide sidebar without rerunning
def auto_hide_sidebar_no_rerun():
    st.session_state.sidebar_state = 'collapsed'
    st.session_state.button_text = '→ Show'
    st.session_state.toggle_triggered = False

# Set page config with initial sidebar state
st.set_page_config(
    page_title="IESA Scenario Analysis",
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

# Database connection
def get_connection():
    return mysql.connector.connect(
        host="localhost",
        port="3306",
        user="root",
        passwd="admin123",
        db="iesa_db"
    )

# Fetch Scenarios from Database
def fetch_scenarios():
    conn = get_connection()
    query = "SELECT category, scenario FROM scenario_definitions;"
    df = pd.read_sql(query, conn)
    conn.close()
    return df

# Fetch predefined query results
def fetch_data(query):
    conn = get_connection()
    df = pd.read_sql(query, conn)
    conn.close()
    return df

# AI-powered Scenario Analysis
client = groq.Client(api_key=None)  # API key removed for security. Use environment variable or .env file.

class ScenarioAnalysisTool(Tool):
    name = "scenario_analysis"
    description = "Analyzes a generated scenario and provides structured insights."
    inputs = {
        "scenario": {"type": "string", "description": "Scenario title."},
        "data_string": {"type": "string", "description": "String representation of the dataset."}
    }
    output_type = "string"

    def forward(self, scenario: str, data_string: str):
        prompt = (f"Analyze the following dataset based on actual trends:\n\n"
                  f"{data_string}\n\n"
                  f"Scenario: {scenario}\n\n"
                  "Provide a concise yet informative analysis with 2-3 main sections. Each section should have a clear heading and 2-3 bullet points with specific insights. Focus exclusively on the data provided.\n\n"
                  "Format your response as follows:\n\n"
                  "## Key Trend Analysis\n"
                  "- Include specific numbers and percentages from the data\n"
                  "- Highlight the most significant pattern observed\n\n"
                  "## Impact Assessment\n"
                  "- Describe direct implications based on the data\n"
                  "- Use comparative analysis when relevant\n\n"
                  "Keep each bullet point concise but informative with data-backed observations.")

        response = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[{"role": "user", "content": prompt}]
        )
        
        return response.choices[0].message.content.strip()

# CSS and JavaScript for dynamic button states
st.markdown("""
    <style>
    /* General Styling */
    header {
        border-bottom: 3px solid  #136a8a !important; 
    }
    [data-testid="stSidebar"] {
        background: linear-gradient(135deg, #73C8A9, #0b8793); /* Gradient background */
        color: white;
        margin-top:58px;
        box-shadow: 2px 0 10px rgba(0,0,0,0.2);
    }
    .sidebar-content {
        margin-top: -60px;
        padding: 20px;
    }
              #MainMenu, footer, header {
        visibility: hidden;
    }
    
    /* Toggle button styles */
    div[data-testid="stHorizontalBlock"] > div:first-child button {
        background-color: #0b8793;
        color: white !important;
        border: 1px solid #4AC29A;
        border-radius: 5px;
        padding: 8px 15px;
        font-weight: bold;
        box-shadow: 0 2px 5px rgba(0,0,0,0.2);
        transition: all 0.3s ease;
    }

    div[data-testid="stHorizontalBlock"] > div:first-child button:hover {
        background-color: #4AC29A;
        transform: translateY(-1px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    
    [data-testid="stSidebar"] h2 {
        font-size: 22px !important;
        margin-top: 25px !important;
        margin-bottom: 15px !important;
        padding-bottom: 5px;
        border-bottom: 2px solid rgba(255,255,255,0.3);
        text-shadow: 1px 1px 2px rgba(0,0,0,0.2);
    }
    
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] label {
        color: rgba(255,255,255,0.9) !important;
        font-weight: 500;
        margin-bottom: 8px;
        font-size: 15px;
    }
    
    [data-testid="stSidebar"] .stSelectbox > div, [data-testid="stSidebar"] .stMultiSelect > div {
        background-color: rgba(255,255,255,0.1) !important;
        border: 1px solid rgba(255,255,255,0.2) !important;
        border-radius: 5px;
        color: white !important;
        margin-bottom: 15px;
    }
    
    [data-testid="stSidebar"] .stSelectbox > div:hover, [data-testid="stSidebar"] .stMultiSelect > div:hover {
        border: 1px solid rgba(255,255,255,0.4) !important;
    }
    
    [data-testid="stSidebar"] span[data-baseweb="tag"] {
        background-color: #73C8A9 !important;
        border: none !important;
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
   
   
    .stButton button {
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
        margin-bottom: 10px;
        letter-spacing: 0.3px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }

    .stButton button:hover {
        background-color: #4AC29A;
        color: white !important;
        box-shadow: 0 3px 7px rgba(0,0,0,0.15);
        transform: translateY(-1px);
    }
    
    a{
        text-decoration: none;
        color: #0F403F !important;
    }
    a:hover{
        color: #0F403F !important;
        text-decoration: none;
    }
    
    /* Chart Improvements */
    .marks{
        border-radius: 15px; /* Rounded corners for the SVG canvas */
        border: 1px solid  #0b8793; /* Greenish border */
        box-shadow: 0px 8px 15px rgba(0, 0, 0, 0.2);
        margin-top: 20px; /* Add some spacing from the buttons */
        padding: 20px; /* Add padding inside the canvas */
        width: 99%; /* Full width */
        background-color: #f9fcfc;
    }
    
    /* Make axes and labels more visible but sharper */
    .chart-wrapper {
        margin-bottom: 30px;
    }
    
    .marks .axis-title, .marks .axis-label {
        font-weight: bold !important;
        font-size: 16px !important;
        fill: #333 !important;
    }
    
    .marks .axis-domain, .marks .axis-tick {
        stroke: #333 !important;
        stroke-width: 2px !important;
    }
    
    .marks .mark-line line {
        stroke-width: 3.5px !important;
    }
    
    .marks .mark-point circle {
        stroke-width: 1.5px !important;
        fill-opacity: 1 !important;
    }
    
    .marks .mark-rule line {
        stroke: #ddd !important;
        stroke-width: 1px !important;
    }
    
    /* Numbers on axes */
    .marks text.role-axis-label {
        font-size: 16px !important;
        font-weight: bold !important;
        fill: #333 !important;
    }
    
    /* Analysis text formatting */
    .scenario-analysis {
        background-color: #f9fcfc;
        border-left: 4px solid #0b8793;
        padding: 20px;
        margin-top: 20px;
        border-radius: 0 5px 5px 0;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    }
    
    .scenario-analysis h3 {
        color: #0b8793;
        margin-bottom: 15px;
    }
    
    .scenario-analysis ul {
        padding-left: 20px;
    }
    
    .scenario-analysis li {
        margin-bottom: 8px;
        line-height: 1.5;
    }
    
    /* Scenario header styling */
    h2 {
        color: #0b8793;
        border-bottom: 2px solid #73C8A9;
        padding-bottom: 8px;
        margin-top: 30px;
        margin-bottom: 20px;
    }
    
    /* Style the download button in the sidebar */
    [data-testid="stDownloadButton"] button {
        background-color: #0b8793 !important;
        color: white !important;
        border: 1px solid #4AC29A !important;
        border-radius: 5px !important;
        padding: 8px 15px !important;
        font-weight: bold !important;
        box-shadow: 0 2px 5px rgba(0,0,0,0.2) !important;
        transition: all 0.3s ease !important;
        width: 100% !important;
    }

    [data-testid="stDownloadButton"] button:hover {
        background-color: #4AC29A !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2) !important;
    }
    
    /* Toggle button styles */
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
    
    /* Remove extra spacing at the top */
    .block-container {
        padding-top: 3rem !important;
    }
    
    /* Adjust header margin */
    header {
        margin-bottom: 0 !important;
    }
    
    /* Adjust top margin for button row */
    div[data-testid="stHorizontalBlock"] {
        margin-top: 25px !important;
        margin-bottom: 20px !important;
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
    [data-testid="stHorizontalBlock"] div:nth-child(3) .stButton button {
        background-color: #4AC29A !important;
        box-shadow: 0 4px 8px rgba(0,0,0,0.25) !important;
        border: 2px solid #73C8A9 !important;
        position: relative;
        transform: translateY(-2px);
    }
    
    /* Add a small indicator below the active button */
    [data-testid="stHorizontalBlock"] div:nth-child(3) .stButton button::after {
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
    
    [data-testid="stSidebar"] h2 {
        margin-top: 0 !important;
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
        margin-top: 0 !important;
    }
    
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
# if prediction_button:
#     os.system("streamlit run iesa_prediction_engine.py")
# if assistant_button:
#     os.system("streamlit run iesa_personalized_recommendations.py")

selected = option_menu(
    menu_title=None,
    options=["Dashboard","Data Planner", "Scenario","Wisdom Mining", "Prediction", "IESA Assistant"],
    icons=["clipboard-data", "bar-chart", "graph-up", "graph-up-arrow", "robot", "robot"],
    default_index=2,
    orientation="horizontal",
    styles={
        "container": {"padding": "0!important", "background-color": "#f0f2f6"},
        "icon": {"color": "106466", "font-size": "18px"},
        "nav-link": {
            "font-size": "16px",
            "text-align": "center",
            "--hover-color": "#eee",
            "padding": "10px"
        },
        "nav-link-selected": {"background-color": "#106466", "color": "white"},
    }
)

# ---- Page Content Rendering ----
if selected == "Data Planner":
    logger.info("User navigated to Data Planner page from Scenario Analysis")
    os.system("streamlit run iesa_data_planner.py")

elif selected == "Dashboard":
    logger.info("User navigated to Dashboard page from Scenario Analysis")
    os.system("streamlit run iesa_dashboard.py")
    
elif selected == "Wisdom Mining":
    logger.info("User navigated to Wisdom Mining page from Scenario Analysis")
    os.system("streamlit run iesa_wisdom_mining.py")
# elif selected == "Scenario":
#     os.system("streamlit run iesa_scenerio_analysis_with_k_means.py")

elif selected == "IESA Assistant":
    logger.info("User navigated to IESA Assistant page from Scenario Analysis")
    os.system("streamlit run iesa_personalized_recommendations.py")

elif selected == "Prediction":
    logger.info("User navigated to Prediction Engine page from Scenario Analysis")
    os.system("streamlit run iesa_prediction_engine.py")

# Streamlit UI
st.sidebar.image("images/iesa_white.svg", width=150)
st.sidebar.markdown("""<h2>IESA Scenario Analysis</h2>""", unsafe_allow_html=True)

# Fetch available scenarios from DB
scenarios_df = fetch_scenarios()
logger.info(f"Fetched scenarios from DB: {scenarios_df.shape[0]} rows")
scenario_categories = {category: list(group["scenario"]) for category, group in scenarios_df.groupby("category")}

# Sidebar - Category Selection
selected_category = st.sidebar.selectbox("Select Category", list(scenario_categories.keys()), key="category_select")

# Sidebar - Multi-Select Scenarios within Category
selected_scenarios = st.sidebar.multiselect("Select Scenarios", scenario_categories[selected_category], key="scenarios_multiselect")

# Check if scenarios selection has changed and auto-hide sidebar if so
if selected_scenarios and selected_scenarios != st.session_state.previous_scenarios:
    st.session_state.current_action = "new_selection"  # Mark that selection changed
    auto_hide_sidebar()
    st.session_state.previous_scenarios = selected_scenarios.copy()

# Query Dictionary for Analysis
query_dict = {
    "Future Electricity Demand Growth": "SELECT Year, `Consumption (GWh)`, ((`Consumption (GWh)` - LAG(`Consumption (GWh)`, 1) OVER (ORDER BY Year)) / LAG(`Consumption (GWh)`, 1) OVER (ORDER BY Year) * 100) AS Growth_Rate FROM annual_electricity_data;",
    "Renewable Energy Contribution": "SELECT Year, `Renewable Electricity`, `Total`, (`Renewable Electricity` / `Total`) * 100 AS Renewable_Percentage FROM primary_energy_supplies_by_source_toe;",
    "Power Shortage Risk": "SELECT Year, `Generation (GWh)`, `Consumption (GWh)`, (`Generation (GWh)` - `Consumption (GWh)`) AS Surplus_Deficit FROM annual_electricity_data;",
    "Impact of Industrial Expansion on Electricity Demand": "SELECT Year, Industrial, (Industrial - LAG(Industrial, 1) OVER (ORDER BY Year)) / LAG(Industrial, 1) OVER (ORDER BY Year) * 100 AS Industrial_Growth_Rate FROM electricity_consumption_by_sector_gwh;",
    "Future Gas Demand Forecast": "SELECT Year, `Natural Gas Consumption`, ((`Natural Gas Consumption` - LAG(`Natural Gas Consumption`, 1) OVER (ORDER BY Year)) / LAG(`Natural Gas Consumption`, 1) OVER (ORDER BY Year)) * 100 AS Growth_Rate FROM natural_gas_production_and_consumption;",
    "Gas Production vs. Consumption Balance": "SELECT Year, `Natural Gas Production`, `Natural Gas Consumption`, (`Natural Gas Production` - `Natural Gas Consumption`) AS Surplus_Deficit FROM natural_gas_production_and_consumption;",
    "Total Energy Demand vs. Supply Balance": "SELECT YEAR, `Total Primary Energy Supply (MTOE)`, `Total Final Consumption of Energy (MTOE)`, (`Total Primary Energy Supply (MTOE)` - `Total Final Consumption of Energy (MTOE)`) AS Surplus_Deficit FROM energy_supply_and_consumption_analysis;",
    "Supply Chain Disruptions in Gas Imports": "SELECT Year, `Imports` FROM total_imports_lng;",
    "Sector-Wise Energy Consumption Changes": "SELECT Year, Total FROM sector_wise_energy_consumption;"
}

# Function to create chart with fixed dimensions
def create_chart(data, scenario, y_col):
    # Format title and handle wrapping for long titles
    chart_title = f"{scenario}: Year vs {y_col}"
    
    # More aggressive wrapping for longer titles
    if len(chart_title) > 35:  # Reduced threshold for wrapping
        parts = chart_title.split(': ')
        if len(parts) > 1:
            chart_title = f"{parts[0]}:\n{parts[1]}"
    
    # Fixed dimensions for consistency
    fixed_width = 550  # Increased fixed width for better title display
    fixed_height = 350  # Height unchanged
    
    # Add top padding to prevent title from being cut off
    padding = {"top": 10, "bottom": 10, "left": 10, "right": 10}
    
    # Title configuration with improved text handling
    title_config = {
        "text": chart_title,
        "fontSize": 16,  # Slightly smaller font for better fit
        "fontWeight": "bold",
        "color": "#0b8793",
        "font": "Arial",
        "anchor": "middle",
        "limit": 500,  # Limit width to ensure text is visible
        "offset": 15   # Move title further from the chart area
    }
    
    try:
        # Handle any NaN or infinite values in the data to prevent errors
        data_clean = data.copy()
        
        # Check if the y column has any NaN or inf values and replace them
        if y_col in data_clean.columns:
            data_clean[y_col] = data_clean[y_col].fillna(0)
            data_clean[y_col] = data_clean[y_col].replace([float('inf'), -float('inf')], 0)
        
        # Create a base chart with fixed dimensions
        base = alt.Chart(data_clean).encode(
            x=alt.X("Year:O", title="Year", axis=alt.Axis(
                labelAngle=0,
                titleFontSize=16,
                labelFontSize=14,
                titleFontWeight='bold',
                labelFontWeight='bold',
                tickWidth=2,
                tickColor='#333333',
                labelColor='#333333',
                titleColor='#333333',
                domainColor='#666666',
                domainWidth=2
            )),
            y=alt.Y(y_col, title=y_col, axis=alt.Axis(
                titleFontSize=16,
                labelFontSize=14,
                titleFontWeight='bold',
                labelFontWeight='bold',
                grid=True,
                gridColor='#e0e0e0',
                tickWidth=2,
                tickColor='#333333',
                labelColor='#333333',
                titleColor='#333333',
                domainColor='#666666',
                domainWidth=2,
                format=',.0f'  # Format numbers without decimals
            ))
        ).properties(
            title=title_config,
            width=fixed_width,
            height=fixed_height
        )
        
        # Add line layer
        line = base.mark_line(
            strokeWidth=3.5,
            clip=True,
            color='#0066cc'
        ).encode(
            tooltip=list(data_clean.columns)
        )
        
        # Add points with enhanced visibility
        points = base.mark_circle(
            size=80,
            opacity=1,
            stroke='#fff',
            strokeWidth=1.5,
            color='#0066cc'
        ).encode(
            tooltip=list(data_clean.columns)
        )
        
        # Combine layers
        final_chart = alt.layer(line, points).configure_view(
            strokeWidth=1,
            stroke='#ddd',
            continuousHeight=fixed_height + padding["top"] + padding["bottom"],
            continuousWidth=fixed_width + padding["left"] + padding["right"]
        ).configure_axis(
            domainWidth=2,
            domainColor='#666666',
            labelFontWeight='bold',
            labelColor='#333333',
            titleColor='#333333',
            tickColor='#666666'
        ).configure_title(
            fontSize=16,
            font='Arial',
            fontWeight='bold',
            anchor='middle',  # Center title
            color='#0b8793',
            offset=20,  # Add more space between title and chart (increased from 15 to 20)
            limit=500,  # Set maximum width for title text
            lineHeight=20  # Add line height for wrapped text
        ).configure_header(
            titleFontSize=16,
            titleColor='#0b8793'
        ).properties(
            padding=padding
        )
        
        return final_chart
    
    except Exception as e:
        # If there's an error in chart creation, show a simpler fallback chart
        st.warning(f"Error creating chart: {str(e)}")
        
        # Create a simple fallback chart
        fallback_chart = alt.Chart(data).mark_line().encode(
            x="Year:O",
            y=y_col
        ).properties(
            title=title_config,
            width=fixed_width,
            height=fixed_height,
            padding=padding
        )
        
        return fallback_chart

# Function to create PDF report for scenario analysis
def create_scenario_report(scenario_analyses=None):
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
    logo_path = "images/iesa_green.png"
    if os.path.exists(logo_path):
        logo = ImageReader(logo_path)
        c.drawImage(logo, width - 80, height - 42, width=60, height=24, mask='auto')
    
    # Title with proper spacing
    c.setFillColor(colors.HexColor("#504B38")) 
    c.setFont("Helvetica-Bold", 22)
    title_text = "IESA Scenario Analysis Report"
    c.drawString((width - c.stringWidth(title_text, "Helvetica-Bold", 22)) / 2, height - 100, title_text)
    
    # Add description
    c.setFillColor(colors.black)
    c.setFont("Helvetica", 11)
    description = "This report presents detailed analysis of energy scenarios based on AI-driven insights."
    
    # Center the description
    desc_width = c.stringWidth(description, "Helvetica", 11)
    c.drawString((width - desc_width) / 2, height - 130, description)
    
    # Horizontal line
    c.setStrokeColor(colors.HexColor("#0b8793"))
    c.setLineWidth(1)
    c.line(60, height - 160, width - 60, height - 160)
    
    # Create paragraph styles
    styles = getSampleStyleSheet()
    styleN = styles["Normal"]
    styleH1 = ParagraphStyle(
        'Heading1',
        parent=styles['Heading1'],
        fontSize=16,
        textColor=colors.HexColor("#0b8793"),
        spaceAfter=12
    )
    styleH2 = ParagraphStyle(
        'Heading2',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor("#0b8793"),
        spaceBefore=6,
        spaceAfter=6
    )
    
    # Section for report introduction
    content_y = height - 190
    c.setFillColor(colors.HexColor("#0b8793"))
    c.setFont("Helvetica-Bold", 16)
    c.drawString(60, content_y, "Scenario Analysis Overview")
    content_y -= 30
    
    c.setFillColor(colors.black)
    c.setFont("Helvetica", 10)
    intro_text = ("The IESA Scenario Analysis tool evaluates various energy scenarios using historical data and "
                 "AI-powered predictive analytics. Each scenario examines different aspects of energy supply, "
                 "demand, and their economic and environmental implications.")
    
    # Wrap and draw introduction text
    for line in wrap(intro_text, width=80):
        c.drawString(60, content_y, line)
        content_y -= 15
    
    content_y -= 20
    
    # Page counters
    page_number = 2
    
    # Check if we have scenario analyses
    if scenario_analyses and len(scenario_analyses) > 0:
        # Draw section title for scenarios
        c.setFillColor(colors.HexColor("#0b8793"))
        c.setFont("Helvetica-Bold", 16)
        c.drawString(60, content_y, "Scenario Detailed Analysis")
        content_y -= 30
        
        # Process each scenario analysis
        for scenario_name, analysis in scenario_analyses.items():
            # Check if we need a new page
            if content_y < 120:
                # Add page number to current page
                c.setFont("Helvetica", 8)
                c.setFillColor(colors.gray)
                c.drawString(width - 80, 15, f"Page {page_number}")
                
                # Create new page
                c.showPage()
                page_number += 1
                
                # Reset position and add header to new page
                content_y = height - 60
                
                # Add orange line at top of new page
                c.setStrokeColor(colors.HexColor("#F06C00"))
                c.setLineWidth(2)
                c.line(20, height - 30, width - 20, height - 30)
                
                # Add small report title to continuation pages
                c.setFillColor(colors.HexColor("#504B38"))
                c.setFont("Helvetica-Bold", 14)
                c.drawString(40, height - 50, "IESA Scenario Analysis Report (Continued)")
            
            # Scenario title with background
            scenario_title_y = content_y
            
            # Draw background box for scenario title
            c.setFillColor(colors.HexColor("#e5f2f2"))
            c.rect(40, scenario_title_y - 15, width - 80, 30, fill=1, stroke=0)
            
            # Draw scenario title
            c.setFillColor(colors.HexColor("#0b8793"))
            c.setFont("Helvetica-Bold", 14)
            c.drawString(50, scenario_title_y, f"Scenario: {scenario_name}")
            
            content_y -= 40
            
            # Process analysis text - handle markdown-like formatting
            analysis_lines = analysis.split('\n')
            
            # Set to normal black text initially
            c.setFillColor(colors.black)
            c.setFont("Helvetica", 10)
            
            for line in analysis_lines:
                # Skip empty lines but leave some space
                if not line.strip():
                    content_y -= 8
                    continue
                
                # Check if we need a new page
                if content_y < 60:
                    # Add page number to current page
                    c.setFont("Helvetica", 8)
                    c.setFillColor(colors.gray)
                    c.drawString(width - 80, 15, f"Page {page_number}")
                    
                    # Create new page
                    c.showPage()
                    page_number += 1
                    
                    # Reset position and add header to new page
                    content_y = height - 60
                    
                    # Add orange line at top of new page
                    c.setStrokeColor(colors.HexColor("#F06C00"))
                    c.setLineWidth(2)
                    c.line(20, height - 30, width - 20, height - 30)
                    
                    # Add small report title to continuation pages
                    c.setFillColor(colors.HexColor("#504B38"))
                    c.setFont("Helvetica-Bold", 14)
                    c.drawString(40, height - 50, "IESA Scenario Analysis Report (Continued)")
                    
                    # Continue with scenario title
                    c.setFillColor(colors.HexColor("#0b8793"))
                    c.setFont("Helvetica-Bold", 12)
                    c.drawString(60, content_y, f"Scenario: {scenario_name} (Continued)")
                    content_y -= 25
                
                # Check for headers
                if line.startswith("## "):
                    # Medium header (h2)
                    c.setFillColor(colors.HexColor("#0b8793"))
                    c.setFont("Helvetica-Bold", 12)
                    text = line[3:].strip()
                    c.drawString(60, content_y, text)
                    
                    # Underline the h2 header
                    text_width = c.stringWidth(text, "Helvetica-Bold", 12)
                    c.setStrokeColor(colors.HexColor("#0b8793"))
                    c.setLineWidth(0.5)
                    c.line(60, content_y - 2, 60 + text_width, content_y - 2)
                    
                    content_y -= 20
                elif line.startswith("# "):
                    # Large header (h1)
                    c.setFillColor(colors.HexColor("#0b8793"))
                    c.setFont("Helvetica-Bold", 14)
                    c.drawString(60, content_y, line[2:].strip())
                    content_y -= 25
                elif line.startswith("- "):
                    # Bullet point
                    c.setFillColor(colors.black)
                    c.setFont("Helvetica", 10)
                    
                    # Draw bullet
                    c.setFont("Helvetica-Bold", 12)
                    c.drawString(60, content_y, "•")
                    c.setFont("Helvetica", 10)
                    
                    # Wrap bullet text with proper indentation
                    bullet_text = line[2:].strip()
                    wrapped_lines = wrap(bullet_text, width=75)
                    
                    # First line
                    if wrapped_lines:
                        c.drawString(75, content_y, wrapped_lines[0])
                        content_y -= 15
                    
                    # Additional wrapped lines with indentation
                    for wrapped_line in wrapped_lines[1:]:
                        c.drawString(75, content_y, wrapped_line)
                        content_y -= 15
                else:
                    # Normal paragraph text
                    c.setFillColor(colors.black)
                    c.setFont("Helvetica", 10)
                    
                    # Wrap text
                    wrapped_lines = wrap(line, width=80)
                    for wrapped_line in wrapped_lines:
                        c.drawString(60, content_y, wrapped_line)
                        content_y -= 15
            
            # Add space between scenarios
            content_y -= 30
            
            # Add separator between scenarios
            c.setStrokeColor(colors.HexColor("#e0e0e0"))
            c.setLineWidth(1)
            c.line(60, content_y + 15, width - 60, content_y + 15)
    else:
        # No analysis message
        c.setFillColor(colors.red)
        c.setFont("Helvetica", 12)
        c.drawString(60, content_y, "No scenario analysis has been generated yet.")
        content_y -= 30
    
    # Add page footer
    c.setStrokeColor(colors.HexColor("#4389a2"))
    c.setLineWidth(2)
    c.line(20, 30, width - 20, 30)
    
    # Footer text
    c.setFont("Helvetica", 8)
    c.setFillColor(colors.gray)
    c.drawString(40, 15, "© 2025 IESA. All rights reserved.")
    c.drawString(width - 80, 15, f"Page {page_number}")
    
    c.save()
    buffer.seek(0)
    return buffer

# Log scenario/category selection and analysis
if selected_category:
    logger.info(f"User selected scenario category: {selected_category}")
    if selected_scenarios:
        logger.info(f"User selected scenarios: {selected_scenarios}")

# Loop through selected scenarios
for scenario in selected_scenarios:
    logger.info(f"Rendering scenario: {scenario}")
    st.markdown(f"## Scenario: {scenario}")

    # Fetch data
    if scenario in query_dict:
        logger.info(f"Fetching data for scenario: {scenario}")
        query = query_dict[scenario]
        data = fetch_data(query)
        logger.info(f"Fetched data for scenario '{scenario}': {data.shape[0]} rows")
        
        if data is not None and not data.empty:
            # Dynamic Charts (Two-column layout)
            num_cols = 2
            cols = st.columns(num_cols)
            y_columns = list(data.columns[1:])  # Exclude 'Year' column

            for idx, y_col in enumerate(y_columns):
                col_idx = idx % num_cols
                chart_key = f"{scenario}_{y_col}"
                
                # Add to tracking of currently displayed charts
                st.session_state.chart_keys.add(chart_key)
                
                with cols[col_idx]:
                    # Create a fixed sized container to ensure consistency
                    container = st.container()
                    
                    # Only create new chart when needed (selection changed, first load, or analysis)
                    if (chart_key not in st.session_state.rendered_charts or 
                        st.session_state.current_action in ["new_selection", "analysis", None]):
                        final_chart = create_chart(data, scenario, y_col)
                        st.session_state.rendered_charts[chart_key] = final_chart
                    else:
                        final_chart = st.session_state.rendered_charts[chart_key]
                    
                    # Use precise dimensions for chart display
                    with container:
                        st.altair_chart(final_chart, use_container_width=False)
        else:
            st.error(f"No data available for scenario: {scenario}")

    # AI Analysis Button for Each Scenario with auto-hide on click
    if st.sidebar.button(f"Analyze {scenario}", on_click=auto_hide_sidebar_no_rerun, key=f"analyze_{scenario}"):
        st.toast(f"Analysis started for {scenario}!", icon="🔎")
        logger.info(f"User requested analysis for scenario: {scenario}")
        st.session_state.current_action = "analysis"  # Mark that we're running analysis
        with st.spinner(f"Analyzing {scenario}... This may take a moments"):
            analysis_tool = ScenarioAnalysisTool()
            data_string = data.to_string(index=False)
            analysis = analysis_tool.forward(scenario, data_string)
            # Store analysis in session state
            st.session_state.scenario_analyses[scenario] = analysis
        
    # Display saved analyses for this scenario
    if scenario in st.session_state.scenario_analyses:
        logger.info(f"Displaying analysis for scenario: {scenario}")
        st.subheader(f"Analysis for {scenario}")
        # Wrap the analysis in a styled div
        st.markdown(f'<div class="scenario-analysis">{st.session_state.scenario_analyses[scenario]}</div>', unsafe_allow_html=True)

# Add report generation button if we have analyses
if st.session_state.scenario_analyses:
    logger.info(f"Scenario analyses available: {len(st.session_state.scenario_analyses)} scenarios")
    st.sidebar.markdown("---")
    st.sidebar.header("Report Options")
    
    # Add report generation button
    st.sidebar.download_button(
        "Download Scenario Analysis Report", 
        create_scenario_report(st.session_state.scenario_analyses),
        "IESA_Scenario_Analysis_Report.pdf",
        "application/pdf"
    )

    # After report download
    if st.sidebar.button("Download Scenario Analysis Report"):
        st.toast("Scenario analysis report downloaded!", icon="⬇️")

# Check if we should rerun the app at the end
if st.session_state.should_rerun:
    st.session_state.should_rerun = False
    # Reset current action after rerun
    st.session_state.current_action = None
    st.rerun()