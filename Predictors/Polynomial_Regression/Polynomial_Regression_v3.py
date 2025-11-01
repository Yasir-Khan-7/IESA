import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
from fpdf import FPDF
import io
import tempfile

# Set up Streamlit page
st.set_page_config(page_title="IESA Dashboard with Polynomial Regression", layout="wide", page_icon="📊")

# Function to load data
def load_data(file):
    try:
        data = pd.read_excel(file)
        data.columns = data.iloc[0]  # Set the first row as column headers
        data = data.drop(0, axis=0).reset_index(drop=True)
        data.columns = ["Year", "Installed_Capacity", "Generation", "Imports", "Consumption","East","West","North","South"]
        data["Year"] = data["Year"].astype(str).str[:4].astype(int)
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
    if data[x_column].dtype == 'object':
        data[x_column] = data[x_column].apply(lambda x: int(x.split('-')[0]))  # Extract year from 'YYYY-MM'

    data[y_column] = pd.to_numeric(data[y_column], errors='coerce')
    data = data.dropna()

    X = data[[x_column]].values
    y = data[y_column].values

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    poly = PolynomialFeatures(degree=degree)
    X_train_poly = poly.fit_transform(X_train)
    X_test_poly = poly.transform(X_test)

    model = LinearRegression()
    model.fit(X_train_poly, y_train)

    y_pred = model.predict(X_test_poly)

    mse = mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)

    return model, mse, r2, X_test, y_test, y_pred, poly

# Function to generate predictions for future years
def predict_future(model, poly, start_year, end_year):
    future_years = np.array(range(start_year, end_year + 1)).reshape(-1, 1)
    future_poly = poly.transform(future_years)
    future_pred = model.predict(future_poly)
    return future_years.flatten(), future_pred

# Function to generate a PDF report
def generate_pdf(df, future_years, future_pred):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(200, 10, "IESA Energy Prediction Report", ln=True, align="C")
    pdf.ln(10)
    
    pdf.set_font("Arial", "B", 12)
    pdf.cell(200, 10, "Polynomial Regression Results", ln=True, align="L")
    pdf.ln(5)

    # Add table headers
    pdf.set_font("Arial", "B", 10)
    pdf.cell(50, 10, "Year", border=1)
    pdf.cell(50, 10, "Predicted Generation", border=1)
    pdf.ln()

    # Add future predictions
    pdf.set_font("Arial", "", 10)
    for year, pred in zip(future_years, future_pred):
        pdf.cell(50, 10, str(year), border=1)
        pdf.cell(50, 10, f"{pred:.2f}", border=1)
        pdf.ln()

    pdf.ln(10)
    
    # Generate a plot
    fig, ax = plt.subplots(figsize=(6, 3))
    ax.plot(future_years, future_pred, marker="o", linestyle="-", label="Predicted Generation")
    ax.set_xlabel("Year")
    ax.set_ylabel("Generation")
    ax.set_title("Future Energy Predictions")
    ax.legend()
    
    # Save plot to BytesIO
    img_buf = io.BytesIO()
    plt.savefig(img_buf, format="png")
    img_buf.seek(0)

    # Save image temporarily
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmpfile:
        tmpfile.write(img_buf.read())
        tmpfile_path = tmpfile.name

    # Add image to PDF
    pdf.image(tmpfile_path, x=10, y=None, w=190)

    # Save PDF
    pdf_bytes = pdf.output(dest="S").encode("latin1")
    return pdf_bytes

# Sidebar for file upload
st.sidebar.title("IESA Dashboard")
uploaded_file = st.sidebar.file_uploader("Upload Annual Electricity Data File", type=["xlsx"])

# Sidebar for polynomial degree
degree = st.sidebar.slider("Select Polynomial Degree", min_value=2, max_value=5, value=2)

if uploaded_file:
    df = load_data(uploaded_file)

    if df is not None:
        st.subheader("Transformed Data for Prediction")
        st.dataframe(df)

        # Perform Polynomial Regression
        st.subheader("Polynomial Regression")
        model, mse, r2, X_test, y_test, y_pred, poly = perform_polynomial_regression(df, "Year", "Generation", degree)

        st.write("### Regression Model Evaluation Metrics")
        st.write(f"**Mean Squared Error (MSE):** {mse:.2f}")
        st.write(f"**R² Score:** {r2:.2f}")

        # Predictions for 2019-2025
        future_years, future_pred = predict_future(model, poly, 2019, 2025)

        # Display future predictions
        st.write("### Future Predictions (2019-2025)")
        future_df = pd.DataFrame({"Year": future_years, "Predicted Generation": future_pred})
        st.table(future_df)

        # Plot predictions
        st.subheader("Prediction Chart")
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.plot(future_years, future_pred, marker="o", linestyle="-", label="Predicted Generation")
        ax.set_xlabel("Year")
        ax.set_ylabel("Generation")
        ax.set_title("Future Energy Predictions")
        ax.legend()
        st.pyplot(fig)

        # Generate and download PDF report
        pdf_data = generate_pdf(df, future_years, future_pred)
        st.download_button("📄 Download PDF Report", pdf_data, "IESA_Report.pdf", "application/pdf")

else:
    st.sidebar.info("Please upload a file to proceed.")
