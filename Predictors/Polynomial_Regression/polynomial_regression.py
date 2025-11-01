import streamlit as st
import pandas as pd
import numpy as np
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score

# Set up Streamlit page
st.set_page_config(page_title="IESA Dashboard with Polynomial Regression", layout="wide", page_icon="📊")

# Function to load data
def load_data(file):
    try:
        data = pd.read_excel(file)
        data.columns = data.iloc[0]  # Set the first row as column headers
        data = data.drop(0, axis=0).reset_index(drop=True)
        data.columns = ["Year", "Installed_Capacity", "Generation", "Imports", "Consumption","East","WEST","NORTH","SOUTH"]
        # data["Year"] = data["Year"].str[:4].astype(int)
        data["Installed_Capacity"] = pd.to_numeric(data["Installed_Capacity"], errors="coerce")
        data["Generation"] = pd.to_numeric(data["Generation"], errors="coerce")
        data["Imports"] = pd.to_numeric(data["Imports"], errors="coerce").fillna(0).astype(int)
        data["Consumption"] = pd.to_numeric(data["Consumption"], errors="coerce")
        data["Installed_Capacity_GWh"] = (data["Installed_Capacity"] * 8760) / 1000
        return data
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None

# Function to perform polynomial regression
def perform_polynomial_regression(data, x_column, y_column, degree=2):
    if data[x_column].dtype == 'object':  # Check if x_column is a string
        data[x_column] = data[x_column].apply(lambda x: int(x.split('-')[0]))  # Extract year from 'YYYY-MM'

    # Convert y_column to numeric
    data[y_column] = pd.to_numeric(data[y_column], errors='coerce')
    data = data.dropna()  # Drop rows with NaN values

    X = data[[x_column]].values
    y = data[y_column].values

    # Split data into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Transform input features to polynomial terms
    poly = PolynomialFeatures(degree=degree)
    X_train_poly = poly.fit_transform(X_train)
    X_test_poly = poly.transform(X_test)

    # Train the model
    model = LinearRegression()
    model.fit(X_train_poly, y_train)

    # Predictions
    y_pred = model.predict(X_test_poly)

    # Evaluate model performance
    mse = mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)

    return model, mse, r2, X_test, y_test, y_pred, poly

# Sidebar for file upload
st.sidebar.title("IESA Dashboard")
uploaded_file = st.sidebar.file_uploader("Upload Annual Electricity Data File", type=["xlsx"])

# Sidebar for polynomial degree
degree = st.sidebar.slider("Select Polynomial Degree", min_value=2, max_value=5, value=2)

if uploaded_file:
    # Load data
    df = load_data(uploaded_file)

    if df is not None:
        st.subheader("Transformed Data for Prediction")
        st.dataframe(df)

        # Perform Polynomial Regression
        st.subheader("Polynomial Regression")
        model, mse, r2, X_test, y_test, y_pred, poly = perform_polynomial_regression(df, "Year", "Generation", degree)

        # Display metrics
        st.write("### Regression Model Evaluation Metrics")
        st.write(f"**Mean Squared Error (MSE):** {mse:.2f}")
        st.write(f"**R² Score:** {r2:.2f}")

        # Display actual vs predicted values
        st.write("### Actual vs Predicted Values")
        results = pd.DataFrame({
            "Year": X_test.flatten(),
            "Actual": y_test,
            "Predicted": y_pred
        }).sort_values(by="Year")
        st.table(results)

        # Plot predictions
        st.subheader("Prediction Chart")
        st.line_chart(results.set_index("Year"))

        # Polynomial equation (optional)
        coefficients = model.coef_
        intercept = model.intercept_
        st.write("### Polynomial Equation")
        equation = f"{intercept:.2f}"
        for i, coef in enumerate(coefficients[1:], start=1):
            equation += f" + ({coef:.2f} * x^{i})"
        st.write(f"**y = {equation}**")
else:
    st.sidebar.info("Please upload a file to proceed.")
