import streamlit as st
import pandas as pd
import os
from io import BytesIO
import altair as alt
import random
from utils.logger import setup_logger

# Setup logger
logger = setup_logger("iesa_input_entry_operator")
logger.info("IESA Input Entry Operator page loaded")

st.set_page_config(
    page_title="IESA Input Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
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

# CSS Styling
st.markdown(
    """
    <style>
    /* General Styling */
    header {
        border-bottom: 3px solid #136a8a !important;
    }
    [data-testid="stSidebar"] {
        background: linear-gradient(135deg, #73C8A9, #0b8793);
        color: white;
        margin-top: 58px;
    }
    [data-testid="stSidebar"] .stSelectbox{
        width: 100% !important;
    }
    .sidebar-content {
        margin-top: -60px;
        padding: 20px;
    }
    .sidebar-content * {
        color: white !important; /* Ensure all sidebar text is white */
    }
    .app-name {
        font-size: 25px;
        font-weight:600;
    }
   
    
    .stButton button {
        width:100%;
        background-color: #0b8793;
        color: white !important;
        border: 1px solid #4AC29A;
        border-radius: 5px;
        font-size: 0.9em;
        font-weight: bold;
        padding: 6px 20px;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    
    .stButton button:hover {
        background-color: #0b8793;
        color: white !important;
    }
    .stDownloadButton button {
       
        background-color: #0b8793;
        color: white !important;
        border: 1px solid #4AC29A;
        border-radius: 5px;
        font-size: 0.9em;
        font-weight: bold;
        padding: 6px 20px;
        cursor: pointer;
        transition: all 0.3s ease;
        
    }
    .summary-metrics {
        display: flex;
        gap: 20px;
        margin-top: 20px;
        margin-bottom: 20px;
    }
    .metric-box {
        border: 2px solid #4AC29A;
        padding: 10px;
        border-radius: 10px;
        text-align: center;
        flex: 1;
    }
    h1, h2, h3 {
        font-size: 1.5rem !important;
    }
   
    /* Styling the DataFrame */
    .stDataFrame {
        width: 100%;
        border: 1px solid  #4AC29A;
        border-radius: 7px;
    }
    
    /* Custom Styling for Success and Error Messages */
    .stAlert {
        width: 80%;
        border-radius: 5px;
        font-size: 14px;
        font-weight: bold;
    }

    .custom-success {
        background-color: #0b8793;
        color: #FFFFFF;
        padding: 10px;
        border-radius: 5px;
        margin: 10px 0;
        width: 100%;
        font-size: 14px;
        font-weight: bold;
        box-shadow: 0 4px 6px rgba(11, 135, 147, 0.2);
    }

    .custom-error {
        background-color: #FF6B6B;
        color: #FFFFFF;
        padding: 10px;
        border-radius: 5px;
        margin: 10px 0;
        width: 100%;
        font-size: 14px;
        font-weight: bold;
        box-shadow: 0 4px 6px rgba(255, 107, 107, 0.2);
    }
    /* Full-width select boxes */
    
    
    .stSelectbox{
         width: 40% !important;
          
    }
   .stSelectbox >div >div{
       border: 1px solid  #0b8793; /* Greenish border */
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
    """,
    unsafe_allow_html=True,
)

# Function to reset the buttons if needed
def reset_buttons():
    st.session_state["show_quality"] = False
    st.session_state["show_etl"] = False
    st.session_state["show_visualization"] = False
   
with st.sidebar:
    st.image("images/iesa_white.svg",width=150)
    st.markdown("""
    <h3>Input Entry operator Dashboard</h3>
    """,unsafe_allow_html=True)
    input_type = st.selectbox("Select Data Type", ["Energy Data", "Gas Data", "Electricity Data"])
    logger.info(f"User selected input type: {input_type}")
    uploaded_file = st.file_uploader(f"Upload {input_type} File", type=["xlsx"])
    if uploaded_file:
        logger.info(f"File uploaded: {uploaded_file.name} for {input_type}")
    if st.button("Check Data Quality", key="data_quality_button"):
        logger.info("Check Data Quality button clicked")
        st.session_state["show_quality"] = True
    if st.button("Perform ETL", key="perform_etl_button"):
        logger.info("Perform ETL button clicked")
        st.session_state["show_etl"] = True
    if st.button("Visualize Data", key="visualize_button"):
        logger.info("Visualize Data button clicked")
        st.session_state["show_visualization"] = True
    if st.button("Reset", key="reset_button"):
        logger.info("Reset button clicked")
        reset_buttons()
    st.markdown("<hr>", unsafe_allow_html=True)
    if st.button("Logout", key="logout_button"):
        logger.info("User logged out from Input Entry Operator")
        os.system("streamlit run iesa_login.py")
    if st.button("Contact Us", key="contact_us_button"):
        logger.info("User clicked Contact Us from Input Entry Operator (navigating to Contact Us page)")
        os.system("streamlit run iesa_contact_us.py")

# Main Content
if uploaded_file:
    try:
        data = pd.read_excel(uploaded_file)
        logger.info(f"Data loaded from uploaded file: {uploaded_file.name}, shape={data.shape}")
        st.toast(f"File '{uploaded_file.name}' uploaded successfully!", icon="📤")
        st.markdown("<h3>Data Preview:</h3>", unsafe_allow_html=True)
        st.write(data.head())
        
        # Data Validation and Quality Checks
        if st.session_state.get("show_quality"):
            logger.info("Performing data quality check")
            quality_results = []
            error_messages = []
            for column in data.columns:
                total = len(data)
                valid = data[column].dropna().apply(lambda x: isinstance(x, (int, float, str))).sum()
                empty = data[column].isnull().sum()
                duplicate = data[column].duplicated(keep=False).sum()
                logger.info(f"Column: {column}, Valid: {valid}, Empty: {empty}, Duplicate: {duplicate}")
                quality_results.append(
                    {
                        "Column": column,
                        "Valid": f"{valid} ({valid/total:.0%})",
                        "Error": f"{duplicate} ({duplicate/total:.0%})",
                        "Empty": f"{empty} ({empty/total:.0%})",
                    }
                )

                if empty > 0:
                    error_messages.append(f"Column '{column}' has {empty} empty values.")
                if duplicate > 0:
                    error_messages.append(f"Column '{column}' has {duplicate} duplicate values.")

            quality_df = pd.DataFrame(quality_results)
            st.markdown("<h3>Data Quality Check</h3>", unsafe_allow_html=True)
            st.write(quality_df)

            if error_messages:
                logger.warning(f"Data quality issues: {'; '.join(error_messages)}")
                st.toast("Data quality issues found!", icon="⚠️")
                # Custom Error Message Styling
                st.markdown(
                    f'<div class="custom-error">{"<br>".join(error_messages)}</div>',
                    unsafe_allow_html=True,
                )
            else:
                st.toast("Data quality check passed!", icon="✅")

            if st.button("Preview Full Data",type="secondary"):
                logger.info("User previewed full data table")
                st.write(data)

        # Perform ETL if required
        if st.session_state.get("show_etl"):
            logger.info("Performing ETL process")
            # Data Cleaning Steps
            st.markdown("<h3>Performing ETL Process...</h3>", unsafe_allow_html=True)
            
            # Standardize column names
            data.columns = [col.strip().lower().replace(" ", "_") for col in data.columns]

            # Drop duplicates
            duplicates_before = data.duplicated().sum()
            data = data.drop_duplicates()
            duplicates_after = data.duplicated().sum()

            # Replace empty values based on column data types
            empty_values_before = data.isnull().sum().sum()
            for col in data.columns:
                if data[col].dtype == "object":  # Replace empty strings with "null"
                    data[col].fillna("null", inplace=True)
                else:  # Replace empty numeric values with 0
                    data[col].fillna(0, inplace=True)
            empty_values_after = data.isnull().sum().sum()

            # Convert columns to appropriate data types dynamically
            for col in data.columns:
                try:
                    # Check if the column can be converted to numeric
                    data[col] = pd.to_numeric(data[col], errors='ignore')
                    
                    # Check if the column can be converted to datetime
                    if not pd.api.types.is_numeric_dtype(data[col]):
                        data[col] = pd.to_datetime(data[col], errors='ignore')

                    # If stilll not numeric or datetime, leave it as string/object
                except Exception as e:
                    logger.error(f"Error processing column {col}: {e}")


            # Custom Success Message Styling
            st.markdown(
                '<div class="custom-success">ETL process completed. Updated data is shown below.</div>',
                unsafe_allow_html=True,
            )
            st.toast("ETL process completed!", icon="🔄")

            st.write(data.head())

            # Display summary of cleaning
            st.markdown(
                f"""
                <div class="summary-metrics">
                    <div class="metric-box">
                        <strong>Duplicates Removed</strong>
                        <div>{duplicates_before - duplicates_after}</div>
                    </div>
                    <div class="metric-box">
                        <strong>Empty Values Replaced</strong>
                        <div>{empty_values_before - empty_values_after}</div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            # Export Processed Data
            buffer = BytesIO()
            data.to_excel(buffer, index=False)
            buffer.seek(0)
            if st.download_button("Download Processed Data", buffer, file_name="processed_data.xlsx"):
                logger.info("User downloaded processed data after ETL")
                st.toast("Data downloaded!", icon="⬇️")
            logger.info("ETL process completed")

        # Input Summary
        st.subheader("Data Summary")
        duplicate_rows = data.duplicated().sum()
        missing_values = data.isnull().sum().sum()
        logger.info(f"Data summary: rows={data.shape[0]}, columns={data.shape[1]}, duplicates={duplicate_rows}, missing={missing_values}")
        st.markdown(
            f"""
            <div class="summary-metrics">
                <div class="metric-box">
                    <strong>Total Rows</strong>
                    <div>{data.shape[0]}</div>
                </div>
                <div class="metric-box">
                    <strong>Total Columns</strong>
                    <div>{data.shape[1]}</div>
                </div>
                <div class="metric-box">
                    <strong>Duplicate Rows</strong>
                    <div>{duplicate_rows}</div>
                </div>
                <div class="metric-box">
                    <strong>Missing Values</strong>
                    <div>{missing_values}</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
       
       # Visualization Section
        if st.session_state.get("show_visualization"):
            logger.info("Performing data visualization")
            st.markdown("<h3>Data Visualization:</h3>", unsafe_allow_html=True)
            # Ensure there are at least two columns in the dataset
            columns = data.columns.tolist()

            if len(columns) < 2:
                logger.warning("Visualization failed: less than 2 columns in dataset")
                st.warning("The dataset must have at least two columns for visualization.")
            else:
                # Input selection for X-axis and Y-axis
                x_axis = st.selectbox("Select X-axis:", columns, key="x_axis_selector")
                y_axis = st.selectbox("Select Y-axis:", columns, key="y_axis_selector")
                logger.info(f"User selected visualization: X={x_axis}, Y={y_axis}")

                # Define individual charts
                line_chart = alt.Chart(data).mark_line(color="#56CCF2").encode(
                    x=f"{x_axis}:O",  # Set X-axis to ordinal
                    y=f"{y_axis}:Q",  # Set Y-axis to quantitative
                    tooltip=[x_axis, y_axis]
                ).properties(
                    title=f"{y_axis} Over {x_axis}",
                    width=500,  # Set a fixed width
                    height=350  # Set a fixed height
                )

                data['Color'] = [
                    random.choice(["#73C8A9", "#0b8793"]) for _ in range(len(data))
                ]
                bar_chart = alt.Chart(data).mark_bar().encode(
                    x=f"{x_axis}:O",  # Set X-axis to ordinal
                    y=f"{y_axis}:Q",  # Set Y-axis to quantitative
                    color=alt.Color("Color:N", scale=None, legend=None),  # Use 'Color' column for random color
                    tooltip=[x_axis, y_axis]
                ).properties(
                    title=f"{y_axis} per {x_axis}",
                    width=500,  # Set a fixed width
                    height=350  # Set a fixed height
                )

                scatter_chart = alt.Chart(data).mark_point().encode(
                    x=f"{x_axis}:O",  # Set X-axis to ordinal
                    y=f"{y_axis}:Q",  # Set Y-axis to quantitative
                    tooltip=[x_axis, y_axis]
                ).properties(
                    title=f"{y_axis} vs {x_axis}",
                    width=500,  # Set a fixed width
                    height=350  # Set a fixed height
                )

                # Display the first two charts in one row
                row1_col1, row1_col2 = st.columns(2)

                with row1_col1:
                    st.altair_chart(line_chart)

                with row1_col2:
                    st.altair_chart(bar_chart)

                # Display the third chart in the next row
                row2_col1, _ = st.columns([1, 1])  # Leave the second column empty
                with row2_col1:
                    st.altair_chart(scatter_chart)
                    st.toast("Visualization generated successfully!", icon="📊")
                    

    except Exception as e:
        logger.error(f"Error occurred during file processing: {e}")
        st.toast("Error processing file!", icon="❌")
        # Custom Error Message Styling
        st.markdown(
            f'<div class="custom-error">An error occurred: {e}</div>',
            unsafe_allow_html=True,
        )
