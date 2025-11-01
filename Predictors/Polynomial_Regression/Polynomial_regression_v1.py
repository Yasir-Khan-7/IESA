import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle, Image
from reportlab.lib import colors
import streamlit as st

# Load Data
df = pd.read_excel(r"C:\Users\HP\Desktop\FYP ALGOS TEST\Linear Regression\Prediction data\Annual_Electricity_Data.xlsx")
df.columns = df.iloc[0]
df = df.drop(0, axis=0).reset_index(drop=True)
df.columns = ["Year", "Installed_Capacity", "Generation", "Imports", "Consumption","East","WEST","NORTH","SOUTH"]

# Data Transformation
df["Installed_Capacity"] = pd.to_numeric(df["Installed_Capacity"], errors="coerce")
df["Generation"] = pd.to_numeric(df["Generation"], errors="coerce")
df["Imports"] = pd.to_numeric(df["Imports"], errors="coerce").fillna(0).astype(int)
df["Consumption"] = pd.to_numeric(df["Consumption"], errors="coerce")
df["Installed_Capacity_GWh"] = (df["Installed_Capacity"] * 8760) / 1000

# Polynomial Regression Function
def predict_category(data, category_name, degree=3):
    X = data["Year"].astype(int).values.reshape(-1, 1)
    y = data[category_name].values

    poly = PolynomialFeatures(degree=degree)
    X_poly = poly.fit_transform(X)
    model = LinearRegression()
    model.fit(X_poly, y)

    future_years = np.array([2019, 2020, 2021, 2022, 2023, 2024]).reshape(-1, 1)
    future_years_poly = poly.transform(future_years)
    predictions = model.predict(future_years_poly)

    return future_years.flatten(), predictions

# Get Predictions
predicted_values = {}
for category in ["Installed_Capacity_GWh", "Generation", "Imports", "Consumption"]:
    years, predictions = predict_category(df, category, degree=3)
    predicted_values[category] = {"Years": years, "Predictions": predictions}

# Generate and Save Prediction Plot
plt.figure(figsize=(10, 6))
for category in predicted_values.keys():
    plt.plot(predicted_values[category]["Years"], predicted_values[category]["Predictions"], label=category)
plt.xlabel("Year")
plt.ylabel("Predicted Value")
plt.title("Predicted Energy Values (2019-2024)")
plt.legend()
plt.grid()
plt.savefig("prediction_plot.png")  # Save plot as an image
plt.close()

# Generate PDF Report
def generate_pdf(file_path="energy_report.pdf"):
    c = canvas.Canvas(file_path, pagesize=letter)
    width, height = letter

    # Title
    c.setFont("Helvetica-Bold", 16)
    c.drawString(200, 750, "IESA Energy Forecast Report")

    # Add Table Data
    table_data = [["Year", "Installed_Capacity (GWh)", "Generation", "Imports", "Consumption"]]
    for i in range(len(years)):
        table_data.append([
            years[i],
            round(predicted_values["Installed_Capacity_GWh"]["Predictions"][i], 2),
            round(predicted_values["Generation"]["Predictions"][i], 2),
            round(predicted_values["Imports"]["Predictions"][i], 2),
            round(predicted_values["Consumption"]["Predictions"][i], 2)
        ])

    table = Table(table_data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))

    table.wrapOn(c, width, height)
    table.drawOn(c, 50, 500)  # Adjust position

    # Add Prediction Plot
    c.drawImage("prediction_plot.png", 100, 300, width=400, height=200)

    # Save PDF
    c.showPage()
    c.save()
    return file_path

pdf_file = generate_pdf()

# Streamlit UI
st.title("IESA Energy Forecast Report")

# Show Predictions in Streamlit
st.subheader("Predicted Energy Values (2019-2024)")
df_predictions = pd.DataFrame({
    "Year": years,
    "Installed_Capacity_GWh": predicted_values["Installed_Capacity_GWh"]["Predictions"],
    "Generation": predicted_values["Generation"]["Predictions"],
    "Imports": predicted_values["Imports"]["Predictions"],
    "Consumption": predicted_values["Consumption"]["Predictions"],
})
st.dataframe(df_predictions)

# Display the Plot in Streamlit
st.subheader("Predicted Trends")
st.image("prediction_plot.png", caption="Predicted Values for 2019-2024", use_column_width=True)

# Download PDF
with open(pdf_file, "rb") as f:
    st.download_button("Download Report as PDF", f, file_name="IESA_Energy_Report.pdf", mime="application/pdf")
