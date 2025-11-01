import mysql.connector
import pandas as pd
import streamlit as st
import os
import altair as alt
import locale
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
import pyautogui
import google.generativeai as genai
from fpdf import FPDF
import matplotlib.pyplot as plt
import tempfile

st.set_page_config(page_title="IESA Dashboard", layout="wide", page_icon="📊")

genai.configure(api_key="AIzaSyAUWQ8q6xyhRLd51aueJj0VH4C7emtWKic")

# Initialize session state
if "future_data" not in st.session_state:
    st.session_state["future_data"] = None

if "charts" not in st.session_state:
    st.session_state["charts"] = []

if "metrics" not in st.session_state:
    st.session_state["metrics"] = []

if "selected_table" not in st.session_state:
    st.session_state["selected_table"] = None

def update_future_data(new_data: pd.DataFrame):
    st.session_state["future_data"] = new_data

def get_ai_recommendations(future_data: pd.DataFrame):
    if future_data is None or future_data.empty:
        return "Since no energy predictions were provided, I cannot analyze them or offer personalized recommendations. Please run a linear regression to generate predictions first."
    
    prompt = f"""
    Analyze the following energy predictions and provide insights:
    {future_data.to_string()}
    Now give me personalized recommendations based on the predictions above. 
    Keep the response concise and on point.
    """
    
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)
        return response.text if response else "No response received from the AI model."
    except Exception as e:
        return f"Error generating recommendations: {str(e)}"

def format_large_number(num):
    if num >= 1_000_000:
        return f"{locale.format_string('%d', num // 1_000_000)} million"
    elif num >= 1_000:
        return f"{locale.format_string('%d', num // 1_000)} thousand"
    return locale.format_string('%d', num)

def get_connection():
    return mysql.connector.connect(
        host="localhost",
        port="3306",
        user="root",
        passwd="admin123",
        db="iesa_db"
    )

def fetch_tables():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SHOW TABLES")
        tables = [table[0] for table in cursor.fetchall()]
        conn.close()
        return tables
    except Exception as e:
        print(f"Error fetching tables: {e}")
        return []

def fetch_table_data(table_name):
    conn = get_connection()
    cursor = conn.cursor()
    query = "SELECT * FROM {}".format(table_name)
    cursor.execute(query)
    rows = cursor.fetchall()
    data = pd.DataFrame(rows, columns=[desc[0] for desc in cursor.description])
    conn.close()
    return data

def perform_linear_regression(data, x_column, y_column):
    if data[x_column].dtype == 'object':
        data[x_column] = data[x_column].apply(lambda x: int(x.split('-')[0]))
    data[y_column] = pd.to_numeric(data[y_column], errors='coerce')

    X = data[[x_column]].values
    y = data[y_column].values
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model = LinearRegression()
    model.fit(X_train, y_train)
    
    y_pred = model.predict(X_test)
    mse = mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    
    return model, mse, r2, X_test, y_test, y_pred

def generate_pdf(predictions, recommendations):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.ln(10)

    logo_path = os.path.join(os.getcwd(), "IESA_logo.jpg")
    if os.path.exists(logo_path):
        pdf.image(logo_path, x=((pdf.w - 30) / 2), y=10, w=30, h=30)
    pdf.ln(20)
    
    pdf.set_font("Arial", "B", 16)
    pdf.cell(200, 10, "IESA Energy Prediction & Personalized Recommendations Report", ln=True, align="C")
    pdf.ln(10)

    pdf.set_font("Arial", "B", 12)
    pdf.cell(200, 10, "Future Energy Predictions", ln=True, align="L")
    pdf.ln(5)

    pdf.set_font("Arial", "B", 10)
    pdf.cell(38, 10, "Year", border=1)
    pdf.cell(38, 10, "Prediction", border=1)
    pdf.ln()

    pdf.set_font("Arial", "", 10)
    for i in range(len(predictions["Year"])):
        pdf.cell(38, 10, str(predictions["Year"][i]), border=1)
        pdf.cell(38, 10, f"{predictions['Prediction'][i]:.2f}", border=1)
        pdf.ln()

    plt.figure(figsize=(8, 6))
    plt.plot(predictions["Year"], predictions["Prediction"], marker='o', label="Prediction")
    plt.xlabel("Year")
    plt.ylabel("Value")
    plt.title("Future Energy Predictions")
    plt.legend()

    img_path = tempfile.NamedTemporaryFile(delete=False, suffix=".png").name
    plt.savefig(img_path)
    plt.close()

    pdf.ln(10)
    pdf.image(img_path, x=10, w=180)

    pdf.ln(55)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(200, 10, "Personalized Recommendations", ln=True, align="L")
    pdf.ln(5)

    pdf.set_font("Arial", "", 10)
    pdf.multi_cell(0, 10, recommendations)

    pdf_bytes = pdf.output(dest="S").encode("latin1")
    os.unlink(img_path)
    return pdf_bytes

# CSS and JavaScript
st.markdown("""
    <style>
    /* [Your existing CSS remains unchanged] */
    </style>
    <script>
    document.addEventListener('DOMContentLoaded', function () {
        const navButtons = document.querySelectorAll('.nav-links button');
        navButtons.forEach(button => {
            button.addEventListener('click', function () {
                navButtons.forEach(btn => btn.classList.remove('active'));
                this.classList.add('active');
            });
        });
    });
    </script>
""", unsafe_allow_html=True)

# Top Bar
st.markdown("""
    <div class="top-bar">
        <div class="nav-links">
            <button class="active"><a href="#home">Home</a></button>
            <button><a href="#scenarios">Scenarios</a></button>
            <button><a href="#predictions">Predictions</a></button>
            <button><a href="#report">Report</a></button>
            <button><a href="#recommendations">Recommendations</a></button>    
        </div>
    </div>
""", unsafe_allow_html=True)

# Sidebar
st.sidebar.image("images/iesa_white.svg", width=150)
st.sidebar.markdown("<h2>Data Planner Dashboard</h2>", unsafe_allow_html=True)
st.sidebar.markdown("<h3>Table and Chart Selection</h3>", unsafe_allow_html=True)

tables = fetch_tables()
selected_table = st.sidebar.selectbox("Select a table", tables)

if selected_table:
    data = fetch_table_data(selected_table)
    columns = data.columns.tolist()

    st.sidebar.markdown("### Chart Options")
    chart_type = st.sidebar.selectbox("Select Chart Type", ["Bar", "Line"])
    x_axis = st.sidebar.selectbox("Select x-axis", columns, key="chart_x_axis")
    y_axis = st.sidebar.selectbox("Select y-axis", columns, key="chart_y_axis")
    add_chart = st.sidebar.button("Add Chart", key="add_chart_button")

    st.sidebar.markdown("### Metric Options")
    metric_column = st.sidebar.selectbox("Select Column for Metric", columns, key="metric_column")
    metric_type = st.sidebar.selectbox("Select Metric Type", ["Sum", "Count", "Average", "Unique"])
    add_metric = st.sidebar.button("Add Metric", key="add_metric_button")

    reset_button = st.sidebar.button("Reset Dashboard")

    if add_chart:
        st.session_state["charts"].append((selected_table, chart_type, x_axis, y_axis))

    if add_metric:
        st.session_state["metrics"].append((selected_table, metric_column, metric_type))

    if reset_button:
        st.session_state["charts"] = []
        st.session_state["metrics"] = []
        st.session_state["selected_table"] = None

# Display Metrics
if st.session_state["metrics"]:
    metric_buttons_html = '<div class="metric-buttons">'
    for metric in st.session_state["metrics"]:
        table, column, metric_type = metric
        metric_data = fetch_table_data(table)
        if metric_type == "Sum":
            result = int(metric_data[column].sum())
            formatted_result = format_large_number(result)
            button_class = "sum-button"
            metric_label = f"{column}:"
        elif metric_type == "Count":
            result = int(metric_data[column].count())
            formatted_result = format_large_number(result)
            button_class = "count-button"
            metric_label = f"{column}:"
        elif metric_type == "Average":
            result = int(metric_data[column].mean())
            formatted_result = format_large_number(result)
            button_class = "total-button"
            metric_label = f"{column}:"
        elif metric_type == "Unique":
            result = int(metric_data[column].nunique())
            formatted_result = format_large_number(result)
            button_class = "unique-button"
            metric_label = f"{column}:"
        metric_buttons_html += f'<button class="{button_class}">{metric_label} {formatted_result}</button>'
    metric_buttons_html += '</div>'
    st.markdown(metric_buttons_html, unsafe_allow_html=True)

# Display Charts
color_schemes = ['blues', 'tealblues', 'teals', 'greens', 'browns', 'greys', 'purples', 'warmgreys', 'reds', 'oranges']
selected_color_scheme = st.sidebar.selectbox("Choose Color Scheme", color_schemes)

if st.session_state["charts"]:
    num_cols = 2
    cols = st.columns(num_cols)
    for idx, chart in enumerate(st.session_state["charts"]):
        table, chart_type, x_axis, y_axis = chart
        chart_data = fetch_table_data(table)
        chart_title = f"{table.replace('_', ' ').title()}: {x_axis} vs {y_axis}"
        with cols[idx % num_cols]:
            if chart_type == "Bar":
                chart = alt.Chart(chart_data).mark_bar().encode(
                    x=x_axis,
                    y=y_axis,
                    color=alt.Color(x_axis, scale=alt.Scale(scheme=selected_color_scheme), legend=None)
                ).properties(title=chart_title)
            elif chart_type == "Line":
                chart = alt.Chart(chart_data).mark_line().encode(
                    x=x_axis,
                    y=y_axis,
                ).properties(title=chart_title)
            st.altair_chart(chart, use_container_width=True)

# Linear Regression and Report Options
if selected_table:
    data = fetch_table_data(selected_table)
    columns = data.columns.tolist()
    st.sidebar.title("Linear Regression")

    x_column = st.sidebar.selectbox("Select X", columns)
    y_column = st.sidebar.selectbox("Select Y", columns)

    run_prediction = st.sidebar.button("Run Linear Regression")

    if run_prediction:
        if x_column and y_column:
            model, mse, r2, X_test, y_test, y_pred = perform_linear_regression(data, x_column, y_column)
            last_year = data[x_column].max()
            future_years = pd.DataFrame({x_column: range(last_year + 1, last_year + 6)})
            future_predictions = model.predict(future_years)

            future_data_local = pd.DataFrame({x_column: future_years[x_column], "Prediction": future_predictions})
            update_future_data(future_data_local)

            actual_data = alt.Chart(data).mark_line().encode(
                x=alt.X(x_column, title=x_column),
                y=alt.Y(y_column, title=y_column),
                color=alt.value('blue'),
                tooltip=[x_column, y_column]
            ).properties(
                title=f'{x_column} vs {y_column} (Actual vs Predicted)',
                width=500,
                height=350
            )

            prediction_line = alt.Chart(future_data_local).mark_line(color='red').encode(
                x=alt.X(x_column, title=x_column),
                y=alt.Y(y_column, title=y_column),
                tooltip=[x_column, y_column]
            ).properties(
                width=500,
                height=350
            )

            final_chart = actual_data + prediction_line
            col1, col2 = st.columns([1,1])
            with col1:
                st.altair_chart(final_chart, use_container_width=False)
        else:
            st.error("Please select both X and Y columns for regression.")

    personalized_recommendation = st.sidebar.button("Get Personalized Recommendation")
    report = st.sidebar.button("Print Report")
    print_custom_report = st.sidebar.button("Print Custom Report")

    if report:
        st.sidebar.expander("Report", expanded=True)
        st.markdown("""
        <style>
            [data-testid="stSidebar"] {display: none;}
        </style>
        """, unsafe_allow_html=True)
        pyautogui.hotkey('ctrl', 'p')

    if personalized_recommendation:
        response = get_ai_recommendations(st.session_state["future_data"])
        st.write(response)

    if print_custom_report:
        if st.session_state["future_data"] is not None:
            predictions = st.session_state["future_data"].rename(columns={x_column: "Year", "Prediction": "Prediction"})
            recommendations = get_ai_recommendations(st.session_state["future_data"])
            pdf_bytes = generate_pdf(predictions, recommendations)
            st.download_button(
                label="Download Custom Report",
                data=pdf_bytes,
                file_name="IESA_Energy_Report.pdf",
                mime="application/pdf"
            )
        else:
            st.error("Please run a linear regression to generate predictions before printing a custom report.")

    if st.sidebar.button("Logout", key="logout_button"):
        os.system("streamlit run iesa_login.py")

    if st.sidebar.button("Contact Us", key="contact_us_button"):
        os.system("streamlit run iesa_contact_us.py")