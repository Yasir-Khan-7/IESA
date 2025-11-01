import streamlit as st
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression

st.set_page_config(page_title="IESA Dashboard", layout="wide", page_icon="📊")

# Function to load data
def load_data(file):
    try:
        data = pd.read_excel(file)
        data.columns = data.iloc[0]  # Set the first row as column headers
        data = data.drop(0, axis=0).reset_index(drop=True)
        data.columns = ["Year", "Installed_Capacity", "Generation", "Imports", "Consumption"]
        data["Year"] = data["Year"].str[:4].astype(int)
        data["Installed_Capacity"] = pd.to_numeric(data["Installed_Capacity"], errors="coerce")
        data["Generation"] = pd.to_numeric(data["Generation"], errors="coerce")
        data["Imports"] = pd.to_numeric(data["Imports"], errors="coerce").fillna(0).astype(int)
        data["Consumption"] = pd.to_numeric(data["Consumption"], errors="coerce")
        data["Installed_Capacity_GWh"] = (data["Installed_Capacity"] * 8760) / 1000
        return data
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None

# Prediction function
def predict_category(data, category_name):
    X = data["Year"].values.reshape(-1, 1)  # Independent variable (years)
    y = data[category_name].values  # Dependent variable (category values)
    model = LinearRegression()
    model.fit(X, y)
    future_years = np.array([2019, 2020, 2021, 2022, 2023, 2024]).reshape(-1, 1)
    predictions = model.predict(future_years)
    return future_years.flatten(), predictions
st.markdown(
    """
    <style>
        /* Change the background color of the sidebar */
        [data-testid="stSidebar"] {
            background: linear-gradient(135deg, #73C8A9, #0b8793); /* Gradient background */
            color: white;
            margin-top:58px;
        }

        /* Change the font color of the sidebar text */
        [data-testid="stSidebar"] * {
            color: white; /* Sidebar text color */
        }

        /* Customize the file uploader text color */
        [data-testid="stSidebar"] .stFileUploader {
            color: white !important;
        }

        /* Customize the scrollbar color */
        [data-testid="stSidebar"] ::-webkit-scrollbar {
            width: 8px;
        }

        [data-testid="stSidebar"] ::-webkit-scrollbar-thumb {
            background-color: #1B4F72; /* Scrollbar thumb color */
        }

        [data-testid="stSidebar"] ::-webkit-scrollbar-thumb:hover {
            background-color: #154360; /* Hover effect for scrollbar thumb */
        }
    </style>
    """,
       unsafe_allow_html=True
)
# Sidebar Content
st.sidebar.title("IESA Dashboard")
uploaded_file = st.sidebar.file_uploader("Upload Annual Electricity Data File", type=["xlsx"])

if uploaded_file:
    # Load data
    df = load_data(uploaded_file)
    
    if df is not None:
        st.subheader("Transformed Data for Prediction")
        st.dataframe(df)

        # Predictions
        st.subheader("Predicted Values (2019-2024)")
        prediction_data = {"Year": [2019, 2020, 2021, 2022, 2023, 2024]}
        for category in ["Installed_Capacity_GWh", "Generation", "Imports", "Consumption"]:
            years, predictions = predict_category(df, category)
            prediction_data[category] = predictions

        # Create a DataFrame for predictions
        prediction_df = pd.DataFrame(prediction_data)

        # Display prediction table
        st.write("### Prediction Table")
        st.table(prediction_df)

        # Plot predictions using Streamlit Charts
        st.subheader("Prediction Charts")
        for category in ["Installed_Capacity_GWh", "Generation", "Imports", "Consumption"]:
            st.write(f"**{category}**")
            
            # Combine years and predictions into a DataFrame
            category_df = prediction_df[["Year", category]].rename(columns={category: "Prediction"})
            
            # Line Chart
            st.line_chart(category_df.set_index("Year"))
            
            # Bar Chart
            st.bar_chart(category_df.set_index("Year"))
