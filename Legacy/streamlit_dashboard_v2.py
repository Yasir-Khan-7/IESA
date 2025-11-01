# Importing the libraries
import streamlit as st
import pandas as pd
from sklearn.linear_model import LinearRegression
import numpy as np
import matplotlib.pyplot as plt

# Function to extract the starting year from various formats
def extract_start_year(year_entry):
    if isinstance(year_entry, int):
        return year_entry
    elif isinstance(year_entry, float):
        return int(year_entry)
    elif isinstance(year_entry, str):
        # Handle formats like '2002-03', '2002/03', '2002', etc.
        for delimiter in ['-', '/', ' ']:
            if delimiter in year_entry:
                try:
                    return int(year_entry.split(delimiter)[0])
                except ValueError:
                    continue
        # If no delimiter or unable to parse, try converting directly
        try:
            return int(year_entry)
        except ValueError:
            return np.nan
    else:
        return np.nan

# Title of the Dashboard
st.title("Electricity Dashboard with Linear Regression")

# File uploader to load the Excel file
uploaded_file = st.file_uploader("Upload an Excel File", type=["xlsx"])

if uploaded_file:
    try:
        # Read the Excel file
        annual_data = pd.read_excel(uploaded_file)
        
        # Ensure the columns match the expected structure
        required_columns = [
            "Year", "Installed Capacity (MW)", "Generation (GWh)",
            "Imports (GWh)", "Consumption (GWh)"
        ]
        if all(col in annual_data.columns for col in required_columns):
            # Data transformation
            annual_data["Year"] = annual_data["Year"].apply(extract_start_year)
            
            # Identify and handle rows with invalid Year entries
            invalid_years = annual_data[annual_data["Year"].isna()]
            if not invalid_years.empty:
                st.warning(f"{len(invalid_years)} rows have invalid 'Year' entries and will be skipped.")
                # Drop rows with invalid Year entries
                annual_data = annual_data.dropna(subset=["Year"])
            
            # Convert Year to integer
            annual_data["Year"] = annual_data["Year"].astype(int)
            
            # Convert other columns to numeric, handling errors
            numeric_columns = ["Installed Capacity (MW)", "Generation (GWh)", "Imports (GWh)", "Consumption (GWh)"]
            for col in numeric_columns:
                annual_data[col] = pd.to_numeric(annual_data[col], errors='coerce')
            
            # Handle NaN values in numeric columns if necessary
            # For example, fill NaN in Imports with 0
            annual_data["Imports (GWh)"] = annual_data["Imports (GWh)"].fillna(0)
            
            # Convert Installed Capacity (MW) to GWh
            annual_data["Installed_Capacity_GWh"] = (annual_data["Installed Capacity (MW)"] * 8760) / 1000
            
            # Bar chart for Generation (GWh) over the years
            st.subheader("Annual Electricity Generation (GWh)")
            st.bar_chart(annual_data.set_index("Year")["Generation (GWh)"])
            
            # Data table to display the entire dataset
            st.subheader("Electricity Data Table")
            st.dataframe(annual_data)
            
            # Linear regression prediction
            st.subheader("Linear Regression Predictions")
            category = st.selectbox(
                "Select a category to predict:",
                ["Installed_Capacity_GWh", "Generation (GWh)", "Imports (GWh)", "Consumption (GWh)"]
            )
            
            def predict_category(data, category_name):
                X = data["Year"].values.reshape(-1, 1)  # Independent variable (years)
                y = data[category_name].values  # Dependent variable (category values)
                model = LinearRegression()
                model.fit(X, y)
                # Predict for the next 6 years beyond the latest year in the data
                last_year = data["Year"].max()
                future_years = np.array([last_year + i for i in range(1, 7)]).reshape(-1, 1)
                predictions = model.predict(future_years)
                return future_years.flatten(), predictions
            
            # Perform prediction for the selected category
            years, predictions = predict_category(annual_data, category)
            
            # Display predictions in a table
            st.write(f"Predictions for {category}:")
            prediction_table = pd.DataFrame({
                "Year": years,
                "Predicted Value": predictions
            })
            st.table(prediction_table)
            
            # Plot predictions
            st.subheader("Prediction Plot")
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.plot(annual_data["Year"], annual_data[category], label="Actual Data", marker="o")
            ax.plot(years, predictions, label="Predicted Data", linestyle="--", marker="x", color="red")
            ax.set_xlabel("Year")
            ax.set_ylabel(category)
            ax.set_title(f"Actual vs Predicted {category} ({annual_data['Year'].min()}-{years[-1]})")
            ax.legend()
            st.pyplot(fig)
        else:
            st.error(f"The file does not have the required columns: {', '.join(required_columns)}")
    except Exception as e:
        st.error(f"An error occurred while processing the file: {e}")
else:
    st.warning("Please upload an Excel file to view the dashboard.")
