import pandas as pd
from itertools import combinations
import mysql.connector
import streamlit as st
import numpy as np
import traceback

if 'df' not in st.session_state:
    st.session_state.df = None
if 'transactions' not in st.session_state:
    st.session_state.transactions = None
if 'run_analysis' not in st.session_state:
    st.session_state.run_analysis = False

st.set_page_config(page_title="WisRule Mining Algorithm", layout="wide", page_icon="📊")
st.title("WisRule Mining Algorithm with Positive and Negative Rules")
st.markdown("""
This application implements the WisRule mining algorithm to discover positive and negative association rules from your data.
Adjust the support and confidence thresholds to refine the rules.
""")

# Database connection
def get_connection():
    return mysql.connector.connect(
        host="localhost",
        port="3306",
        user="root",
        passwd="admin123",
        db="iesa_db"
    )

# WisRule Algorithm Class
class WisRuleWithNegative:
    def _init_(self, transactions, min_support=0.15, min_confidence=0.3, min_utility=0.1):
        self.transactions = transactions
        self.min_support = min_support
        self.min_confidence = min_confidence
        self.min_utility = min_utility
        self.item_support = {}
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

    def evaluate_rule(self, antecedent, consequent, positive=True):
        if not consequent:
            return
        antecedent_support = self.item_support.get(antecedent, 0)
        consequent_support = self.item_support.get(consequent, 0)
        if positive:
            confidence = antecedent_support
            rule_type = "Positive"
        else:
            complement_support = 1 - consequent_support
            confidence = antecedent_support * complement_support
            rule_type = "Negative"
        if positive:
            utility = confidence / consequent_support if consequent_support > 0 else 0
        else:
            utility = confidence / complement_support if complement_support > 0 else 0
        if confidence >= self.min_confidence and utility >= self.min_utility:
            rule = (antecedent, "¬" if not positive else "", consequent, confidence, rule_type, utility)
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
            query = f"SELECT * FROM {table_name}"
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
    for _, row in df.iterrows():
        transaction = []
        for col in columns:
            if col in df.columns:
                label = col.split(" ")[0]
                curr = row[col]
                prev = previous_values[col]
                transaction.append(categorize_yoy(curr, prev, label))
                previous_values[col] = curr
        if year_col:
            transaction.append(f"Year: {row[year_col]}")
        transactions.append(transaction)
    return transactions

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

# Sidebar interface for input
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


if st.session_state.df is not None:
    st.sidebar.header("Algorithm Parameters")
    min_support = st.sidebar.slider("Minimum Support", 0.0, 1.0, 0.3, 0.01)
    min_confidence = st.sidebar.slider("Minimum Confidence", 0.0, 1.0, 0.5, 0.01)

    # Optional filters for dimension-based data
    st.sidebar.subheader("WisRule Dimensions")
    selected_location_table = st.sidebar.selectbox("Select Location Table", ["province_wise_electricity_consumption_gwh"])
    selected_utility_table = st.sidebar.selectbox("Select Utility Table", ["electricity_consumption_by_sector_gwh"])
    use_dimensions = st.sidebar.checkbox("Use Location & Utility Dimensions", value=False)

    st.header("Input Data")
    st.dataframe(st.session_state.df)

    required_columns = ["Installed Capacity (GWh)", "Generation (GWh)", "Imports (GWh)", "Consumption (GWh)"]
    for col in required_columns:
        if col in st.session_state.df.columns:
            st.session_state.df[col] = pd.to_numeric(st.session_state.df[col], errors='coerce')

    # Create year-over-year based transactions
    st.session_state.transactions = create_yoy_transactions(st.session_state.df, required_columns)

    if use_dimensions:
        location_df = fetch_table(selected_location_table)
        utility_df = fetch_table(selected_utility_table)
        dimension_transactions = create_dimension_transactions(location_df, utility_df)
        st.session_state.transactions.extend(dimension_transactions)
        st.success("Dimension-based transactions added.")

    st.header("Categorized Transactions")
    st.dataframe(pd.DataFrame(st.session_state.transactions))

    if st.button("Run WisRule Analysis"):
        st.session_state.run_analysis = True

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
            st.warning("No rules meet the support and confidence thresholds.")
        else:
            rule_data = []
            for antecedent, negation, consequent, confidence, rule_type, utility in rules:
                rule_data.append({
                    "Antecedent": ", ".join(set(antecedent)),
                    "Consequent": f"{negation}{', '.join(set(consequent))}",
                    "Confidence": f"{confidence:.2f}",
                    "Rule Type": rule_type,
                    "Utility": f"{utility:.2f}"
                })

            rule_df = pd.DataFrame(rule_data)

            st.header("WisRule Results")
            st.dataframe(rule_df)

            st.download_button(
                label="Download Rules as CSV",
                data=rule_df.to_csv(index=False).encode('utf-8'),
                file_name="wisrule_results.csv",
                mime='text/csv'
            )

            st.header("Rule Type Distribution")
            st.bar_chart(rule_df["Rule Type"].value_counts())

            st.header("Confidence Levels by Rule Type")
            rule_df["Confidence"] = pd.to_numeric(rule_df["Confidence"])
            confidence_by_type = rule_df.groupby("Rule Type")["Confidence"].mean().reset_index()
            st.bar_chart(confidence_by_type.set_index("Rule Type"))

            st.subheader("Top 10 Rule Confidence")
            chart_data = pd.DataFrame({
                "Rule": [f"{row['Antecedent']} → {row['Consequent']}" for _, row in rule_df.iterrows()],
                "Confidence": rule_df["Confidence"],
                "Type": rule_df["Rule Type"],
                "Utility": rule_df["Utility"]
            }).head(10)
            st.bar_chart(chart_data.set_index("Rule")[["Confidence", "Utility"]])
