import streamlit as st
import pandas as pd
import mysql.connector
import groq
import json
import os
from smolagents import Tool

st.set_page_config(page_title="IESA Scenario Analysis", layout="wide")

SCENARIO_FILE = "scenarios.json"

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
        st.error(f"Error fetching tables: {e}")
        return []

def fetch_table_data(table_name):
    """Fetches table data and converts it to a readable string format."""
    conn = get_connection()
    cursor = conn.cursor()
    query = f"SELECT * FROM {table_name}"
    cursor.execute(query)
    rows = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]
    conn.close()

    if not rows:
        return None  # Return None if the table is empty

    data = pd.DataFrame(rows, columns=columns)
    data_string = data.to_string(index=False)[:4000]  # Convert data to string (limit 4000 chars)
    
    return data_string

def load_scenarios():
    if os.path.exists(SCENARIO_FILE):
        with open(SCENARIO_FILE, "r") as f:
            return json.load(f)
    return {}

def save_scenario(table_name, scenario):
    scenarios = load_scenarios()
    scenarios[table_name] = scenario
    with open(SCENARIO_FILE, "w") as f:
        json.dump(scenarios, f, indent=4)

def get_scenario(table_name):
    scenarios = load_scenarios()
    return scenarios.get(table_name, None)

# client = groq.Client(api_key="YOUR_GROQ_API_KEY_HERE")

class ScenarioGeneratorTool(Tool):
    name = "scenario_generator"
    description = "Generates a scenario summary based on dataset trends."
    inputs = {"table_name": {"type": "string", "description": "Database table name."}}
    output_type = "string"

    def forward(self, table_name: str):
        data_string = fetch_table_data(table_name)
        if data_string is None:
            return "No data available in this table. Unable to generate a scenario."

        prompt = (f"Analyze the following dataset and generate a scenario title based only on this data:\n\n"
                  f"{data_string}\n\n"
                  "Ensure the title reflects actual data trends without introducing external knowledge.")

        response = client.chat.completions.create(
            model="qwen-2.5-32b",
            messages=[{"role": "user", "content": prompt}]
        )

        scenario = response.choices[0].message.content.strip()
        save_scenario(table_name, scenario)
        return scenario

class ScenarioAnalysisTool(Tool):
    name = "scenario_analysis"
    description = "Analyzes a generated scenario and provides structured insights."
    inputs = {"table_name": {"type": "string", "description": "Database table name."}, "scenario": {"type": "string", "description": "Generated scenario title."}}
    output_type = "string"

    def forward(self, table_name: str, scenario: str):
        data_string = fetch_table_data(table_name)
        if data_string is None:
            return "No data available in this table. Unable to analyze the scenario."

        prompt = (f"Analyze the following dataset based on actual trends:\n\n"
                  f"{data_string}\n\n"
                  f"Scenario: {scenario}\n\n"
                  "**Overall Trends**\n"
                  "- Identify key trends from the data.\n"
                  "- Provide only insights based on available data.\n"
                  "- Avoid introducing external information.\n\n"
                  "**Key Insights**\n"
                  "- Summarize major findings based only on this dataset.")

        response = client.chat.completions.create(
            model="qwen-2.5-32b",
            messages=[{"role": "user", "content": prompt}]
        )
        
        return response.choices[0].message.content.strip()


st.markdown("""
    <style>
    /* General Styling */
    header {
        border-bottom: 3px solid  #136a8a !important; 
    }
    [data-testid="stSidebar"] {
        background: linear-gradient(135deg, #536976, #076585); /* Gradient background */
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
   
    .stButton button {
        width: 100%;
        background: linear-gradient(135deg, #73C8A9, #0b8793);
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
        background: linear-gradient(135deg, #0b8793, #73C8A9);
        transform: translateY(-5px);
        box-shadow: 0px 8px 15px rgba(0, 0, 0, 0.2);
    }
    a{
        text-decoration: none;
        color: #0F403F !important;
    }
    a:hover{
        color: #0F403F !important;
        text-decoration: none;
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

""", unsafe_allow_html=True)
# Streamlit UI
st.sidebar.image("images/iesa_white.svg", width=150)
st.sidebar.markdown("""<h2>IESA Scenario Analysis</h2>""", unsafe_allow_html=True)

tables = fetch_tables()
selected_table = st.sidebar.selectbox("select table", tables,label_visibility="collapsed")

generator_tool = ScenarioGeneratorTool()
analysis_tool = ScenarioAnalysisTool()

if selected_table:
    if st.sidebar.button("Generate Scenario"):
        scenario = generator_tool.forward(selected_table)
        st.subheader("Generated Scenario:")
        st.write(scenario)

    if st.sidebar.button("Analyze Scenario"):
        scenario = get_scenario(selected_table)
        if scenario:
            analysis = analysis_tool.forward(selected_table, scenario)
            st.subheader("Scenario Analysis:")
            st.write(analysis)
        else:
            st.error("No scenario found. Please generate one first.")
