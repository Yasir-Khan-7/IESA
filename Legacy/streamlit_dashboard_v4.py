import streamlit as st
import pandas as pd

# Set page configuration
st.set_page_config(page_title="IESA Dashboard", layout="wide", page_icon="🔌")

# Apply custom CSS for dark sidebar
st.markdown("""
    <style>
    .sidebar .sidebar-content {
        background-color: #001f3f; /* Dark blue */
        color: white;
    }
    .block-container {
        background-color: white; /* White for main content */
        color: black;
    }
    .stButton>button {
        background-color: #007acc;
        color: white;
        border: none;
        border-radius: 5px;
    }
    .stButton>button:hover {
        background-color: #005f99;
        color: white;
    }
    </style>
""", unsafe_allow_html=True)

# Sidebar for inputs
with st.sidebar:
    st.image("https://via.placeholder.com/300x100?text=IESA+Logo", use_column_width=True)  # Replace with your logo
    st.title("IESA Dashboard")
    
    st.subheader("Input Entry Operator")
    input_type = st.selectbox("Select Input Type", ["Energy Data", "Gas Data", "Electricity Data"])

    uploaded_file = st.file_uploader(f"Upload {input_type} File", type=["xlsx"])

    # Upload message
    if uploaded_file:
        st.success(f"{input_type} file uploaded successfully!")

# Top tabs
tabs = st.tabs(["Summary", "Trends", "Settings"])
with tabs[0]:
    st.header("Summary")
    if uploaded_file:
        try:
            # Read uploaded file
            data = pd.read_excel(uploaded_file)
            required_columns = ["Year", "Generation (GWh)"]  # Example structure

            # Check if required columns exist
            if all(col in data.columns for col in required_columns):
                st.subheader(f"{input_type} Overview")
                st.write("This tab summarizes the data.")
                st.dataframe(data)  # Display the dataset
            else:
                st.error(f"The file must have the columns: {', '.join(required_columns)}")
        except Exception as e:
            st.error(f"An error occurred: {e}")
    else:
        st.info("Upload a file to see the summary.")

with tabs[1]:
    st.header("Trends")
    if uploaded_file:
        try:
            # Read uploaded file
            data = pd.read_excel(uploaded_file)
            required_columns = ["Year", "Generation (GWh)"]  # Example structure

            # Check if required columns exist
            if all(col in data.columns for col in required_columns):
                st.subheader(f"{input_type} Trends")
                st.bar_chart(data.set_index("Year")["Generation (GWh)"])  # Bar chart for trends
            else:
                st.error(f"The file must have the columns: {', '.join(required_columns)}")
        except Exception as e:
            st.error(f"An error occurred: {e}")
    else:
        st.info("Upload a file to view trends.")

with tabs[2]:
    st.header("Settings")
    st.write("Configure application settings here.")
