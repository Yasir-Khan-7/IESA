import streamlit as st
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score

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

# Function to perform linear regression
def perform_linear_regression(data, x_column, y_column):
    if data[x_column].dtype == 'object':
        data[x_column] = data[x_column].apply(lambda x: int(x.split('-')[0]))  # Extract year

    # Convert y_column to numeric
    data[y_column] = pd.to_numeric(data[y_column], errors='coerce')

    X = data[[x_column]].values
    y = data[y_column].values

    # Split data into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Create and train the model
    model = LinearRegression()
    model.fit(X_train, y_train)

    # Predictions
    y_pred = model.predict(X_test)

    # Performance metrics
    mse = mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)

    return model, mse, r2, X_train, y_train, X_test, y_test, y_pred

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
        [data-testid="stSidebar"] {
            background: linear-gradient(135deg, #73C8A9, #0b8793);
            color: white;
            margin-top:58px;
        }
        [data-testid="stSidebar"] * {
            color: white;
        }
        [data-testid="stSidebar"] .stFileUploader {
            color: white !important;
        }
        [data-testid="stSidebar"] ::-webkit-scrollbar {
            width: 8px;
        }
        [data-testid="stSidebar"] ::-webkit-scrollbar-thumb {
            background-color: #1B4F72;
        }
        [data-testid="stSidebar"] ::-webkit-scrollbar-thumb:hover {
            background-color: #154360;
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

        # Linear Regression Analysis
        st.subheader("Linear Regression Analysis")
        for category in ["Installed_Capacity_GWh", "Generation", "Imports", "Consumption"]:
            model, mse, r2, X_train, y_train, X_test, y_test, y_pred = perform_linear_regression(df, "Year", category)

            st.write(f"### {category}")
            st.write(f"Mean Squared Error (MSE): {mse:.2f}")
            st.write(f"R² Score: {r2:.2f}")

            # Plot Train vs Test Data
            train_df = pd.DataFrame({"Year": X_train.flatten(), "Actual": y_train})
            test_df = pd.DataFrame({"Year": X_test.flatten(), "Actual": y_test, "Predicted": y_pred})

            st.write("#### Training Data")
            st.dataframe(train_df)

            st.write("#### Test Data")
            st.dataframe(test_df)

            st.write("#### Test Data Prediction vs Actual")
            st.line_chart(test_df.set_index("Year"))
