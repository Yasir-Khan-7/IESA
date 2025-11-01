# Importing the libraries
import streamlit as st
import pandas as pd

# Title of the Dashboard
st.title("IESA Electricity Dashboard")

# Create tabs for two stakeholder sections
tabs = st.tabs(["Input Entry Operator", "Energy Planner"])

# Section for Input Entry Operator
with tabs[0]:
    st.header("Input Entry Operator Section")
    
    # File uploader to load the Excel file
    uploaded_file = st.file_uploader("Upload an Excel File", type=["xlsx"])
    
    if uploaded_file:
        try:
            # Read the Excel file and ensure the structure is correct
            annual_data = pd.read_excel(uploaded_file)
            
            # Save data to session state for access by other tabs
            st.session_state['annual_data'] = annual_data
            
            st.success("File uploaded successfully! Switch to the Energy Planner tab for visualizations.")
        except Exception as e:
            st.error(f"An error occurred while processing the file: {e}")
    else:
        st.info("Please upload an Excel file.")

# Section for Energy Planner
with tabs[1]:
    st.header("Energy Planner Section")
    
    if 'annual_data' in st.session_state:
        annual_data = st.session_state['annual_data']
        
        # Ensure the columns match the expected structure
        required_columns = [
            "Year", "Installed Capacity (MW)", "Generation (GWh)", 
            "Imports (GWh)", "Consumption (GWh)"
        ]
        if all(col in annual_data.columns for col in required_columns):
            # Bar chart for Generation (GWh) over the years
            st.subheader("Annual Electricity Generation (GWh)")
            st.bar_chart(annual_data.set_index("Year")["Generation (GWh)"])
            
            # Data table to display the entire dataset
            st.subheader("Electricity Data Table")
            st.dataframe(annual_data)
        else:
            st.error(f"The file does not have the required columns: {', '.join(required_columns)}")
    else:
        st.warning("No data uploaded yet. Please upload a file in the Input Entry Operator section.")
