import streamlit as st
import pandas as pd
import base64
import altair as alt
import random
import os
st.set_page_config(page_title="IESA Dashboard", layout="wide", page_icon="📊")

# Function to convert an image to Base64
def image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        encoded_image = base64.b64encode(image_file.read()).decode()
    return f"data:image/png;base64,{encoded_image}"

# Local image path (Replace with your actual image path)
image_path = "IESA_logo.png"

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
    }
    .sidebar-content {
        margin-top: -60px;
        padding: 20px;
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
    .top-bar {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-top: -10px;
    }
    .nav-links > button {
        background-color: transparent;
        border: none;
        font-size: 1em;
        font-weight: 500;
        cursor: pointer;
        margin: 0 5px;
        border-bottom: 2px solid transparent;
        transition: all 0.3s ease;
        color: white; /* Anchor text color */
    }
    .nav-links > button.active {
        border-bottom: 2px solid red; /* Persistent red border for active button */
    }
    .nav-links > button:hover {
        border-bottom: 2px solid green; /* Green border on hover */
    }
    
    .stButton button {
       background-color: #0F403F;
        color: white;
        border: 1px solid #0F403F;
        border-radius: 20px;
        
        font-size: 0.9em;
        font-weight: bold;
        padding: 6px 20px;
        cursor: pointer;
        transition: all 0.3s ease;
        width: 100%;
    }
    .stButton button:hover {
       background-color: #0F403F;
        color: white;
    }
    a{
        text-decoration: none;
        color: #0F403F !important;
    }
    a:hover{
        color: #0F403F !important;
        text-decoration: none;
    }
    

    /* Metric Buttons */
    .metric-buttons {
        display: flex;
        justify-content:space-between;  /* Centers buttons horizontally */
       
        flex-wrap: wrap;  /* Ensures buttons wrap on smaller screens */
        margin-top: 20px;  /* Add some spacing from other elements */
    }

    .sum-button, .count-button, .total-button, .unique-button {
        padding: 8px 15px;  /* Reduced padding */
        border-radius: 12px;  /* Slightly smaller border radius */
        text-align: center;
        margin: 5px;
        color: white;
        font-weight: bold;
        cursor: pointer;
        transition: all 0.3s ease;
        box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);
        border: none;
        width: 120px;  /* Set a fixed width for each button */
        font-size: 0.85em;  /* Reduced font size */
    }

    /* Greenish Gradient (matching sidebar) */
    .sum-button { 
        background: linear-gradient(135deg, #73C8A9, #0b8793);  /* Sidebar-like greenish tones */
    }

    /* Redish Gradient (lighter tones) */
    .count-button { 
        background: linear-gradient(135deg, #FF6F61, #DE4313);  /* Lighter red gradient */
    }

    /* Blueish Gradient (lighter tones) */
    .total-button { 
        background: linear-gradient(135deg, #56CCF2, #2F80ED);  /* Lighter blue gradient */
    }

    /* Soft Greenish Gradient for Unique Button */
    .unique-button { 
        background: linear-gradient(135deg, #A5D6A7, #66BB6A);  /* Soft green gradient */
    }

    /* Hover effects */
    .sum-button:hover, .count-button:hover, .total-button:hover, .unique-button:hover {
        transform: translateY(-5px);
        box-shadow: 0px 8px 15px rgba(0, 0, 0, 0.2);
    }
    .marks{
        border-radius: 15px; /* Rounded corners for the SVG canvas */
        border: 1px solid  #0b8793; /* Greenish border */
         box-shadow: 0px 8px 15px rgba(0, 0, 0, 0.2);
        margin-top: 20px; /* Add some spacing from the buttons */
        padding: 10px; /* Add padding inside the canvas */
        width: 99%; /* Full width */
    }
    </style>

    <script>
    document.addEventListener('DOMContentLoaded', function () {
        const navButtons = document.querySelectorAll('.nav-links button');
        navButtons.forEach(button => {
            button.addEventListener('click', function () {
                navButtons.forEach(btn => btn.classList.remove('active'));
                this.classList.add('active');
            });
        });
    });
    </script>
""", unsafe_allow_html=True)

# Sidebar Content
with st.sidebar:
    st.markdown(
        f"""
        <div class="sidebar-content">
            <div class="logo-title-container">
                <div class="logo">
                    <img src="{image_to_base64(image_path)}" alt="IESA Logo">
                </div>
                <div class="app-name">IESA Dashboard</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.subheader("Input Data Type")
    input_type = st.selectbox("Select Data Type", ["Energy Data", "Gas Data", "Electricity Data"])

    uploaded_file = st.file_uploader(f"Upload {input_type} File", type=["xlsx"])
    # Python button actions
    col1, col2 = st.columns(2)

    with col1:
        if st.button("Logout", key="logout_button"):
            os.system("streamlit run streamlit_dashboard_login_page_v2.py")

    with col2:
        if st.button("Contact Us", key="contact_us_button"):
            os.system("streamlit run streamlit_dashboard_contact_us_page.py")
    if uploaded_file:
        try:
            data = pd.read_excel(uploaded_file)
            numeric_columns = [col for col in data.columns if pd.api.types.is_numeric_dtype(data[col])]

            st.subheader("Choose how to display data")
            basis_selection = st.selectbox("Select a column to analyze:", options=numeric_columns, index=0 if numeric_columns else None)

        except Exception as e:
            st.error(f"An error occurred: {e}")

# Top Bar Content
st.markdown(
    """
    <div class="top-bar">
        <div class="nav-links">
            <button class="active"><a href="#home">Home</a></button>
            <button><a href="#scenarios">Scenarios</a></button>
            <button><a href="#predictions">Predictions</a></button>
            <button><a href="#report">Report</a></button>
            <button><a href="#recommendations">Recommendations</a></button>    
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


# Main Content Area
if uploaded_file and basis_selection:
        if "Year" in data.columns:
            year_options = ["All"] + sorted(data["Year"].unique())
            year_filter = st.multiselect("", options=year_options, default="All")
            if "All" in year_filter or not year_filter:
                filtered_data = data
            else:
                filtered_data = data[data["Year"].isin(year_filter)]
        else:
            st.warning("No 'Year' column found in the uploaded data.")
            filtered_data = data

        # Wrap buttons in a flex container
        st.markdown("""
            <div class="metric-buttons">
                <button class="sum-button">Sum: {}</button>
                <button class="count-button">Count: {}</button>
                <button class="total-button">Total: {}</button>
                <button class="unique-button">Unique: {}</button>
            </div>
        """.format(
            data.select_dtypes("number").sum().sum(),
            data.shape[0],
            data.select_dtypes("number").sum().sum(),
            data.nunique().sum()
        ), unsafe_allow_html=True)

            # Altair Bar Chart with Different Colors for Bars
        cols = st.columns(2)
        with cols[0]:
            if "Year" in filtered_data.columns and basis_selection:
                # Add a new column 'Color' for random greenish color assignment
                filtered_data['Color'] = [
                    random.choice(["#73C8A9", "#0b8793"]) for _ in range(len(filtered_data))
                ]
                
                # Create the bar chart with the new color column
                bar_chart = alt.Chart(filtered_data).mark_bar().encode(
                    x="Year:O",
                    y=f"{basis_selection}:Q",
                    color=alt.Color("Color:N", scale=None, legend=None),  # Use the new 'Color' column for the color encoding and disable the scale
                    tooltip=["Year", basis_selection]
                ).properties(
                    title=f"{basis_selection} per Year",
                    width=500,
                    height=350
                ).configure_title(
                    fontSize=16,
                    fontWeight="bold",
                    font="Arial",
                    color="#0F403F"
                ).configure_axis(
                    grid=False,
                    labelFontSize=12,
                    titleFontSize=14,
                    labelColor="#0F403F",
                    titleColor="#0F403F"
                ).configure_legend(
                    labelFontSize=12,
                    titleFontSize=14,
                    labelColor="#0F403F",
                    titleColor="#0F403F",
                    orient="none"  # Remove the legend
                )
                st.altair_chart(bar_chart, use_container_width=True)
        # Altair Line Chart
        with cols[1]:
            if "Year" in filtered_data.columns and basis_selection:
                line_chart = alt.Chart(filtered_data).mark_line(color="#56CCF2").encode(
                    x="Year:O",
                    y=f"{basis_selection}:Q",
                    tooltip=["Year", basis_selection]
                ).properties(
                    title=f"{basis_selection} Over Time",
                    width=500,
                    height=350
                ).configure_title(
                    fontSize=16,
                    fontWeight="bold",
                    font="Arial",
                    color="#0F403F"
                ).configure_axis(
                    grid=False,
                    labelFontSize=12,
                    titleFontSize=14,
                    labelColor="#0F403F",
                    titleColor="#0F403F"
                ).configure_legend(
                    labelFontSize=12,
                    titleFontSize=14,
                    labelColor="#0F403F",
                    titleColor="#0F403F"
                )
                st.altair_chart(line_chart, use_container_width=True)