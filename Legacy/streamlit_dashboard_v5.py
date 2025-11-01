import streamlit as st
import pandas as pd
import plotly.express as px
import base64

# Set page configuration
st.set_page_config(page_title="IESA Dashboard", layout="wide", page_icon="🔌")
st.markdown("""
    <style>
    /* Sidebar Styling */
    [data-testid="stSidebar"] {
         background: linear-gradient(135deg, #2980b9, #2c3e50);
        
        color: #FFFFFF; /* White text */
    }

    /* Main App Background */
    .stApp {
        background-color: #F7F9FB; /* Very light gray */
    }
    header{
         background-color: #64b3f4 !important;
    }
    /* Sidebar Typography */
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3, [data-testid="stSidebar"] label {
        color: #FFFFFF; /* White for sidebar titles and labels */
    }

    /* Vibrant Card Styling */
    .card {
        padding: 8px;
        border-radius: 15px;
        text-align: center;
        margin: 5px;
        box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1); /* Soft shadow */
        color: white; /* White text for better contrast */
    }

    .card:nth-child(1) {
        background: linear-gradient(135deg, #4B79A1, #283E51);
        
    } /* Vibrant blue */
  
    </style>
""", unsafe_allow_html=True)
def image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        encoded_image = base64.b64encode(image_file.read()).decode()
    return f"data:image/jpeg;base64,{encoded_image}"

# Local image path (Replace with the local path of your image)
image_path = "IESA_logo.png"  # Replace with your local image path

# Convert image to base64 string
image_base64 = image_to_base64(image_path)
# Sidebar for data type selection and file upload
with st.sidebar:
    st.image(image_path)  # Replace with your logo
    st.title("IESA Dashboard")
    st.subheader("Input Data Type")
    input_type = st.selectbox("Select Data Type", ["Energy Data", "Gas Data", "Electricity Data"])

    uploaded_file = None
    if input_type:
        uploaded_file = st.file_uploader(f"Upload {input_type} File", type=["xlsx"])

    if uploaded_file:
        try:
            data = pd.read_excel(uploaded_file)
            numeric_columns = [col for col in data.columns if pd.api.types.is_numeric_dtype(data[col])]

            st.subheader("Select Data Basis")
            basis_selection = st.selectbox(
                "Choose how to display data:",
                options=numeric_columns,
                index=0 if numeric_columns else None,
            )
        except Exception as e:
            st.error(f"An error occurred: {e}")

# Layout for top aggregation cards and filter options
if uploaded_file:
    try:
        data = pd.read_excel(uploaded_file)

        # Define columns for cards
        card_cols = st.columns(5)
        with card_cols[0]:
            st.markdown('<div class="card">Sum<br><strong>{}</strong></div>'.format(data.select_dtypes('number').sum().sum()), unsafe_allow_html=True)
        with card_cols[1]:
            st.markdown('<div class="card">Count<br><strong>{}</strong></div>'.format(data.shape[0]), unsafe_allow_html=True)
        with card_cols[2]:
            st.markdown('<div class="card">Total<br><strong>{}</strong></div>'.format(data.select_dtypes('number').sum().sum()), unsafe_allow_html=True)
        with card_cols[3]:
            st.markdown('<div class="card">Unique<br><strong>{}</strong></div>'.format(data.nunique().sum()), unsafe_allow_html=True)
        with card_cols[4]:
            if "Year" in data.columns:
                year_options = ["All"] + sorted(data["Year"].unique())
                year_filter = st.multiselect("Select Year(s)", options=year_options, default="All")
                if "All" in year_filter or not year_filter:
                    filtered_data = data
                else:
                    filtered_data = data[data["Year"].isin(year_filter)]
            else:
                st.warning("No 'Year' column found in the uploaded data.")
                filtered_data = data
    except Exception as e:
        st.error(f"An error occurred: {e}")

# Main Chart Section
if uploaded_file:
    try:
        if filtered_data is not None:
            cols = st.columns(2)

            # Bar chart
            with cols[0]:
                if "Year" in filtered_data.columns and basis_selection:
                    bar_chart = px.bar(
                        filtered_data,
                        x="Year",
                        y=basis_selection,
                        color_discrete_sequence=px.colors.qualitative.Set2  # Multi-color palette
                    )
                    st.plotly_chart(bar_chart, use_container_width=True)

            # Line chart
            with cols[1]:
                if "Year" in filtered_data.columns and basis_selection:
                    line_chart = px.line(
                        filtered_data,
                        x="Year",
                        y=basis_selection,
                        color_discrete_sequence=px.colors.qualitative.Set1,  # Multi-color palette
                        markers=True
                    )
                    st.plotly_chart(line_chart, use_container_width=True)
    except Exception as e:
        st.error(f"An error occurred in visualization: {e}")
