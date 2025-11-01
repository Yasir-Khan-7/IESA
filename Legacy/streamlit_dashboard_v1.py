# importing the libraries
import streamlit as st
import pandas as pd

# Title of the Dashboard
st.title("Electricity Dashboard")

# File uploader to load the Excel file
uploaded_file = st.file_uploader("Upload an Excel File", type=["xlsx"])

if uploaded_file:
    try:
        # Read the Excel file and assume the correct sheet structure
        annual_data = pd.read_excel(uploaded_file)

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
    except Exception as e:
        st.error(f"An error occurred while processing the file: {e}")
else:
    st.warning("Please upload an Excel file to view the dashboard.")
