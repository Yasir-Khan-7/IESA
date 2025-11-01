import mysql.connector
import pandas as pd
import streamlit as st
import altair as alt

def get_connection():
    return mysql.connector.connect(
        host="localhost",
        port="3306",
        user="root",
        passwd="admin123",
        db="iesa_db"
    )

# Fetch Data from a Table
def fetch_table_data(table_name):
    try:
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
        print(f"Error fetching data from {table_name}: {e}")
        data = pd.DataFrame()
    finally:
        conn.close()
    
    return data

def energy_by_souce_dashboard():

     # Fetch Supplies Data (First Row Only)
    supplies_table_name = "primary_energy_supplies_by_source_toe"
    supplies_data = fetch_table_data(supplies_table_name)

    # Fetch  Consumption Data
    consumption_table_name = "final_energy_consumption_by_source_toe"
    consumption_data = fetch_table_data(consumption_table_name)

    if not supplies_data.empty and not consumption_data.empty:
        supplies_data_columns = supplies_data.columns.tolist()
        consumption_columns = consumption_data.columns.tolist()

        # Add custom styling
        st.markdown("""
        <style>
        .chart-container {
            border-radius: 5px;
            background-color: #f8f9fa;
            padding: 10px;
            margin-bottom: 20px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        .section-header {
            background-color: #2E8B57;
            color: white;
            padding: 10px 15px;
            border-radius: 5px;
            margin-bottom: 20px;
        }
        </style>
        """, unsafe_allow_html=True)

        # Energy Supplies Section
        st.markdown("<div class='section-header'><h2>📊 Energy Supplies By Source</h2></div>", unsafe_allow_html=True)
        st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
        
        # First Row - 3 per row
        col1, col2, col3 = st.columns(3)

        with col1:
            if len(supplies_data_columns) > 1:
                chart1 = alt.Chart(supplies_data).mark_bar(color="#1F77B4").encode(
                    x=alt.X(supplies_data_columns[0], title=supplies_data_columns[0]),
                    y=alt.Y(supplies_data_columns[1], title=supplies_data_columns[1])
                ).properties(title="Oil")
                st.altair_chart(chart1, use_container_width=True)
            else:
                st.warning("Missing Oil Data")

        with col2:
            if len(supplies_data_columns) > 2:
                chart2 = alt.Chart(supplies_data).mark_bar(color="#2CA02C").encode(
                    x=alt.X(supplies_data_columns[0], title=supplies_data_columns[0]),
                    y=alt.Y(supplies_data_columns[2], title=supplies_data_columns[2])
                ).properties(title="Gas")
                st.altair_chart(chart2, use_container_width=True)
            else:
                st.warning("Missing Gas Data")

        with col3:
            if len(supplies_data_columns) > 3:
                chart3 = alt.Chart(supplies_data).mark_bar(color="#D62728").encode(
                    x=alt.X(supplies_data_columns[0], title=supplies_data_columns[0]),
                    y=alt.Y(supplies_data_columns[3], title=supplies_data_columns[3])
                ).properties(title="LNG Import")
                st.altair_chart(chart3, use_container_width=True)
            else:
                st.warning("Missing LNG Import Data")

        # Second Row - 3 per row
        col1, col2, col3 = st.columns(3)

        with col1:
            if len(supplies_data_columns) > 4:
                chart4 = alt.Chart(supplies_data).mark_bar(color="#FF7F0E").encode(
                    x=alt.X(supplies_data_columns[0], title=supplies_data_columns[0]),
                    y=alt.Y(supplies_data_columns[4], title=supplies_data_columns[4])
                ).properties(title="LNG Local Supply")
                st.altair_chart(chart4, use_container_width=True)
            else:
                st.warning("Missing LNG Local Supply Data")

        with col2:
            if len(supplies_data_columns) > 5:
                chart5 = alt.Chart(supplies_data).mark_bar(color="#9467BD").encode(
                    x=alt.X(supplies_data_columns[0], title=supplies_data_columns[0]),
                    y=alt.Y(supplies_data_columns[5], title=supplies_data_columns[5])
                ).properties(title="Coal")
                st.altair_chart(chart5, use_container_width=True)
            else:
                st.warning("Missing Coal Data")

        with col3:
            if len(supplies_data_columns) > 6:
                chart6 = alt.Chart(supplies_data).mark_bar(color="#8C564B").encode(
                    x=alt.X(supplies_data_columns[0], title=supplies_data_columns[0]),
                    y=alt.Y(supplies_data_columns[6], title=supplies_data_columns[6])
                ).properties(title="Hydro Electricity")
                st.altair_chart(chart6, use_container_width=True)
            else:
                st.warning("Missing Hydro Electricity Data")

        # Third Row - 3 per row
        col1, col2, col3 = st.columns(3)

        with col1:
            if len(supplies_data_columns) > 7:
                chart7 = alt.Chart(supplies_data).mark_bar(color="#E377C2").encode(
                    x=alt.X(supplies_data_columns[0], title=supplies_data_columns[0]),
                    y=alt.Y(supplies_data_columns[7], title=supplies_data_columns[7])
                ).properties(title="Nuclear Electricity")
                st.altair_chart(chart7, use_container_width=True)
            else:
                st.warning("Missing Nuclear Electricity Data")

        with col2:
            if len(supplies_data_columns) > 8:
                chart8 = alt.Chart(supplies_data).mark_bar(color="#7F7F7F").encode(
                    x=alt.X(supplies_data_columns[0], title=supplies_data_columns[0]),
                    y=alt.Y(supplies_data_columns[8], title=supplies_data_columns[8])
                ).properties(title="Imported Electricity")
                st.altair_chart(chart8, use_container_width=True)
            else:
                st.warning("Missing Imported Electricity Data")

        with col3:
            if len(supplies_data_columns) > 9:
                chart9 = alt.Chart(supplies_data).mark_bar(color="#BCBD22").encode(
                    x=alt.X(supplies_data_columns[0], title=supplies_data_columns[0]),
                    y=alt.Y(supplies_data_columns[9], title=supplies_data_columns[9])
                ).properties(title="Renewable Electricity")
                st.altair_chart(chart9, use_container_width=True)
            else:
                st.warning("Missing Renewable Electricity Data")

        # Line chart for supplies data
        st.subheader("Energy Supplies Trends")
        st.line_chart(supplies_data, x=supplies_data_columns[0], y=[supplies_data_columns[1], supplies_data_columns[2],supplies_data_columns[3],supplies_data_columns[4],supplies_data_columns[5], supplies_data_columns[6],supplies_data_columns[7],supplies_data_columns[8],supplies_data_columns[9]])
        
        st.markdown("</div>", unsafe_allow_html=True)

        # Energy Consumption Section
        st.markdown("<div class='section-header'><h2>📊 Energy Consumption By Source</h2></div>", unsafe_allow_html=True)
        st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
        
        # First Row of consumption charts - 3 per row
        cons_col1, cons_col2, cons_col3 = st.columns(3)
        
        with cons_col1:
            if len(consumption_columns) > 1:
                cons_chart1 = alt.Chart(consumption_data).mark_bar(color="#17BECF").encode(
                    x=alt.X(consumption_columns[0], title=consumption_columns[0]),
                    y=alt.Y(consumption_columns[1], title=consumption_columns[1])
                ).properties(title="Oil Consumption")
                st.altair_chart(cons_chart1, use_container_width=True)
            else:
                st.warning("Missing Oil Consumption Data")

        with cons_col2:
            if len(consumption_columns) > 2:
                cons_chart2 = alt.Chart(consumption_data).mark_bar(color="#1F77B4").encode(
                    x=alt.X(consumption_columns[0], title=consumption_columns[0]),
                    y=alt.Y(consumption_columns[2], title=consumption_columns[2])
                ).properties(title="Gas Consumption")
                st.altair_chart(cons_chart2, use_container_width=True)
            else:
                st.warning("Missing Gas Consumption Data")

        with cons_col3:
            if len(consumption_columns) > 3:
                cons_chart3 = alt.Chart(consumption_data).mark_bar(color="#2CA02C").encode(
                    x=alt.X(consumption_columns[0], title=consumption_columns[0]),
                    y=alt.Y(consumption_columns[3], title=consumption_columns[3])
                ).properties(title="LPG Consumption")
                st.altair_chart(cons_chart3, use_container_width=True)
            else:
                st.warning("Missing LPG Consumption Data")

        # Second Row of consumption charts - 3 per row
        cons_col1, cons_col2, cons_col3 = st.columns(3)
        
        with cons_col1:
            if len(consumption_columns) > 4:
                cons_chart4 = alt.Chart(consumption_data).mark_bar(color="#D62728").encode(
                    x=alt.X(consumption_columns[0], title=consumption_columns[0]),
                    y=alt.Y(consumption_columns[4], title=consumption_columns[4])
                ).properties(title="Coal Consumption")
                st.altair_chart(cons_chart4, use_container_width=True)
            else:
                st.warning("Missing Coal Consumption Data")
                
        with cons_col2:
            if len(consumption_columns) > 5:
                cons_chart5 = alt.Chart(consumption_data).mark_bar(color="#9467BD").encode(
                    x=alt.X(consumption_columns[0], title=consumption_columns[0]),
                    y=alt.Y(consumption_columns[5], title=consumption_columns[5])
                ).properties(title="Electricity Consumption")
                st.altair_chart(cons_chart5, use_container_width=True)
            else:
                st.warning("Missing Electricity Consumption Data")
                
        with cons_col3:
            if len(consumption_columns) > 6:
                cons_chart6 = alt.Chart(consumption_data).mark_bar(color="#8C564B").encode(
                    x=alt.X(consumption_columns[0], title=consumption_columns[0]),
                    y=alt.Y(consumption_columns[6], title=consumption_columns[6])
                ).properties(title="Total Consumption")
                st.altair_chart(cons_chart6, use_container_width=True)
            else:
                st.warning("Missing Total Consumption Data")

        # Line chart for consumption data
        st.subheader("Energy Consumption Trends")
        st.line_chart(consumption_data, x=consumption_columns[0], y=[consumption_columns[1], consumption_columns[2],consumption_columns[3],consumption_columns[4],consumption_columns[5],consumption_columns[6]])
        
        st.markdown("</div>", unsafe_allow_html=True)
    else:
          st.warning("No data available for the selected tables.")