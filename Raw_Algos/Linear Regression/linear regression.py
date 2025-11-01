import pandas as pd
from sklearn.linear_model import LinearRegression
import numpy as np
import matplotlib.pyplot as plt

# Load data
df = pd.read_excel(r"C:\Users\HP\Desktop\WisRule\Linear Regression\Prediction data\Annual_Electricity_Data.xlsx")
df.columns = df.iloc[0]  # Set the first row as column headers
df = df.drop(0, axis=0).reset_index(drop=True)  # Drop the header row

# Rename columns
df.columns = ["Year", "Installed_Capacity", "Generation", "Imports", "Consumption"]

# Data transformation
df["Year"] = df["Year"].str[:4].astype(int)  # Extract year as integer
df["Installed_Capacity"] = pd.to_numeric(df["Installed_Capacity"], errors="coerce")
df["Generation"] = pd.to_numeric(df["Generation"], errors="coerce")
df["Imports"] = pd.to_numeric(df["Imports"], errors="coerce").fillna(0).astype(int)
df["Consumption"] = pd.to_numeric(df["Consumption"], errors="coerce")

# Convert Installed Capacity (MW) to GWh
df["Installed_Capacity_GWh"] = (df["Installed_Capacity"] * 8760) / 1000

print("Transformed Data:")
print(df)

# Prediction function
def predict_category(data, category_name):
    X = data["Year"].values.reshape(-1, 1)  # Independent variable (years)
    y = data[category_name].values  # Dependent variable (category values)
    model = LinearRegression()
    model.fit(X, y)
    future_years = np.array([2019, 2020, 2021, 2022, 2023, 2024]).reshape(-1, 1)
    predictions = model.predict(future_years)

    return future_years.flatten(), predictions

# Predictions for all categories
predicted_values = {}
for category in ["Installed_Capacity_GWh", "Generation", "Imports", "Consumption"]:
    years, predictions = predict_category(df, category)
    predicted_values[category] = {"Years": years, "Predictions": predictions}

# Display predictions
for category, values in predicted_values.items():
    print(f"\nCategory: {category}")
    for year, prediction in zip(values["Years"], values["Predictions"]):
        print(f"Year {year}: Predicted Value = {prediction:.2f}")

# Plot predictions
plt.figure(figsize=(10, 8))
for category in predicted_values.keys():
    years = predicted_values[category]["Years"]
    predictions = predicted_values[category]["Predictions"]
    plt.plot(years, predictions, label=category)
plt.xlabel("Year")
plt.ylabel("Predicted Value")
plt.title("Predicted Values for Each Category (2019-2024)")
plt.legend()
plt.show()
