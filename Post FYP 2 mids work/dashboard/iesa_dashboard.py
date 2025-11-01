import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from streamlit_option_menu import option_menu
import mysql.connector
from mysql_con import get_connection, fetch_table_data
import base64
from PIL import Image
import time

# Importing other dashboard modules
import energy_by_souce
import total_energy
import electricty
import gas

# Set page configuration
st.set_page_config(
    page_title="IESA Dashboard",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for enhanced visuals
st.markdown("""
<style>
    /* Main styles */
    .main {
        background-color: #f8f9fa;
    }
    
    /* Custom container */
    .dashboard-container {
        background-color: white;
        border-radius: 15px;
        padding: 25px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        margin-bottom: 30px;
        animation: fadeIn 0.8s ease-in-out;
    }
    
    /* Dashboard header */
    .dashboard-header {
        background: linear-gradient(90deg, #106466, #329D9C);
        color: white;
        padding: 20px;
        border-radius: 12px;
        margin-bottom: 30px;
        box-shadow: 0 8px 20px rgba(16, 100, 102, 0.3);
        position: relative;
        overflow: hidden;
        animation: slideIn 1s ease-out;
    }
    
    /* Animated gradient accent for headers */
    .dashboard-header::after {
        content: "";
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
        animation: shine 3s infinite;
    }
    
    /* Card styles */
    .info-card {
        background: white;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
        margin-bottom: 20px;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        border-left: 4px solid #106466;
    }
    .info-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
    }
    
    /* Metric styles */
    .metric-container {
        display: flex;
        flex-wrap: wrap;
        gap: 15px;
        margin-bottom: 20px;
    }
    .metric-card {
        background: linear-gradient(135deg, #f8f9fa, #e9ecef);
        border-radius: 10px;
        padding: 20px;
        text-align: center;
        flex: 1;
        min-width: 200px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.05);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
    }
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        margin: 10px 0;
        color: #106466;
    }
    .metric-label {
        font-size: 1rem;
        color: #555;
        font-weight: 500;
    }
    
    /* Section divider */
    .section-divider {
        height: 3px;
        background: linear-gradient(90deg, rgba(16,100,102,0.2), rgba(16,100,102,0.8), rgba(16,100,102,0.2));
        margin: 30px 0;
        border-radius: 2px;
    }
    
    /* Navigation menu styling */
    .nav-link {
        border-radius: 10px !important;
        margin: 5px 0 !important;
        transition: all 0.3s ease !important;
    }
    .nav-link:hover {
        background-color: rgba(16, 100, 102, 0.1) !important;
        transform: translateX(5px);
    }
    .nav-link.active {
        background-color: #106466 !important;
        color: white !important;
        box-shadow: 0 4px 10px rgba(16, 100, 102, 0.4) !important;
    }
    
    /* Animations */
    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }
    @keyframes slideIn {
        from { transform: translateY(-20px); opacity: 0; }
        to { transform: translateY(0); opacity: 1; }
    }
    @keyframes shine {
        to { left: 100%; }
    }
    
    /* Logo container */
    .logo-container {
        text-align: center;
        margin-bottom: 20px;
        animation: fadeIn 1.2s ease-in-out;
    }
    
    /* Footer */
    .footer {
        text-align: center;
        padding: 20px;
        color: #666;
        font-size: 0.9rem;
        border-top: 1px solid #eee;
        margin-top: 40px;
    }
    
    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 10px;
        height: 10px;
    }
    ::-webkit-scrollbar-track {
        background: #f1f1f1;
        border-radius: 10px;
    }
    ::-webkit-scrollbar-thumb {
        background: #106466;
        border-radius: 10px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: #329D9C;
    }
    
    /* Hide default Streamlit elements */
    .css-18e3th9 {
        padding-top: 0;
    }
    #MainMenu, footer, header {
        visibility: hidden;
    }
    
    /* Chart container */
    .chart-container {
        background-color: white;
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    .chart-container:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.12);
    }
</style>
""", unsafe_allow_html=True)

# Function for setting background image
def set_bg_from_local(image_file):
    with open(image_file, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode()
    
    bg_img = f"""
    <style>
    .stApp {{
        background-image: url("data:image/jpeg;base64,{encoded_string}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }}
    </style>
    """
    
    st.markdown(bg_img, unsafe_allow_html=True)

# Set background image
# try:
#     # set_bg_from_local("images/background.jpg")
# except Exception as e:
    # If background image fails to load, use a gradient background
    st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(135deg, #f5f7fa, #c3cfe2);
    }
    </style>
    """, unsafe_allow_html=True)

# Sidebar with IESA logo
with st.sidebar:
    try:
        image = Image.open('images/IESA_logo.png')
        st.image(image, width=250, caption='')
    except Exception as e:
        st.sidebar.title("IESA Dashboard")
    
    st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)
    
    # Side navigation menu
    selected = option_menu(
        menu_title="Dashboard Navigation",
        options=[
            "Dashboard Home", 
            "Energy by Source", 
            "Total Energy", 
            "Electricity", 
            "Natural Gas",
        ],
        icons=[
            'house-fill', 
            'pie-chart-fill', 
            'lightning-fill', 
            'plug-fill', 
            'fire', 
            'person-check',
            'pencil-square',
            'envelope'
        ],
        menu_icon="cast",
        default_index=0,
        styles={
            "container": {"padding": "5px"},
            "icon": {"color": "#106466", "font-size": "16px"},
            "nav-link": {
                "font-size": "14px",
                "text-align": "left",
                "margin": "4px",
                "padding": "10px",
                "--hover-color": "#eee"
            },
            "nav-link-selected": {"background-color": "#106466"},
        }
    )

# Main dashboard layout
if selected == "Dashboard Home":
    # Main header
    st.markdown("<div class='dashboard-header'>", unsafe_allow_html=True)
    st.title("🌍 Integrated Energy System Analytics Dashboard")
    st.markdown("<p style='font-size: 18px;'>Comprehensive energy analytics for intelligent decision making</p>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Dashboard introduction
    st.markdown("<div class='dashboard-container'>", unsafe_allow_html=True)
    st.markdown("### Welcome to the Integrated Energy System Analytics Platform")
    
    # Introduction cards - 3 columns
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="info-card">
            <h4>📊 Data Visualization</h4>
            <p>Interactive charts and graphs for intuitive data exploration and analysis of Pakistan's energy landscape.</p>
        </div>
        """, unsafe_allow_html=True)
        
    with col2:
        st.markdown("""
        <div class="info-card">
            <h4>🔍 Energy Insights</h4>
            <p>Detailed breakdowns of energy production, consumption, and trends across multiple sectors.</p>
        </div>
        """, unsafe_allow_html=True)
        
    with col3:
        st.markdown("""
        <div class="info-card">
            <h4>📈 Performance Tracking</h4>
            <p>Monitor key performance indicators and track progress over time with our advanced analytics tools.</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Key metrics section
    st.markdown("<div class='dashboard-container'>", unsafe_allow_html=True)
    st.subheader("📌 Key Energy Metrics Overview")
    
    # Placeholder data - Replace with actual database data
    try:
        # Fetch some summary data from the database
        conn = get_connection()
        cursor = conn.cursor()
        
        # Example metrics - Replace with actual queries as needed
        cursor.execute("SELECT SUM(energy_production) FROM total_energy WHERE year = 2022")
        total_production = cursor.fetchone()[0]
        
        cursor.execute("SELECT SUM(energy_consumption) FROM total_energy WHERE year = 2022")
        total_consumption = cursor.fetchone()[0]
        
        cursor.execute("SELECT SUM(electricity_production) FROM electricity_production_and_consumption WHERE year = 2022")
        electricity_production = cursor.fetchone()[0]
        
        cursor.execute("SELECT SUM(gas_production) FROM natural_gas_production_and_consumption WHERE year = 2022")
        gas_production = cursor.fetchone()[0]
        
        conn.close()
        
    except Exception as e:
        # Fallback data if the database query fails
        total_production = 85.7
        total_consumption = 79.3
        electricity_production = 41.2
        gas_production = 33.5
    
    # Display key metrics with attractive cards
    st.markdown("<div class='metric-container'>", unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Total Energy Production</div>
        <div class="metric-value">{total_production:.1f} MTOE</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Total Energy Consumption</div>
        <div class="metric-value">{total_consumption:.1f} MTOE</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Electricity Generation</div>
        <div class="metric-value">{electricity_production:.1f} TWh</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Natural Gas Production</div>
        <div class="metric-value">{gas_production:.1f} Bcf</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Overview charts
    st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
    
    # Sample data for energy mix chart - replace with actual data
    try:
        # Get energy mix data
        energy_mix = fetch_table_data("energy_by_source")
        energy_mix = energy_mix.sort_values(by="year", ascending=False).head(1)
        
        # Extract the latest year data and prepare for pie chart
        latest_year = energy_mix["year"].values[0]
        energy_sources = []
        energy_values = []
        
        # Skip the year column (index 0)
        for col in energy_mix.columns[1:]:
            energy_sources.append(col)
            energy_values.append(energy_mix[col].values[0])
        
        # Create the energy mix pie chart
        fig = px.pie(
            values=energy_values,
            names=energy_sources,
            title=f"Energy Mix in Pakistan ({latest_year})",
            color_discrete_sequence=px.colors.sequential.Viridis,
            hole=0.4,
        )
        
        # Update layout
        fig.update_layout(
            legend_title="Energy Sources",
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.1,
                xanchor="center",
                x=0.5
            )
        )
        
        # Add percentage and labels
        fig.update_traces(
            textposition='inside',
            textinfo='percent+label'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
    except Exception as e:
        # Fallback visualization if database query fails
        labels = ['Oil', 'Natural Gas', 'Coal', 'Hydro', 'Nuclear', 'Renewable']
        values = [27, 38, 12, 10, 8, 5]
        
        fig = px.pie(
            values=values,
            names=labels,
            title="Energy Mix in Pakistan (2022)",
            color_discrete_sequence=px.colors.sequential.Viridis,
            hole=0.4,
        )
        
        fig.update_layout(
            legend_title="Energy Sources",
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.1,
                xanchor="center",
                x=0.5
            )
        )
        
        fig.update_traces(
            textposition='inside',
            textinfo='percent+label'
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Energy Trends Section
    st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
    
    try:
        # Get energy trend data
        energy_trend = fetch_table_data("total_energy")
        
        # Create trend visualization
        fig = go.Figure()
        
        # Add production line
        fig.add_trace(
            go.Scatter(
                x=energy_trend["year"], 
                y=energy_trend["energy_production"],
                mode='lines+markers',
                name='Production',
                line=dict(color='#106466', width=3),
                marker=dict(size=8)
            )
        )
        
        # Add consumption line
        fig.add_trace(
            go.Scatter(
                x=energy_trend["year"], 
                y=energy_trend["energy_consumption"],
                mode='lines+markers',
                name='Consumption',
                line=dict(color='#FF6B6B', width=3),
                marker=dict(size=8)
            )
        )
        
        # Update layout
        fig.update_layout(
            title="Energy Production vs. Consumption Trend",
            xaxis_title="Year",
            yaxis_title="Energy (MTOE)",
            legend_title="Energy Metrics",
            hovermode="x unified",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)"
        )
        
        # Add grid lines
        fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(230, 230, 230, 0.8)')
        fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(230, 230, 230, 0.8)')
        
        st.plotly_chart(fig, use_container_width=True)
        
    except Exception as e:
        # Fallback trend chart
        years = [2018, 2019, 2020, 2021, 2022]
        production = [78.2, 80.1, 81.5, 83.4, 85.7]
        consumption = [72.5, 74.8, 75.9, 77.6, 79.3]
        
        fig = go.Figure()
        
        # Add production line
        fig.add_trace(
            go.Scatter(
                x=years, 
                y=production,
                mode='lines+markers',
                name='Production',
                line=dict(color='#106466', width=3),
                marker=dict(size=8)
            )
        )
        
        # Add consumption line
        fig.add_trace(
            go.Scatter(
                x=years, 
                y=consumption,
                mode='lines+markers',
                name='Consumption',
                line=dict(color='#FF6B6B', width=3),
                marker=dict(size=8)
            )
        )
        
        # Update layout
        fig.update_layout(
            title="Energy Production vs. Consumption Trend",
            xaxis_title="Year",
            yaxis_title="Energy (MTOE)",
            legend_title="Energy Metrics",
            hovermode="x unified",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)"
        )
        
        # Add grid lines
        fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(230, 230, 230, 0.8)')
        fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(230, 230, 230, 0.8)')
        
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Navigation Cards to other dashboard sections
    st.markdown("<div class='dashboard-container'>", unsafe_allow_html=True)
    st.markdown("### 🧭 Dashboard Sections")
    
    # Create a nice grid of navigation cards
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="info-card" onclick="parent.window.location.href='#'">
            <h4>⚡ Electricity</h4>
            <p>Detailed analysis of electricity generation, consumption, and pricing trends.</p>
        </div>
        """, unsafe_allow_html=True)
        
    with col2:
        st.markdown("""
        <div class="info-card" onclick="parent.window.location.href='#'">
            <h4>🔥 Natural Gas</h4>
            <p>Comprehensive data on natural gas production, consumption, and infrastructure.</p>
        </div>
        """, unsafe_allow_html=True)
        
    with col3:
        st.markdown("""
        <div class="info-card" onclick="parent.window.location.href='#'">
            <h4>📊 Energy by Source</h4>
            <p>Breakdown of energy production and consumption by source.</p>
        </div>
        """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="info-card" onclick="parent.window.location.href='#'">
            <h4>📈 Total Energy</h4>
            <p>Overall energy landscape with cumulative statistics and trends.</p>
        </div>
        """, unsafe_allow_html=True)
        
    with col2:
        st.markdown("""
        <div class="info-card" onclick="parent.window.location.href='#'">
            <h4>📑 Reports</h4>
            <p>Generate custom reports and export data for your analysis needs.</p>
        </div>
        """, unsafe_allow_html=True)
        
    with col3:
        st.markdown("""
        <div class="info-card" onclick="parent.window.location.href='#'">
            <h4>🔮 Predictions</h4>
            <p>Machine learning based forecasts of future energy trends.</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Footer
    st.markdown("<div class='footer'>", unsafe_allow_html=True)
    st.markdown(
        "© 2025 Integrated Energy System Analytics Dashboard. All rights reserved." 
        " | Version 2.1.0", 
        unsafe_allow_html=True
    )
    st.markdown("</div>", unsafe_allow_html=True)

elif selected == "Energy by Source":
    energy_by_souce.energy_by_souce_dashboard()

elif selected == "Total Energy":
    total_energy.total_energy()

elif selected == "Electricity":
    electricty.electricty_dashboard()

elif selected == "Natural Gas":
    gas.gas_dashboard()

elif selected == "Login":
    st.title("IESA Login")
    # Add more code or import the right module

elif selected == "Data Entry":
    st.title("IESA Data Entry Portal")
    # Add more code or import the right module

elif selected == "Contact Us":
    st.title("Contact IESA")
    # Add more code or import the right module