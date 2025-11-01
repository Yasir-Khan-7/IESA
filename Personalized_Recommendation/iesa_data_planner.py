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
st.set_page_config(page_title="IESA Dashboard", layout="wide", page_icon="📊")

genai.configure(api_key="AIzaSyAUWQ8q6xyhRLd51aueJj0VH4C7emtWKic")

# init future_data
if "future_data" not in st.session_state:
    st.session_state["future_data"] = None

def update_future_data(new_data: pd.DataFrame):
    st.session_state["future_data"] = new_data  # Update session state of future_data

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

# Function to format large numbers
def format_large_number(num):
    if num >= 1_000_000:
        return f"{locale.format_string('%d', num // 1_000_000)} million"
    elif num >= 1_000:
        return f"{locale.format_string('%d', num // 1_000)} thousand"
    return locale.format_string('%d', num)
# Connection
def get_connection():
    return mysql.connector.connect(
        host="localhost",
        port="3306",
        user="root",
        passwd="admin123",
        db="iesa_db"
    )

# Function to fetch tables from the database
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

# Function to fetch data from a specific table
def fetch_table_data(table_name):
    conn = get_connection()
    cursor = conn.cursor()
    query = "SELECT * FROM {}".format(table_name)  # Still a risk
    cursor.execute(query)
    rows = cursor.fetchall()
    data = pd.DataFrame(rows, columns=[desc[0] for desc in cursor.description])
    conn.close()
    return data

# Linear regression function
def perform_linear_regression(data, x_column, y_column):
    if data[x_column].dtype == 'object':  # check if it's a string column
        data[x_column] = data[x_column].apply(lambda x: int(x.split('-')[0]))  # Extract year from 'YYYY-MM by usng lambda function

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
    
    # Performance metrics to compare test data with predicted dataa
    mse = mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    
    return model, mse, r2, X_test, y_test, y_pred

# Local image path (Replace with your actual image path)
image_path = "images/iesa_white.svg"

# CSS and JavaScript for dynamic button states
st.markdown("""
    <style>
    /* General Styling */
    header {
        border-bottom: 3px solid  #136a8a !important; 
    }
    [data-testid="stSidebar"] {
        background: linear-gradient(135deg, #73C8A9, #0b8793); /* Gradient background */
        color: white;
        margin-top:58px;
    }
    .sidebar-content {
        margin-top: -60px;
        padding: 20px;
    }
    .logo-title-container {
        display: flex;
        flex-direction: row;
        align-items: center;
        justify-content: space-between;
    }
    .logo img {
        width: 60px;
        border-radius: 50%;
    }
    .app-name {
        font-size: 1.5em;
        font-weight: bold;
    }
    .top-bar {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-top: -10px;
    }
    .nav-links > button {
        background-color: transparent;
        border: none;
        font-size: 1em;
        font-weight: 500;
        cursor: pointer;
        margin: 0 5px;
        border-bottom: 2px solid transparent;
        transition: all 0.3s ease;
        color: white; /* Anchor text color */
    }
    .nav-links > button.active {
        border-bottom: 2px solid red; /* Persistent red border for active button */
    }
    .nav-links > button:hover {
        border-bottom: 2px solid green; /* Green border on hover */
    }

    .stButton button {
        width:100%;
        background-color: #0b8793;
        color: white !important;
        border: 1px solid #4AC29A;
        border-radius: 5px;
        font-size: 0.9em;
        font-weight: bold;
        padding: 6px 20px;
        cursor: pointer;
        transition: all 0.3s ease;
    }

    .stButton button:hover {
        background-color: #0b8793;
        color: white !important;
    }
    a{
        text-decoration: none;
        color: #0F403F !important;
    }
    a:hover{
        color: #0F403F !important;
        text-decoration: none;
    }
    

    /* Metric Buttons */
    .metric-buttons {
        display: flex;
        justify-content:space-between;  /* Centers buttons horizontally */
      
  
        flex-wrap: wrap;  /* Ensures buttons wrap on smaller screens */
        margin-top: 20px;  /* Add some spacing from other elements */
    }

    .sum-button, .count-button, .total-button, .unique-button {
        padding: 8px 15px;  /* Reduced padding */
        border-radius: 12px;  /* Slightly smaller border radius */
        text-align: center;
        margin: 5px;
        color: white;
        font-weight: bold;
        cursor: pointer;
        transition: all 0.3s ease;
        box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);
        border: none;
        width: 120px;  /* Set a fixed width for each button */
        font-size: 0.85em;  /* Reduced font size */
    }

    /* Greenish Gradient (matching sidebar) */
    .sum-button { 
        background: linear-gradient(135deg, #73C8A9, #0b8793);  /* Sidebar-like greenish tones */
    }

    /* Redish Gradient (lighter tones) */
    .count-button { 
        background: linear-gradient(135deg, #FF6F61, #DE4313);  /* Lighter red gradient */
    }

    /* Blueish Gradient (lighter tones) */
    .total-button { 
        background: linear-gradient(135deg, #56CCF2, #2F80ED);  /* Lighter blue gradient */
    }

    /* Soft Greenish Gradient for Unique Button */
    .unique-button { 
        background: linear-gradient(135deg, #A5D6A7, #66BB6A);  /* Soft green gradient */
    }

    /* Hover effects */
    .sum-button:hover, .count-button:hover, .total-button:hover, .unique-button:hover {
        transform: translateY(-5px);
        box-shadow: 0px 8px 15px rgba(0, 0, 0, 0.2);
    }
    .marks{
        border-radius: 15px; /* Rounded corners for the SVG canvas */
        border: 1px solid  #0b8793; /* Greenish border */
         box-shadow: 0px 8px 15px rgba(0, 0, 0, 0.2);
        margin-top: 20px; /* Add some spacing from the buttons */
        padding: 10px; /* Add padding inside the canvas */
        width: 99%; /* Full width */
    }
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

# Top Bar Content
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

# Initialize session state
if "charts" not in st.session_state:
    st.session_state["charts"] = []

if "metrics" not in st.session_state:
    st.session_state["metrics"] = []

if "selected_table" not in st.session_state:
    st.session_state["selected_table"] = None


# Sidebar for table selection
st.sidebar.image(image_path,width=150)
# st.sidebar.title("IESA Data Planner Dashboard")
st.sidebar.markdown("""
    <h2>Data Planner Dashboard</h2>
""",unsafe_allow_html=True)
st.sidebar.markdown("""
    <h3>Table and Chart Selection</h3>
""",unsafe_allow_html=True)
# st.sidebar.title("Table and Chart Selection")

# Fetch tables and display table selection
tables = fetch_tables()
selected_table = st.sidebar.selectbox("Select a table", tables)

# Initialize session state for charts and metrics if not already done
if 'charts' not in st.session_state:
    st.session_state['charts'] = []  # Store charts from all tables
if 'metrics' not in st.session_state:
    st.session_state['metrics'] = []  # Store metrics from all tables

# Fetch data for the selected table
if selected_table:
    data = fetch_table_data(selected_table)
    columns = data.columns.tolist()

    # Chart selection
    st.sidebar.markdown("### Chart Options")
    chart_type = st.sidebar.selectbox("Select Chart Type", ["Bar", "Line"])
    x_axis = st.sidebar.selectbox("Select x-axis", columns, key="chart_x_axis")
    y_axis = st.sidebar.selectbox("Select y-axis", columns, key="chart_y_axis")
    add_chart = st.sidebar.button("Add Chart", key="add_chart_button")

    # Metric selection
    st.sidebar.markdown("### Metric Options")
    metric_column = st.sidebar.selectbox("Select Column for Metric", columns, key="metric_column")
    metric_type = st.sidebar.selectbox("Select Metric Type", ["Sum", "Count", "Average", "Unique"])
    add_metric = st.sidebar.button("Add Metric", key="add_metric_button")

    reset_button = st.sidebar.button("Reset Dashboard")
    
    # Add charts to session state (retain charts from all tables)
    if add_chart:
        st.session_state["charts"].append((selected_table, chart_type, x_axis, y_axis))

    # Add metrics to session state (retain metrics from all tables)
    if add_metric:
        st.session_state["metrics"].append((selected_table, metric_column, metric_type))

    # Reset button functionality
    if reset_button:
        # Reset session state
        st.session_state["charts"] = []
        st.session_state["metrics"] = []
        st.session_state["selected_table"] = None

# Display metrics dynamically from all selected tables
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


# List of color schemes
color_schemes = ['blues', 'tealblues', 'teals', 'greens', 'browns', 'greys', 'purples', 'warmgreys', 'reds', 'oranges']

# Assuming chart_data, chart_type, x_axis, y_axis, chart_title, and num_cols are already defined

# Dropdown to select the color scheme
selected_color_scheme = st.sidebar.selectbox("Choose Color Scheme", color_schemes)
# Display charts dynamically from all selected tables
if st.session_state["charts"]:
    num_cols = 2  # Adjust number of columns if needed
    cols = st.columns(num_cols)

    for idx, chart in enumerate(st.session_state["charts"]):
        table, chart_type, x_axis, y_axis = chart
        chart_data = fetch_table_data(table)  # Fetch data for the associated table

        chart_title = f"{table.replace('_', ' ').title()}: {x_axis} vs {y_axis}"
        
        with cols[idx % num_cols]:
            if chart_type == "Bar":
                chart = alt.Chart(chart_data).mark_bar().encode(
                    x=x_axis,
                    y=y_axis,
                    color=alt.Color(x_axis, scale=alt.Scale(scheme=selected_color_scheme), legend=None)  # Apply selected color scheme
                    ).properties(title=chart_title)
            elif chart_type == "Line":
                chart = alt.Chart(chart_data).mark_line().encode(
                    x=x_axis,
                    y=y_axis,
                    ).properties(title=chart_title)

            st.altair_chart(chart, use_container_width=True)

# Streamlit interaction
if selected_table:
    data = fetch_table_data(selected_table)
    columns = data.columns.tolist()
    st.sidebar.title("Linear Regression")

    x_column = st.sidebar.selectbox("Select X", columns)
    y_column = st.sidebar.selectbox("Select Y", columns)

    run_prediction = st.sidebar.button("Run Linear Regression")

    if run_prediction:
        if x_column and y_column:
            # Perform linear regression after traning the model
            model, mse, r2, X_test, y_test, y_pred = perform_linear_regression(data, x_column, y_column)
            # Predict for the next 5 years from current data's last year
            last_year = data[x_column].max()
            future_years = pd.DataFrame({x_column: range(last_year + 1, last_year + 6)})
            future_predictions = model.predict(future_years)

            # Create a dataframe for future predictions by setting years on x axis and predicted values on y axis
            future_data_local = pd.DataFrame({x_column: future_years[x_column], y_column: future_predictions})
            update_future_data(future_data_local)

            # Create line chart for actual data and predicted data
            actual_data = alt.Chart(data).mark_line().encode(
                x=alt.X(x_column, title=x_column),
                y=alt.Y(y_column, title=y_column),
                color=alt.value('blue'),
                tooltip=[x_column, y_column]
            ).properties(
                title=f'{x_column} vs {y_column} (Actual vs Predicted)',
                 width=500,  # Set chart width to 400
                height=350  # Set chart height to 250
            )

            prediction_line = alt.Chart(future_data_local).mark_line(color='red').encode(
                x=alt.X(x_column, title=x_column),
                y=alt.Y(y_column, title=y_column),
                tooltip=[x_column, y_column]
            ).properties(
                 width=500,  # Set chart width to 400
                height=350  # Set chart height to 250
            )

            # Combine actual data and future prediction line
            final_chart = actual_data + prediction_line

            col1, col2,  = st.columns([1,1])  # Adjust the proportions as needed
            with col1:
                st.altair_chart(final_chart, use_container_width=False) # Set to False to use the full width of the screen

        else:
            st.error("Please select both X and Y columns for regression.")
            
    persoanlized_recommendation = st.sidebar.button("Get Personalized Recommendation")
    report = st.sidebar.button("Print Report")
    if report:
        st.sidebar.expander("Report", expanded=True)
        st.markdown("""
        <style>
            [data-testid="stSidebar"] {display: none;}
        </style>
    """, unsafe_allow_html=True)
        hide_elements_script = """
    <style>
        @media print {
            .stApp { background: white; } /* Optional: remove dark mode */
            .stSidebar { display: none; } /* Hide sidebar */
        }
    </style>
"""
        # st.markdown(hide_elements_script, unsafe_allow_html=True)  # Hide sidebar
        pyautogui.hotkey('ctrl', 'p')

    if(persoanlized_recommendation):
        response = get_ai_recommendations(st.session_state["future_data"])
        st.write(response)

    if st.sidebar.button("Logout", key="logout_button"):
        os.system("streamlit run iesa_login.py")

    if st.sidebar.button("Contact Us", key="contact_us_button"):
        os.system("streamlit run iesa_contact_us.py")