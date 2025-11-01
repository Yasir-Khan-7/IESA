import mysql.connector
import pandas as pd
import streamlit as st
import altair as alt
import plotly.express as px
import plotly.graph_objects as go

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

def total_energy():
    # Add custom styling for the dashboard
    st.markdown("""
    <style>
    .dashboard-title {
        background-color: #106466;
        color: white;
        padding: 15px 20px;
        border-radius: 10px;
        margin-bottom: 25px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        text-align: center;
    }
    .chart-section {
        background-color: white;
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    .chart-section:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.12);
    }
    .section-header {
        background-color: #f8f9fa;
        padding: 10px 15px;
        border-radius: 5px;
        margin-bottom: 15px;
        border-left: 4px solid #106466;
        font-weight: bold;
        color: #333;
    }
    .metric-row {
        display: flex;
        flex-wrap: wrap;
        gap: 15px;
        margin-bottom: 20px;
    }
    .metric-card {
        background-color: #f8f9fa;
        border-radius: 8px;
        padding: 15px;
        text-align: center;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        flex: 1;
    }
    .metric-value {
        font-size: 1.8rem;
        font-weight: 700;
        color: #106466;
        margin: 10px 0;
    }
    .metric-label {
        font-size: 0.9rem;
        color: #555;
    }
    </style>
    """, unsafe_allow_html=True)

    table_name = "energy_supply_and_consumption_analysis"
    energy_data = fetch_table_data(table_name)

    if not energy_data.empty:
        energy_columns = energy_data.columns.tolist()
        
        # Dashboard title
        st.markdown("<div class='dashboard-title'><h1>⚡ Total Energy Dashboard</h1></div>", unsafe_allow_html=True)

        # Key Metrics Section
        st.markdown("<div class='section-header'>Key Energy Metrics</div>", unsafe_allow_html=True)
        
        # Calculate key metrics from most recent year
        latest_year_data = energy_data.iloc[-1]
        
        # Display metrics in a row
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            if len(energy_columns) > 1:
                supply = latest_year_data[energy_columns[1]]
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">Total Energy Supply</div>
                    <div class="metric-value">{supply:.2f} MTOE</div>
                    <div>Latest available data</div>
                </div>
                """, unsafe_allow_html=True)
        
        with col2:
            if len(energy_columns) > 2:
                consumption = latest_year_data[energy_columns[2]]
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">Total Consumption</div>
                    <div class="metric-value">{consumption:.2f} MTOE</div>
                    <div>Latest available data</div>
                </div>
                """, unsafe_allow_html=True)
        
        with col3:
            if len(energy_columns) > 3:
                gap = latest_year_data[energy_columns[3]]
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">Supply-Consumption Gap</div>
                    <div class="metric-value">{gap:.2f} MTOE</div>
                    <div>Latest available data</div>
                </div>
                """, unsafe_allow_html=True)
        
        with col4:
            if len(energy_columns) > 8:
                losses = latest_year_data[energy_columns[8]]
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">Total System Losses</div>
                    <div class="metric-value">{losses:.2f} MTOE</div>
                    <div>Latest available data</div>
                </div>
                """, unsafe_allow_html=True)
        
        # Energy Supply and Consumption Section
        st.markdown("<div class='chart-section'>", unsafe_allow_html=True)
        st.markdown("<div class='section-header'>Energy Supply & Consumption Analysis</div>", unsafe_allow_html=True)
        
        # Create a plotly line chart for supply vs consumption
        fig = go.Figure()
        
        # Add supply line
        fig.add_trace(go.Scatter(
            x=energy_data[energy_columns[0]], 
            y=energy_data[energy_columns[1]],
            mode='lines+markers',
            name='Total Energy Supply',
            line=dict(color='#1f77b4', width=3),  # Plain blue color
            marker=dict(size=8)
        ))
        
        # Add consumption line
        fig.add_trace(go.Scatter(
            x=energy_data[energy_columns[0]], 
            y=energy_data[energy_columns[2]],
            mode='lines+markers',
            name='Total Energy Consumption',
            line=dict(color='#ff7f0e', width=3),  # Plain orange color
            marker=dict(size=8)
        ))
        
        # Add gap line if available
        if len(energy_columns) > 3:
            fig.add_trace(go.Scatter(
                x=energy_data[energy_columns[0]], 
                y=energy_data[energy_columns[3]],
                mode='lines+markers',
                name='Supply-Consumption Gap',
                line=dict(color='#2ca02c', width=3, dash='dot'),  # Plain green color with dash
                marker=dict(size=8)
            ))
        
        # Update layout
        fig.update_layout(
            title="Energy Supply vs. Consumption Trend",
            xaxis_title="Year",
            yaxis_title="Energy (MTOE)",
            legend_title="Energy Metrics",
            hovermode="x unified",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)"
        )
        
        # Add grid lines
        fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(230, 230, 230, 0.8)')
        fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(230, 230, 230, 0.8)')
        
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Energy Losses Analysis Section
        st.markdown("<div class='chart-section'>", unsafe_allow_html=True)
        st.markdown("<div class='section-header'>Energy Losses Analysis</div>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Bar chart for transformation losses
            if len(energy_columns) > 4:
                chart1 = alt.Chart(energy_data).mark_bar(color="#d62728").encode(  # Plain red color
                    x=alt.X(energy_columns[0], title="Year"),
                    y=alt.Y(energy_columns[4], title="Losses (TTOE)"),
                    tooltip=[energy_columns[0], energy_columns[4]]
                ).properties(
                    title="Transformation Losses Over Time",
                    height=300
                )
                st.altair_chart(chart1, use_container_width=True)
            else:
                st.warning("Missing Transformation Losses Data")
        
        with col2:
            # Bar chart for T&D losses
            if len(energy_columns) > 6:
                chart2 = alt.Chart(energy_data).mark_bar(color="#9467bd").encode(  # Plain purple color
                    x=alt.X(energy_columns[0], title="Year"),
                    y=alt.Y(energy_columns[6], title="Losses (TTOE)"),
                    tooltip=[energy_columns[0], energy_columns[6]]
                ).properties(
                    title="T&D Losses Over Time",
                    height=300
                )
                st.altair_chart(chart2, use_container_width=True)
            else:
                st.warning("Missing T&D Losses Data")
        
        # Create a stacked bar chart for different types of losses
        if len(energy_columns) > 8:
            loss_data = energy_data.copy()
            
            # Rename columns for better display
            loss_data = loss_data.rename(columns={
                energy_columns[4]: "Transformation Losses",
                energy_columns[6]: "T&D Losses"
            })
            
            fig = px.bar(
                loss_data, 
                x=energy_columns[0],
                y=["Transformation Losses", "T&D Losses"],
                title="Breakdown of Energy Losses",
                labels={
                    energy_columns[0]: "Year",
                    "value": "Losses (TTOE)",
                    "variable": "Loss Type"
                },
                color_discrete_map={  # Plain colors
                    "Transformation Losses": "#d62728",
                    "T&D Losses": "#9467bd"
                }
            )
            
            fig.update_layout(
                barmode='stack',
                xaxis_title="Year",
                yaxis_title="Energy Losses (TTOE)",
                legend_title="Loss Type",
                height=400,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)"
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Add a pie chart for the latest year's loss breakdown
            latest_year = energy_data[energy_columns[0]].iloc[-1]
            latest_losses = energy_data[energy_data[energy_columns[0]] == latest_year]
            
            if not latest_losses.empty:
                loss_values = [
                    latest_losses[energy_columns[4]].values[0],  # Transformation losses
                    latest_losses[energy_columns[6]].values[0]   # T&D losses
                ]
                
                fig = px.pie(
                    values=loss_values,
                    names=["Transformation Losses", "T&D Losses"],
                    title=f"Energy Loss Distribution ({latest_year})",
                    color_discrete_sequence=["#d62728", "#9467bd"]  # Plain colors
                )
                
                fig.update_traces(
                    textposition='inside',
                    textinfo='percent+label'
                )
                
                fig.update_layout(
                    height=350,
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=-0.15,
                        xanchor="center",
                        x=0.5
                    )
                )
                
                st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Energy Utilization Section
        st.markdown("<div class='chart-section'>", unsafe_allow_html=True)
        st.markdown("<div class='section-header'>Energy Utilization Analysis</div>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Bar chart for Energy used in Transformation
            if len(energy_columns) > 9:
                chart3 = alt.Chart(energy_data).mark_bar(color="#17becf").encode(  # Plain cyan color
                    x=alt.X(energy_columns[0], title="Year"),
                    y=alt.Y(energy_columns[9], title=energy_columns[9]),
                    tooltip=[energy_columns[0], energy_columns[9]]
                ).properties(
                    title="Energy Used in Transformation",
                    height=300
                )
                st.altair_chart(chart3, use_container_width=True)
            else:
                st.warning("Missing Energy Used in Transformation Data")
        
        with col2:
            # Bar chart for Energy Sector Own Use
            if len(energy_columns) > 10:
                chart4 = alt.Chart(energy_data).mark_bar(color="#8c564b").encode(  # Plain brown color
                    x=alt.X(energy_columns[0], title="Year"),
                    y=alt.Y(energy_columns[10], title=energy_columns[10]),
                    tooltip=[energy_columns[0], energy_columns[10]]
                ).properties(
                    title="Energy Sector Own Use",
                    height=300
                )
                st.altair_chart(chart4, use_container_width=True)
            else:
                st.warning("Missing Energy Sector Own Use Data")
        
        # Energy Efficiency and Utilization Metrics
        if len(energy_columns) > 10:
            # Calculate some efficiency metrics
            energy_data["Utilization_Ratio"] = (
                energy_data[energy_columns[2]] / energy_data[energy_columns[1]] * 100
            ).round(2)
            
            # Line chart for efficiency trend
            fig = px.line(
                energy_data,
                x=energy_columns[0],
                y="Utilization_Ratio",
                title="Energy Utilization Ratio Over Time (Higher is Better)",
                labels={
                    energy_columns[0]: "Year", 
                    "Utilization_Ratio": "Utilization Ratio (%)"
                },
                markers=True
            )
            
            fig.update_traces(line=dict(color="#2ca02c", width=3))  # Plain green color
            
            fig.update_layout(
                xaxis_title="Year",
                yaxis_title="Utilization Ratio (%)",
                height=350,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)"
            )
            
            # Add grid lines
            fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(230, 230, 230, 0.8)')
            fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(230, 230, 230, 0.8)')
            
            st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Data Table Section
        with st.expander("View Raw Data"):
            st.dataframe(energy_data.style.highlight_max(axis=0))
            
            # Download button for the data
            csv = energy_data.to_csv(index=False)
            st.download_button(
                label="Download Data as CSV",
                data=csv,
                file_name="energy_data.csv",
                mime="text/csv"
            )

    else:
        st.warning("No data available for energy supply and consumption analysis.")
