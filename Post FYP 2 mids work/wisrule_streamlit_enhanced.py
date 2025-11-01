import pandas as pd
from itertools import combinations
import mysql.connector
import streamlit as st
import numpy as np
import traceback  # Add traceback for better error reporting

# Initialize session state to store data between refreshes
if 'df' not in st.session_state:
    st.session_state.df = None
if 'transactions' not in st.session_state:
    st.session_state.transactions = None
if 'run_analysis' not in st.session_state:
    st.session_state.run_analysis = False

st.set_page_config(page_title="WisRule Mining Algorithm", layout="wide", page_icon="📊")

# Add a title and description
st.title("WisRule Mining Algorithm with Positive and Negative Rules")
st.markdown("""
This application implements the WisRule mining algorithm to discover positive and negative association rules from your data.
Adjust the support and confidence thresholds to refine the rules.
""")

# NOTE: This is a modular upgrade. You can integrate these blocks into your existing Streamlit app.

# --- 1. UPII Utility Calculation ---
def calculate_upii(antecedent, consequent, support_dict, utility_dict):
    supp_A = support_dict.get(antecedent, 0)
    supp_B = support_dict.get(consequent, 0)
    supp_AB = support_dict.get(antecedent.union(consequent), 0)

    U_A = utility_dict.get(antecedent, 1)
    U_B = utility_dict.get(consequent, 1)
    U_AB = utility_dict.get(antecedent.union(consequent), 1)

    denominator = U_A * supp_A * (1 - supp_B)
    if denominator == 0:
        return 0

    numerator = (U_AB * supp_AB) - (U_A * supp_A * U_B * supp_A)
    upii = numerator / denominator
    return upii


# --- 2. WisVal Function (composite metric) ---
def compute_wisval(support, confidence, utility, interestingness, weights):
    alpha, beta, gamma, delta = weights
    return (alpha * support) + (beta * confidence) + (gamma * utility) + (delta * interestingness)


# --- 3. Lift / Interestingness ---
def calculate_lift(antecedent, consequent, support_dict):
    supp_A = support_dict.get(antecedent, 0)
    supp_B = support_dict.get(consequent, 0)
    supp_AB = support_dict.get(antecedent.union(consequent), 0)
    if supp_A * supp_B == 0:
        return 0
    return supp_AB / (supp_A * supp_B)


# --- 4. Context-Aware Support Adjustment ---
def adjust_support_based_on_context(context_value, normal_range, base_support, adjustment_factor=0.05):
    if context_value is None:
        return base_support
    if context_value < normal_range[0] or context_value > normal_range[1]:
        return base_support - adjustment_factor  # Decrease
    return base_support + adjustment_factor      # Increase


# --- 5. Rule Evaluation with All Metrics Integrated ---
def evaluate_full_rule(antecedent, consequent, support_dict, utility_dict, context_value=None,
                       normal_range=(0, 100), weights=(0.25, 0.25, 0.25, 0.25)):
    support = support_dict.get(antecedent.union(consequent), 0)
    confidence = support_dict.get(antecedent, 0)
    utility = calculate_upii(antecedent, consequent, support_dict, utility_dict)
    interestingness = calculate_lift(antecedent, consequent, support_dict)

    # Adjust support using context
    support = adjust_support_based_on_context(context_value, normal_range, support)

    # WisVal
    wisval = compute_wisval(support, confidence, utility, interestingness, weights)

    return {
        "antecedent": antecedent,
        "consequent": consequent,
        "support": support,
        "confidence": confidence,
        "utility": utility,
        "interestingness": interestingness,
        "wisval": wisval
    }


# --- 6. Intersect Rules Across Time/Location (e.g., stable rules) ---
def intersect_rules_across_contexts(rule_sets):
    common_rules = set.intersection(*[set(rs) for rs in rule_sets if rs])
    return list(common_rules)


# --- 7. Utility Dictionary Creation ---
def create_utility_dict(itemsets, transactions):
    utility_dict = {}
    for itemset in itemsets:
        total_utility = 0
        for tx in transactions:
            if itemset.issubset(set(tx)):
                total_utility += len(itemset)  # Simple heuristic: size-based utility
        utility_dict[itemset] = total_utility / len(transactions)  # normalize
    return utility_dict

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
        self.utility_dict = {}
        self.rules = []

    def generate_frequent_itemsets(self):
        item_counts = {}
        total_transactions = len(self.transactions)

        for transaction in self.transactions:
            for item in transaction:
                item_counts[frozenset([item])] = item_counts.get(frozenset([item]), 0) + 1

        self.item_support = {
            item: count / total_transactions
            for item, count in item_counts.items()
            if count / total_transactions >= self.min_support
        }

        current_itemsets = list(self.item_support.keys())
        k = 2

        while current_itemsets:
            new_candidates = [
                i.union(j) for i in current_itemsets for j in current_itemsets
                if len(i.union(j)) == k
            ]
            candidate_counts = {candidate: 0 for candidate in new_candidates}

            for transaction in self.transactions:
                transaction_set = frozenset(transaction)
                for candidate in new_candidates:
                    if candidate.issubset(transaction_set):
                        candidate_counts[candidate] += 1

            current_itemsets = []
            for candidate, count in candidate_counts.items():
                support = count / total_transactions
                if support >= self.min_support:
                    self.item_support[candidate] = support
                    current_itemsets.append(candidate)
            k += 1
        
        # After generating itemsets, create utility dictionary
        self.utility_dict = create_utility_dict(self.item_support.keys(), self.transactions)

    def generate_rules(self):
        self.rules = []  # Clear existing rules
        for itemset in self.item_support.keys():
            if len(itemset) > 1:
                for subset in self.powerset(itemset):
                    if subset and subset != itemset:
                        antecedent = frozenset(subset)
                        consequent = itemset - antecedent
                        self.evaluate_rule(antecedent, consequent, positive=True)
                        self.evaluate_rule(antecedent, consequent, positive=False)

    def evaluate_rule(self, antecedent, consequent, positive=True):
        if not consequent:
            return

        antecedent_support = self.item_support.get(antecedent, 0)
        consequent_support = self.item_support.get(consequent, 0)
        
        # Calculate basic confidence
        if positive:
            confidence = antecedent_support
            rule_type = "Positive"
        else:
            complement_support = 1 - consequent_support
            confidence = antecedent_support * complement_support
            rule_type = "Negative"
            
        # Calculate traditional utility as lift: P(A→B) / (P(A) × P(B))
        if positive:
            utility = confidence / consequent_support if consequent_support > 0 else 0
        else:
            utility = confidence / complement_support if complement_support > 0 else 0
        
        # Calculate enhanced metrics
        interestingness = calculate_lift(antecedent, consequent, self.item_support)
        upii = calculate_upii(antecedent, consequent, self.item_support, self.utility_dict)
        
        # Calculate WisVal with default weights
        weights = (0.25, 0.25, 0.25, 0.25)  # alpha, beta, gamma, delta
        wisval = compute_wisval(
            self.item_support.get(antecedent.union(consequent), 0),
            confidence, 
            upii, 
            interestingness, 
            weights
        )

        if confidence >= self.min_confidence and utility >= self.min_utility:
            rule = (antecedent, "¬" if not positive else "", consequent, confidence, rule_type, utility, interestingness, upii, wisval)
            self.rules.append(rule)

    def get_rules(self):
        return self.rules

    @staticmethod
    def powerset(itemset):
        return [set(comb) for i in range(1, len(itemset)) for comb in combinations(itemset, i)]

# Function to fetch data from MySQL database
def fetch_data_from_db(table_name="annual_electricity_data"):
    try:
        with st.spinner('Connecting to database...'):
            conn = get_connection()
            cursor = conn.cursor()
            query = f"SELECT * FROM `{table_name}`"
            cursor.execute(query)
            rows = cursor.fetchall()
            if not rows:
                return pd.DataFrame()
            columns = [desc[0] for desc in cursor.description]
            data = pd.DataFrame(rows, columns=columns)

            # Convert MW to GWh if applicable
            if "Installed Capacity (MW)" in data.columns:
                data["Installed Capacity (MW)"] = (data["Installed Capacity (MW)"] * 8760) / 1000
                data = data.rename(columns={"Installed Capacity (MW)": "Installed Capacity (GWh)"})

            # Convert all numeric columns to float for visualization
            for col in data.columns[1:]:
                data[col] = pd.to_numeric(data[col], errors="coerce")
            data.fillna(0, inplace=True)

    except Exception as e:
        st.error(f"Error fetching data from {table_name}: {e}")
        st.error(traceback.format_exc())  # Improved error reporting
        data = pd.DataFrame()
    finally:
        conn.close()
    
    return data

# Function to categorize numerical values into labels based on year-over-year comparison
def categorize_yoy(current_value, previous_value, label):
    if previous_value is None:
        # For the first year, use a simple threshold approach
        if current_value > 0:
            return f"Initial {label}"
        else:
            return f"Low {label}"
    else:
        # Compare with previous year
        if current_value > previous_value:
            return f"High {label} (↑)"
        elif current_value < previous_value:
            return f"Low {label} (↓)"
        else:
            return f"Stable {label} (→)"

# Create transactions with year-over-year comparison
def create_yoy_transactions(df, columns):
    """Create transactions based on year-over-year comparison"""
    # Sort the dataframe by year if a year column exists
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

# Create sidebar for controls
st.sidebar.header("Data Source")
data_source = st.sidebar.radio("Select Data Source", ["Database", "Upload CSV"])

if data_source == "Database":
    table_name = st.sidebar.text_input("Enter table name", "annual_electricity_data")
    if st.sidebar.button("Fetch Data"):
        st.session_state.df = fetch_data_from_db(table_name)
        if st.session_state.df.empty:
            st.warning("No data found in the specified table.")
else:
    uploaded_file = st.sidebar.file_uploader("Upload a CSV file", type="csv")
    if uploaded_file is not None:
        st.session_state.df = pd.read_csv(uploaded_file)
        st.success("File uploaded successfully!")

# Only proceed if we have data
if st.session_state.df is not None:
    st.sidebar.header("Algorithm Parameters")
    min_support = st.sidebar.slider("Minimum Support", 0.0, 1.0, 0.3, 0.01)
    min_confidence = st.sidebar.slider("Minimum Confidence", 0.0, 1.0, 0.5, 0.01)
    
    # Add new parameter controls for WisVal weights
    st.sidebar.header("Advanced Parameters")
    advanced_options = st.sidebar.checkbox("Show Advanced Options")
    
    weights = (0.25, 0.25, 0.25, 0.25)  # Default weights
    if advanced_options:
        st.sidebar.subheader("WisVal Weights")
        alpha = st.sidebar.slider("Support Weight (α)", 0.0, 1.0, 0.25, 0.05)
        beta = st.sidebar.slider("Confidence Weight (β)", 0.0, 1.0, 0.25, 0.05)
        gamma = st.sidebar.slider("Utility Weight (γ)", 0.0, 1.0, 0.25, 0.05)
        delta = st.sidebar.slider("Interestingness Weight (δ)", 0.0, 1.0, 0.25, 0.05)
        
        # Normalize weights to sum to 1
        total = alpha + beta + gamma + delta
        if total > 0:
            alpha /= total
            beta /= total
            gamma /= total
            delta /= total
        
        weights = (alpha, beta, gamma, delta)
        
        st.sidebar.info(f"Normalized weights: α={alpha:.2f}, β={beta:.2f}, γ={gamma:.2f}, δ={delta:.2f}")

    # Display the raw data
    st.header("Input Data")
    st.dataframe(st.session_state.df)
    
    # Check if we have required columns
    required_columns = ["Installed Capacity (GWh)", "Generation (GWh)", "Imports (GWh)", "Consumption (GWh)"]
    missing_columns = [col for col in required_columns if col not in st.session_state.df.columns]
    
    if missing_columns:
        st.error(f"Missing required columns: {', '.join(missing_columns)}")
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
    
    # Display categorized transactions
    st.header("Categorized Transactions")
    transactions_df = pd.DataFrame(st.session_state.transactions, columns=column_names)
    st.dataframe(transactions_df)
    
    col1, col2 = st.columns(2)
    with col1:
        wiserule = st.button("Run WisRule Analysis")
    with col2:
        if advanced_options:
            context_aware = st.checkbox("Enable Context-Aware Support", value=False)
            if context_aware:
                st.session_state.context_aware = True
            
    st.title("WisRule Analysis Results")
    # Run the WisRule algorithm if requested
    if wiserule:
        st.session_state.run_analysis = True

if st.session_state.run_analysis:
    with st.spinner('Running WisRule Analysis...'):
        wisrule = WisRuleWithNegative(st.session_state.transactions, min_support=min_support, min_confidence=min_confidence)
        wisrule.generate_frequent_itemsets()
        wisrule.generate_rules()
        rules = wisrule.get_rules()
        
        if not rules:
            st.warning("No rules meet the support and confidence thresholds. Try lowering the thresholds.")
        else:
            # Display rules in a nice format
            st.header("Association Rules (Positive and Negative)")
            
            # Prepare data for the table
            rule_data = []
            for antecedent, negation, consequent, confidence, rule_type, utility, interestingness, upii, wisval in rules:
                rule_data.append({
                    "Antecedent": ", ".join(set(antecedent)),
                    "Consequent": f"{negation}{', '.join(set(consequent))}",
                    "Confidence": f"{confidence:.2f}",
                    "Rule Type": rule_type,
                    "Utility": f"{utility:.2f}",
                    "Interestingness": f"{interestingness:.2f}",
                    "UPII": f"{upii:.2f}",
                    "WisVal": f"{wisval:.2f}"
                })
            
            rule_df = pd.DataFrame(rule_data)
            
            # Convert numeric columns for sorting
            for col in ['Confidence', 'Utility', 'Interestingness', 'UPII', 'WisVal']:
                rule_df[col] = pd.to_numeric(rule_df[col])
            
            # Add sorting options
            sort_col = st.selectbox("Sort rules by", ['WisVal', 'Confidence', 'Utility', 'Interestingness', 'UPII'])
            st.dataframe(rule_df.sort_values(by=sort_col, ascending=False))
            
            # Visualize the distribution of rule types
            st.header("Rule Type Distribution")
            rule_types = rule_df["Rule Type"].value_counts()
            st.bar_chart(rule_types)
            
            # Visualize metrics by rule type
            st.header("Metrics by Rule Type")
            metrics_tab1, metrics_tab2 = st.tabs(["Confidence & Utility", "Interestingness & WisVal"])
            
            with metrics_tab1:
                col1, col2 = st.columns(2)
                with col1:
                    confidence_by_type = rule_df.groupby("Rule Type")["Confidence"].mean().reset_index()
                    st.subheader("Average Confidence")
                    st.bar_chart(confidence_by_type.set_index("Rule Type"))
                
                with col2:
                    utility_by_type = rule_df.groupby("Rule Type")["Utility"].mean().reset_index()
                    st.subheader("Average Utility")
                    st.bar_chart(utility_by_type.set_index("Rule Type"))
            
            with metrics_tab2:
                col1, col2 = st.columns(2)
                with col1:
                    interestingness_by_type = rule_df.groupby("Rule Type")["Interestingness"].mean().reset_index()
                    st.subheader("Average Interestingness")
                    st.bar_chart(interestingness_by_type.set_index("Rule Type"))
                
                with col2:
                    wisval_by_type = rule_df.groupby("Rule Type")["WisVal"].mean().reset_index()
                    st.subheader("Average WisVal")
                    st.bar_chart(wisval_by_type.set_index("Rule Type"))
            
            # Create network graph of rules visualization
            st.header("Rule Network Visualization")
            
            # Create a simplified network representation with enhanced metrics
            network_df = pd.DataFrame({
                "From": [row["Antecedent"] for _, row in rule_df.iterrows()],
                "To": [row["Consequent"] for _, row in rule_df.iterrows()],
                "Confidence": rule_df["Confidence"],
                "Type": rule_df["Rule Type"],
                "Utility": rule_df["Utility"],
                "Interestingness": rule_df["Interestingness"],
                "UPII": rule_df["UPII"],
                "WisVal": rule_df["WisVal"]
            })
            
            # Display the network as a table with colored backgrounds
            def color_rule_type(val):
                color = 'lightblue' if val == 'Positive' else 'lightcoral'
                return f'background-color: {color}'
            
            st.dataframe(network_df.style.applymap(color_rule_type, subset=['Type']))
            
            # Display top rules by WisVal
            st.subheader("Top Rules by WisVal Score")
            top_rules = rule_df.sort_values(by="WisVal", ascending=False).head(10)
            
            chart_data = pd.DataFrame({
                "Rule": [f"{row['Antecedent']} → {row['Consequent']}" for _, row in top_rules.iterrows()],
                "WisVal": top_rules["WisVal"],
                "Confidence": top_rules["Confidence"],
                "Utility": top_rules["Utility"],
                "Interestingness": top_rules["Interestingness"]
            })
            
            # Show multiple metrics as a chart
            metrics_to_show = st.multiselect(
                "Select metrics to display", 
                ["WisVal", "Confidence", "Utility", "Interestingness", "UPII"],
                default=["WisVal", "Confidence"]
            )
            
            if metrics_to_show:
                st.bar_chart(chart_data.set_index("Rule")[metrics_to_show])
            
            # Comparative Analysis
            st.header("Comparative Analysis")
            st.info("Compare how different metrics rank rules differently")
            
            col1, col2 = st.columns(2)
            with col1:
                metric1 = st.selectbox("First Metric", ["WisVal", "Confidence", "Utility", "Interestingness", "UPII"], index=0)
            with col2:
                metric2 = st.selectbox("Second Metric", ["WisVal", "Confidence", "Utility", "Interestingness", "UPII"], index=1)
            
            if metric1 != metric2:
                scatter_data = pd.DataFrame({
                    "Rule": [f"{row['Antecedent']} → {row['Consequent']}" for _, row in rule_df.iterrows()],
                    metric1: rule_df[metric1],
                    metric2: rule_df[metric2],
                    "Type": rule_df["Rule Type"]
                })
                
                st.subheader(f"Comparison: {metric1} vs {metric2}")
                chart = st.scatter_chart(data=scatter_data, x=metric1, y=metric2, color="Type")
else:
    st.info("Please select a data source to begin analysis")
