import pandas as pd
from itertools import combinations
import mysql.connector
import streamlit as st
import numpy as np
import traceback
from streamlit_option_menu import option_menu
import os

# Initialize session state to store data between refreshes
if 'df' not in st.session_state:
    st.session_state.df = None
if 'transactions' not in st.session_state:
    st.session_state.transactions = None
if 'run_analysis' not in st.session_state:
    st.session_state.run_analysis = False

st.set_page_config(page_title="WisRule Mining Algorithm", layout="wide", page_icon="📊")

selected = option_menu(
    menu_title=None,
    options=["Dashboard","Data Planner", "Scenario","Wisdom Mining", "Prediction", "IESA Assistant"],
    icons=["clipboard-data", "bar-chart", "graph-up", "graph-up-arrow", "robot", "robot"],
    default_index=3,
    orientation="horizontal",
    styles={
        "container": {
            "padding": "0!important", 
            "background-color": "transparent", 
            "margin-top": "-15px", 
            "position": "relative", 
            "z-index": "100",
            "border-radius": "0px",
            "box-shadow": "none",
            "border": "none",
            "border-bottom": "2px solid #e0e5eb",
            "margin-bottom": "15px"
        },
        "icon": {"color": "106466", "font-size": "18px"},
        "nav-link": {
            "font-size": "16px",
            "text-align": "center",
            "--hover-color": "rgba(255,255,255,0.1)",
            "padding": "10px",
            "margin": "0 2px",
            "position": "relative",
            "border": "none",
            "background-color": "transparent"
        },
        "nav-link-selected": {
            "background-color": "transparent", 
            "color": "#106466",
            "font-weight": "600",
            "border-radius": "0px",
            "border": "none",
            "border-bottom": "3px solid #73c8a9"
        },
    }
)

# ---- Page Content Rendering ----
if selected == "Dashboard":
    os.system("streamlit run iesa_dashboard.py")

elif selected == "Data Planner":
    os.system("streamlit run iesa_data_planner.py")

elif selected == "Scenario":
    os.system("streamlit run iesa_scenerio_analysis_with_k_means.py")

elif selected == "Prediction":
     os.system("streamlit run iesa_prediction_engine.py")

elif selected == "IESA Assistant":
    os.system("streamlit run iesa_personalized_recommendations.py")

# Add a title and description
# st.title("Wisdom Mining with WisRule")
# st.markdown("""
# This application implements the WisRule mining algorithm to discover positive and negative association rules from your data.
# Adjust the support and confidence thresholds to refine the rules.
# """)
st.markdown("""
    <style>
    /* General Styling */
    header {
        border-bottom: 3px solid  #136a8a !important; 
        margin-bottom: 0 !important;
        position: relative !important;
        z-index: 99 !important;
        height: 2.5rem !important;
    }
    [data-testid="stSidebar"] {
        background: linear-gradient(135deg, #73C8A9, #0b8793); /* Gradient background */
        color: white;
        margin-top: -10px;
        box-shadow: 2px 0 10px rgba(0,0,0,0.2);
        z-index: 98;
    }
    .sidebar-content {
        margin-top: -60px;
        padding: 20px;
    }
    
    /* Top navigation buttons styling - make all buttons consistent */
    div[data-testid="stHorizontalBlock"] > div .stButton button {
        background-color: #0b8793;
        color: white !important;
        border: 1px solid #4AC29A;
        border-radius: 5px;
        padding: 6px 12px;
        font-weight: bold;
        box-shadow: 0 2px 5px rgba(0,0,0,0.2);
        transition: all 0.3s ease;
        width: auto !important;
        min-width: 120px;
        max-width: 150px;
        margin: 25px auto 20px;
        font-size: 14px;
        white-space: nowrap;
        display: block;
    }
    
    /* Remove grey background from navigation container */
    section[data-testid="stSectionContainer"] div[data-testid="stVerticalBlock"] {
        background-color: transparent !important;
    }
    
    /* Navigation bar styling - remove borders except bottom */
    [data-baseweb="tab-list"] {
        border-top: none !important;
        border-left: none !important;
        border-right: none !important;
        border-bottom: 2px solid #e0e5eb !important;
        background-color: transparent !important;
    }
    
    /* Remove any backgrounds */
    .stTabs {
        background-color: transparent !important;
    }
    
    .stTabs [data-baseweb="tab-list"] {
        background-color: transparent !important;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: transparent !important;
    }
    
    /* Add bottom bar to active navigation item */
    .nav-link-selected::after {
        content: '' !important;
        position: absolute !important;
        bottom: -3px !important;
        left: 10% !important;
        width: 80% !important;
        height: 4px !important;
        background-color: #73c8a9 !important; 
        border-radius: 2px !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.2) !important;
    }
    
    /* Make the active tab text color the original color */
    .nav-link-selected {
        color: #106466 !important; 
        font-weight: bold !important;
    }
    
    /* Highlighted button (active page) */
    [data-testid="stHorizontalBlock"] div:nth-child(2) .stButton button {
        background-color: #4AC29A !important;
        box-shadow: 0 4px 8px rgba(0,0,0,0.25) !important;
        border: 2px solid #73C8A9 !important;
        position: relative;
        transform: translateY(-2px);
    }
    
   

    div[data-testid="stHorizontalBlock"] > div .stButton button:hover {
        background-color: #4AC29A;
        transform: translateY(-1px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    
    /* Toggle button specific styles - target the first button in the first column */
    div[data-testid="stHorizontalBlock"] > div:first-child .stButton button {
        position: fixed;
        z-index: 999;
        width: auto !important;
        min-width: 60px;
        max-width: 80px;
    }
    
    /* Sidebar element styling */
    [data-testid="stSidebar"] h2 {
        font-size: 22px !important;
        margin-top: 25px !important;
        margin-bottom: 15px !important;
        padding-bottom: 5px;
        border-bottom: 2px solid rgba(255,255,255,0.3);
        text-shadow: 1px 1px 2px rgba(0,0,0,0.2);
    }
            #MainMenu, footer, header {
        visibility: hidden;
    }
    
    /* Remove extra spacing at the top */
    .block-container {
        padding-top: 0.1rem !important;
    }
    
    /* Main wrapper for streamlit app */
    .main .block-container {
        padding-top: 0.5rem !important;
        margin-top: 0 !important;
    }
    
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] label {
        color: rgba(255,255,255,0.9) !important;
        font-weight: 500;
        margin-bottom: 8px;
        font-size: 15px;
    }
    
    [data-testid="stSidebar"] .stSelectbox > div {
        background-color: rgba(255,255,255,0.1) !important;
        border: 1px solid rgba(255,255,255,0.2) !important;
        border-radius: 5px;
        color: white !important;
        margin-bottom: 15px;
    }
    
    [data-testid="stSidebar"] .stSelectbox > div:hover {
        border: 1px solid rgba(255,255,255,0.4) !important;
    }
    
    /* Link styling */
    a {
        text-decoration: none;
        color: #0F403F !important;
    }
    
    a:hover {
        color: #0F403F !important;
        text-decoration: none;
    }
    
    /* Sidebar specific button styles */
    [data-testid="stSidebar"] .stButton button {
        width: 100%;
        background-color: #0b8793;
        color: white !important;
        border: 1px solid #4AC29A;
        border-radius: 5px;
        font-size: 0.9em;
        font-weight: bold;
        padding: 8px 20px;
        cursor: pointer;
        transition: all 0.3s ease;
        margin-bottom: 10px;
        letter-spacing: 0.3px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }

    [data-testid="stSidebar"] .stButton button:hover {
        background-color: #4AC29A;
        color: white !important;
        box-shadow: 0 3px 7px rgba(0,0,0,0.15);
        transform: translateY(-1px);
    }
    
    /* Other sidebar specific elements */
    [data-testid="stSidebar"] [data-testid="stBaseButton-secondary"] {
        background-color: #0b8793 !important;
        width: 100% !important;
        border: 1px solid #4AC29A;
        border-radius: 5px;
    }

    [data-testid="stSidebar"] [data-testid="stBaseButton-secondary"]:hover {
        background-color: #0b8793;
        color: white !important;
    }

    /* Fix column layout */
    .row-widget.stHorizontalBlock {
        flex-wrap: wrap;
        gap: 20px;
    }
    
    /* Make sure columns take equal space - exactly 2 per row */
    [data-testid="column"] {
        width: calc(50% - 10px) !important;
        flex: 0 0 calc(50% - 10px) !important;
        max-width: calc(50% - 10px) !important;
        margin: 0 !important;
        padding: 0 !important;
    }
    
    /* Ensure charts take full width of their containers */
    .element-container {
        width: 100% !important;
    }
    
    /* Chart styling */
    .chart {
        width: 100%;
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        padding: 10px;
        background: white;
        box-shadow: none;
    }
    
    /* Main content spacing */
    .block-container {
        padding-top: 30px !important;
        max-width: 95%;
        margin: 0 auto;
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
        box-shadow: none;
        margin-top: 30px;  /* Reduced from 40px */
        padding: 15px; /* Reduced from 20px */
        width: 99%; /* Full width */
    }

    /* Chart Improvements */
    .marks {
        border-radius: 15px;
        border: 1px solid #0b8793;
        box-shadow: none;
        margin-top: 30px;  /* Reduced from 40px */
        padding: 15px; /* Reduced from 20px */
        width: 99%;
        background-color: #f9fcfc;
    }
    
    /* Chart styling */
    .chart-wrapper {
        margin-bottom: 20px; /* Reduced from 30px */
        background: white;
        padding: 15px; /* Reduced from 20px */
        border-radius: 10px;
        box-shadow: none;
    }
    
    .marks .axis-title, .marks .axis-label {
        font-weight: bold !important;
        font-size: 16px !important;
        fill: #333 !important;
    }
    
    .marks .axis-domain, .marks .axis-tick {
        stroke: #333 !important;
        stroke-width: 2px !important;
    }
    
    .marks .mark-line line {
        stroke-width: 3.5px !important;
    }
    
    .marks .mark-point circle {
        stroke-width: 1.5px !important;
        fill-opacity: 1 !important;
    }
    </style>
""", unsafe_allow_html=True)



 
image_path = "images/iesa_white.svg"
st.sidebar.image(image_path,width=150)
st.sidebar.markdown("""
    <h2>Wisdom Mining Dashboard</h2>
""",unsafe_allow_html=True)
# Connection
def get_connection():
    return mysql.connector.connect(
        host="localhost",
        port="3306",
        user="root",
        passwd="admin123",
        db="iesa_db"
    )

class WisRuleWithNegative:
    def __init__(self, transactions, min_support=0.15, min_confidence=0.3, min_utility=0.1):
        self.transactions = transactions
        self.min_support = min_support
        self.min_confidence = min_confidence
        self.min_utility = min_utility
        self.item_support = {}
        self.rules = []
        self.total_transactions = len(transactions)
        # Dictionary to store utility metrics for calculations
        self.utility_dict = {
            "transaction_count": self.total_transactions,
            "item_counts": {},
            "itemset_counts": {}
        }

    def generate_frequent_itemsets(self):
        item_counts = {}
        total_transactions = self.total_transactions
          # Count occurrences of each item
        for transaction in self.transactions:
            for item in transaction:
                item_counts[frozenset([item])] = item_counts.get(frozenset([item]), 0) + 1
                
        # Store item counts in utility dictionary for later use
        self.utility_dict["item_counts"] = {next(iter(item)): count for item, count in item_counts.items()}
        
        # Filter by minimum support
        self.item_support = {
            item: count / total_transactions
            for item, count in item_counts.items()
            if count / total_transactions >= self.min_support
        }
        
        current_itemsets = list(self.item_support.keys())
        k = 2
        
        # Generate larger itemsets iteratively
        while current_itemsets:
            new_candidates = [
                i.union(j) for i in current_itemsets for j in current_itemsets
                if len(i.union(j)) == k
            ]
            candidate_counts = {candidate: 0 for candidate in new_candidates}
            
            # Count occurrences of each candidate itemset
            for transaction in self.transactions:
                transaction_set = frozenset(transaction)
                for candidate in new_candidates:
                    if candidate.issubset(transaction_set):
                        candidate_counts[candidate] += 1
                        
            # Store itemset counts in utility dictionary
            for candidate, count in candidate_counts.items():
                if len(candidate) > 1:
                    self.utility_dict["itemset_counts"][frozenset(candidate)] = count
                    
            current_itemsets = []
            for candidate, count in candidate_counts.items():
                support = count / total_transactions
                if support >= self.min_support:
                    self.item_support[candidate] = support
                    current_itemsets.append(candidate)
            k += 1

    def generate_rules(self):
        self.rules = []
        for itemset in self.item_support.keys():
            if len(itemset) > 1:
                for subset in self.powerset(itemset):
                    if subset and subset != itemset:
                        antecedent = frozenset(subset)
                        consequent = itemset - antecedent
                        self.evaluate_rule(antecedent, consequent, positive=True)
                        self.evaluate_rule(antecedent, consequent, positive=False)

    def calculate_upii(self, antecedent, consequent, positive=True):
        """Calculate Utility-based Probabilistic Interestingness Index (UPII)"""
        ant_support = self.item_support.get(antecedent, 0)
        cons_support = self.item_support.get(consequent, 0)
        
        if not positive:
            cons_support = 1 - cons_support
            
        if ant_support == 0 or cons_support == 0:
            return 0
            
        # Calculate joint probability
        joint_prob = 0
        if positive:
            joint_prob = self.utility_dict.get("itemset_counts", {}).get(
                frozenset(antecedent.union(consequent)), 0
            ) / self.total_transactions
        else:
            # For negative rules, calculate differently
            negation_count = 0
            for transaction in self.transactions:
                if antecedent.issubset(transaction) and not consequent.issubset(transaction):
                    negation_count += 1
            joint_prob = negation_count / self.total_transactions
            
        # Calculate UPII
        expected_prob = ant_support * cons_support
        return (joint_prob - expected_prob) / max(joint_prob, expected_prob) if max(joint_prob, expected_prob) > 0 else 0

    def calculate_lift(self, antecedent, consequent, positive=True):
        """Calculate lift/interestingness"""
        ant_support = self.item_support.get(antecedent, 0)
        cons_support = self.item_support.get(consequent, 0)
        
        if not positive:
            cons_support = 1 - cons_support
            
        if ant_support == 0 or cons_support == 0:
            return 0
            
        # Calculate joint probability
        joint_prob = 0
        if positive:
            joint_prob = self.utility_dict.get("itemset_counts", {}).get(
                frozenset(antecedent.union(consequent)), 0
            ) / self.total_transactions
        else:
            # For negative rules
            negation_count = 0
            for transaction in self.transactions:
                if antecedent.issubset(transaction) and not consequent.issubset(transaction):
                    negation_count += 1
            joint_prob = negation_count / self.total_transactions
            
        # Calculate lift
        return joint_prob / (ant_support * cons_support) if (ant_support * cons_support) > 0 else 0

    def calculate_wisval(self, confidence, lift, upii):
        """Calculate WisVal - Wisdom Value metric"""
        # Weighted combination of confidence, lift and UPII
        return (0.4 * confidence) + (0.3 * lift) + (0.3 * upii)
        
    def evaluate_rule(self, antecedent, consequent, positive=True):
        if not consequent:
            return
            
        antecedent_support = self.item_support.get(antecedent, 0)
        consequent_support = self.item_support.get(consequent, 0)
        
        # Calculate confidence
        if positive:
            confidence = antecedent_support
            rule_type = "Positive"
            complement_support = consequent_support
        else:
            complement_support = 1 - consequent_support
            confidence = antecedent_support * complement_support
            rule_type = "Negative"
            
        # Calculate traditional utility
        if positive:
            utility = confidence / consequent_support if consequent_support > 0 else 0
        else:
            utility = confidence / complement_support if complement_support > 0 else 0
            
        # Calculate advanced metrics
        lift = self.calculate_lift(antecedent, consequent, positive)
        upii = self.calculate_upii(antecedent, consequent, positive)
        wisval = self.calculate_wisval(confidence, lift, upii)
        
        # Only add rules that meet the minimum thresholds
        if confidence >= self.min_confidence and utility >= self.min_utility:
            rule = (antecedent, "¬" if not positive else "", consequent, confidence, 
                   rule_type, utility, lift, upii, wisval)
            self.rules.append(rule)

    def get_rules(self):
        return self.rules

    @staticmethod
    def powerset(itemset):
        return [set(comb) for i in range(1, len(itemset)) for comb in combinations(itemset, i)]

# Data fetching function
def fetch_data_from_db(table_name="annual_electricity_data"):
    try:
        with st.spinner(f'Connecting to database table {table_name}...'):
            conn = get_connection()
            cursor = conn.cursor()
            query = f"SELECT * FROM `{table_name}`"
            cursor.execute(query)
            rows = cursor.fetchall()
            if not rows:
                return pd.DataFrame()
            columns = [desc[0] for desc in cursor.description]
            data = pd.DataFrame(rows, columns=columns)

            # Optional conversion if Installed Capacity (MW) exists
            if "Installed Capacity (MW)" in data.columns:
                data["Installed Capacity (MW)"] = (data["Installed Capacity (MW)"] * 8760) / 1000
                data.rename(columns={"Installed Capacity (MW)": "Installed Capacity (GWh)"}, inplace=True)

            for col in data.columns[1:]:
                data[col] = pd.to_numeric(data[col], errors="coerce")
            data.fillna(0, inplace=True)
    except Exception as e:
        st.error(f"Error: {e}")
        st.error(traceback.format_exc())
        data = pd.DataFrame()
    finally:
        conn.close()
    return data

# Optional helper for year-over-year labels
def categorize_yoy(current_value, previous_value, label):
    if previous_value is None:
        return f"Initial {label}" if current_value > 0 else f"Low {label}"
    if current_value > previous_value:
        return f"High {label} (↑)"
    elif current_value < previous_value:
        return f"Low {label} (↓)"
    else:
        return f"Stable {label} (→)"

# Transaction creation from YOY analysis
def create_yoy_transactions(df, columns):
    year_col = None
    for col in df.columns:
        if 'year' in col.lower():
            year_col = col
            df = df.sort_values(by=year_col)
            break
            
    transactions = []
    previous_values = {col: None for col in columns}
    column_names = []
    
    for idx, row in df.iterrows():
        transaction = []
        for col in columns:
            if col in df.columns:
                label = col.split(" ")[0]  # Extract the label part (e.g., "Imports" from "Imports (GWh)")
                current_value = row[col]
                previous_value = previous_values[col]
                
                # Categorize based on year-over-year comparison
                category = categorize_yoy(current_value, previous_value, label)
                transaction.append(category)
                
                # Update previous value for the next iteration
                previous_values[col] = current_value
                
                # Store column name for first row
                if len(column_names) < len(columns):
                    column_names.append(col)
        
        # Add year information if available
        if year_col:
            transaction.append(f"Year: {row[year_col]}")
            if len(column_names) < len(columns) + 1:
                column_names.append("Year")
                
        transactions.append(transaction)
    
    return transactions, column_names

# Optional secondary table fetch
def fetch_table(table_name):
    conn = get_connection()
    df = pd.read_sql(f"SELECT * FROM {table_name}", conn)
    conn.close()
    return df

# Create transactions from utility/location dimensions
def create_dimension_transactions(location_df, utility_df):
    transactions = []
    for i in range(len(location_df)):
        row = []
        location = location_df.iloc[i].get("Province") or location_df.iloc[i].get("Region")
        if location:
            row.append(f"Location: {location}")
        year = location_df.iloc[i].get("Year")
        if year:
            row.append(f"Year: {year}")
        for col in utility_df.columns[1:]:
            val = utility_df.iloc[i][col]
            if pd.notna(val):
                row.append(f"Utility: {col}")
        transactions.append(row)
    return transactions

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

available_tables = fetch_tables()
if not available_tables:
    st.sidebar.error("No tables found in database")
else:
    table_name = st.sidebar.selectbox("Select table", available_tables, index=0)
    if st.sidebar.button("Load Data"):
        st.session_state.df = fetch_data_from_db(table_name)
        if st.session_state.df.empty:
            st.warning("No data found in the specified table.")
        else:
            st.success(f"Data loaded from {table_name} successfully!")

# Only proceed if we have data
if st.session_state.df is not None:   
    st.sidebar.header("Algorithm Parameters")
    min_support = st.sidebar.slider("Minimum Support", 0.0, 1.0, 0.3, 0.01)
    min_confidence = st.sidebar.slider("Minimum Confidence", 0.0, 1.0, 0.5, 0.01)
    min_utility = st.sidebar.slider("Minimum Utility", 0.0, 1.0, 0.1, 0.01)
    
    # Advanced Parameter Explanation
    with st.sidebar.expander("Advanced WisRule Metrics"):
        st.markdown("""
        **New Metrics Explained:**
        - **Lift**: Measures how much more likely the consequent is, given the antecedent, compared to its base probability.
        - **UPII**: Utility-based Probabilistic Interestingness Index - measures deviation from expected probability.
        - **WisVal**: Combined wisdom value based on confidence, lift and UPII.
        """)
    
    # Optional filters for dimension-based data
    st.sidebar.subheader("WisRule Dimensions")
    selected_location_table = st.sidebar.selectbox("Select Location Table", ["province_wise_electricity_consumption_gwh"])
    selected_utility_table = st.sidebar.selectbox("Select Utility Table", ["electricity_consumption_by_sector_gwh"])
    use_dimensions = st.sidebar.checkbox("Use Location & Utility Dimensions", value=False)

    # Display the raw data
    st.header("Input Data")
    st.dataframe(st.session_state.df)
    
    # Check if we have required columns
    required_columns = ["Installed Capacity (GWh)", "Generation (GWh)", "Imports (GWh)", "Consumption (GWh)"]
    missing_columns = [col for col in required_columns if col not in st.session_state.df.columns]
    
    if missing_columns:
        # st.error(f"Missing required columns: {', '.join(missing_columns)}")
        st.info("Please select columns for analysis:")
        selected_columns = st.multiselect("Select columns for analysis (need at least 3)", 
                                         st.session_state.df.select_dtypes(include=['number']).columns,
                                         max_selections=4)
        if len(selected_columns) < 3:
            st.warning("Please select at least 3 columns for meaningful analysis")
        else:
            required_columns = selected_columns
    
    # Ensure all relevant columns are numeric
    for col in required_columns:
        if col in st.session_state.df.columns:
            st.session_state.df[col] = pd.to_numeric(st.session_state.df[col], errors='coerce')
    
    # Create transactions with year-over-year comparison
    st.session_state.transactions, column_names = create_yoy_transactions(st.session_state.df, required_columns)
      # Add dimension-based transactions if selected
    if use_dimensions:
        try:
            location_df = fetch_table(selected_location_table)
            utility_df = fetch_table(selected_utility_table)
            dimension_transactions = create_dimension_transactions(location_df, utility_df)
            st.session_state.transactions.extend(dimension_transactions)
            st.success("Dimension-based transactions added.")
        except Exception as e:
            st.error(f"Error adding dimensions: {e}")
    
    # Display categorized transactions
    st.header("Categorized Transactions")
    # Safe display of transactions - using only basic transaction data if dimensions were added
    if use_dimensions:
        # Display only the first few transactions that have the original structure
        original_transactions = st.session_state.transactions[:len(st.session_state.df)]
        transactions_df = pd.DataFrame(original_transactions, columns=column_names)
        st.dataframe(transactions_df)
        st.info(f"Note: {len(st.session_state.transactions) - len(original_transactions)} additional transactions from dimensions are not shown in this view.")
    else:
        transactions_df = pd.DataFrame(st.session_state.transactions, columns=column_names)
        st.dataframe(transactions_df)
    
    # Add a prominent button for WisRule Analysis
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        if st.button("Run Wisdom Mining Analysis", type="primary", use_container_width=True):
            st.session_state.run_analysis = True
    
    st.title("WisRule Analysis Results")

if st.session_state.run_analysis:
    with st.spinner('Running WisRule Algorithm...'):
        wisrule = WisRuleWithNegative(
            transactions=st.session_state.transactions,
            min_support=min_support,
            min_confidence=min_confidence
        )
        wisrule.generate_frequent_itemsets()
        wisrule.generate_rules()
        rules = wisrule.get_rules()
        
        if not rules:
            st.warning("No rules meet the support and confidence thresholds. Try lowering the thresholds.")
        else:
            # Display rules in a nice format
            st.header("WisRule Results")
              # Prepare data for the table
            rule_data = []
            for antecedent, negation, consequent, confidence, rule_type, utility, lift, upii, wisval in rules:
                rule_data.append({
                    "Antecedent": ", ".join(set(antecedent)),
                    "Consequent": f"{negation}{', '.join(set(consequent))}",
                    "Confidence": f"{confidence:.2f}",
                    "Rule Type": rule_type,
                    "Utility": f"{utility:.2f}",
                    "Lift": f"{lift:.2f}",
                    "UPII": f"{upii:.2f}",
                    "WisVal": f"{wisval:.2f}"
                })
            
            rule_df = pd.DataFrame(rule_data)
            
            # Sort rules by WisVal for better insights (highest WisVal first)
            rule_df["WisVal"] = pd.to_numeric(rule_df["WisVal"])
            rule_df = rule_df.sort_values(by="WisVal", ascending=False)
            
            # Create tabs for different views of the data
            tabs = st.tabs(["All Rules", "Metric Analysis", "Top Rules"])
            
            with tabs[0]:
                st.subheader("All Discovered Rules")
                st.dataframe(rule_df)
                
                # Add download button for rules
                st.download_button(
                    label="Download Rules as CSV",
                    data=rule_df.to_csv(index=False).encode('utf-8'),
                    file_name="wisrule_results.csv",
                    mime='text/csv'
                )
            
            with tabs[1]:
                # Convert columns to numeric for charts
                for col in ["Confidence", "Utility", "Lift", "UPII", "WisVal"]:
                    rule_df[col] = pd.to_numeric(rule_df[col])
                
                st.subheader("Rule Type Distribution")
                rule_types = rule_df["Rule Type"].value_counts()
                st.bar_chart(rule_types)
                
                # Create columns for metric charts
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("Confidence by Rule Type")
                    confidence_by_type = rule_df.groupby("Rule Type")["Confidence"].mean().reset_index()
                    st.bar_chart(confidence_by_type.set_index("Rule Type"))
                
                with col2:
                    st.subheader("WisVal by Rule Type")
                    wisval_by_type = rule_df.groupby("Rule Type")["WisVal"].mean().reset_index()
                    st.bar_chart(wisval_by_type.set_index("Rule Type"))
                
                # Create metrics comparison
                st.subheader("Comparison of Metrics")
                metric_df = rule_df[["Rule Type", "Confidence", "Utility", "Lift", "UPII", "WisVal"]].melt(
                    id_vars=["Rule Type"], 
                    var_name="Metric", 
                    value_name="Value"
                )
                st.line_chart(metric_df.groupby(["Rule Type", "Metric"])["Value"].mean().unstack())
            
            with tabs[2]:
                st.subheader("Top Rules by WisVal")
                # Get top 10 rules by WisVal
                top_rules = rule_df.head(10).copy()
                top_rules["Rule"] = top_rules.apply(
                    lambda row: f"{row['Antecedent']} → {row['Consequent']}", 
                    axis=1
                )
                
                # Show top rules metrics
                st.dataframe(top_rules[["Rule", "Rule Type", "Confidence", "WisVal"]])
                
                # Create chart for top rules
                chart_data = top_rules[["Rule", "Confidence", "WisVal"]].set_index("Rule")
                st.bar_chart(chart_data)
            
            # Create network graph of rules visualization using Streamlit
            st.header("Rule Network Visualization")
            st.subheader("Rule Relationships")
            
            # Create a simplified network representation
            network_df = pd.DataFrame({
                "From": [row["Antecedent"] for _, row in rule_df.iterrows()],
                "To": [row["Consequent"] for _, row in rule_df.iterrows()],
                "Confidence": [float(row["Confidence"]) for _, row in rule_df.iterrows()],
                "Type": [row["Rule Type"] for _, row in rule_df.iterrows()],
                "Utility": [float(row["Utility"]) for _, row in rule_df.iterrows()]
            })
            
            # Display the network as a table with colored backgrounds
            def color_rule_type(val):
                color = 'lightblue' if val == 'Positive' else 'lightcoral'
                return f'background-color: {color}'
            
            st.dataframe(network_df.style.applymap(color_rule_type, subset=['Type']))
            
            # Display rule strength using Streamlit charts
            st.subheader("Top 10 Rule Confidence")
            chart_data = pd.DataFrame({
                "Rule": [f"{row['From']} → {row['To']}" for _, row in network_df.iterrows()],
                "Confidence": network_df["Confidence"],
                "Type": network_df["Type"],
                "Utility": network_df["Utility"]
            }).head(10)
            
            st.bar_chart(chart_data.set_index("Rule")[["Confidence", "Utility"]])
else:
    st.info("Please Load data to begin analysis")
