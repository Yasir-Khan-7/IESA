import mysql.connector
import pandas as pd
import streamlit as st
import altair as alt
import matplotlib.pyplot as plt
import numpy as np
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

def create_animated_bar(data, x_col, y_col, title, color_sequence=None):
    """Create an animated bar chart with plotly"""
    if color_sequence is None:
        color_sequence = px.colors.qualitative.Plotly
    
    fig = px.bar(
        data, 
        x=x_col, 
        y=y_col, 
        title=title,
        color_discrete_sequence=[color_sequence],
        animation_frame=x_col,
        range_y=[0, data[y_col].max() * 1.1]
    )
    
    fig.update_layout(
        autosize=True,
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor='rgba(230, 230, 230, 0.5)'),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Segoe UI, Arial", size=12),
        margin=dict(l=40, r=20, t=60, b=40),
        title=dict(
            font=dict(size=18, family="Segoe UI, Arial", color="#444"),
            x=0.5,
            xanchor='center'
        ),
    )
    
    return fig

def create_gauge_chart(value, title, min_val=0, max_val=100, color_threshold=None):
    """Create a gauge chart showing a percentage value"""
    if color_threshold is None:
        color_threshold = [[0, "red"], [0.5, "yellow"], [0.8, "green"]]
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        domain=dict(x=[0, 1], y=[0, 1]),
        title=dict(text=title, font=dict(size=16)),
        gauge=dict(
            axis=dict(range=[min_val, max_val]),
            bar=dict(color="#0072B2"),
            bgcolor="white",
            borderwidth=2,
            bordercolor="gray",
            steps=[
                dict(range=[min_val, max_val*0.5], color="#FFD6D6"),
                dict(range=[max_val*0.5, max_val*0.8], color="#FFFFB3"),
                dict(range=[max_val*0.8, max_val], color="#D3F5D3")
            ],
            threshold=dict(
                line=dict(color="red", width=4),
                thickness=0.75,
                value=value
            )
        )
    ))
    
    fig.update_layout(
        height=250,
        margin=dict(l=30, r=30, t=50, b=30),
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Segoe UI, Arial")
    )
    
    return fig

def electricty_dashboard():
     # Fetch Annual Electricity Data (First Row Only)
    table_name = "annual_electricity_data"
    electricity_data = fetch_table_data(table_name)

    # Fetch Sector-wise Electricity Consumption Data
    sector_table_name = "electricity_consumption_by_sector_gwh"
    sector_data = fetch_table_data(sector_table_name)

    province_table_name = "province_wise_electricity_consumption_gwh"
    province_data = fetch_table_data(province_table_name)

    if not electricity_data.empty and not sector_data.empty:
        electricity_columns = electricity_data.columns.tolist()
        sector_columns = sector_data.columns.tolist()
        province_columns = province_data.columns.tolist()

        # Add dashboard-specific styling
        st.markdown("""
        <style>
        .chart-container {
            border-radius: 10px;
            background-color: rgba(255, 255, 255, 0.95);
            padding: 15px;
            margin-bottom: 25px;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
            border: 1px solid rgba(0, 0, 0, 0.05);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }
        .chart-container:hover {
            transform: translateY(-5px);
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
        }
        .section-header {
            background: linear-gradient(90deg, #4682B4, #5F9EA0);
            color: white;
            padding: 15px 20px;
            border-radius: 8px;
            margin: 25px 0 20px 0;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            position: relative;
            overflow: hidden;
        }
        .section-header::after {
            content: "";
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
            animation: shine 3s infinite;
        }
        @keyframes shine {
            to {
                left: 100%;
            }
        }
        .line-chart-container {
            border-radius: 10px;
            background-color: rgba(255, 255, 255, 0.95);
            padding: 20px;
            margin: 25px 0;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
        }
        .chart-title {
            font-size: 1.2rem;
            font-weight: 600;
            color: #444;
            margin-bottom: 15px;
            text-align: center;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        .metric-row {
            background-color: rgba(255, 255, 255, 0.95);
            padding: 15px;
            border-radius: 10px;
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
            margin-bottom: 20px;
            display: flex;
            flex-direction: row;
            justify-content: space-around;
        }
        .metric-card {
            background: linear-gradient(135deg, #f8f9fa, #e9ecef);
            padding: 15px;
            border-radius: 8px;
            text-align: center;
            box-shadow: 0 2px 5px rgba(0,0,0,0.08);
            flex: 1;
            margin: 0 10px;
            transition: transform 0.2s ease;
        }
        .metric-card:hover {
            transform: translateY(-3px);
        }
        .metric-value {
            font-size: 1.8rem;
            font-weight: 700;
            color: #0b3d91;
            margin: 10px 0;
        }
        .metric-label {
            font-size: 1rem;
            color: #555;
        }
        .viz-tabs {
            margin-bottom: 20px;
        }
        /* Custom scrollbar */
        ::-webkit-scrollbar {
            width: 10px;
            height: 10px;
        }
        ::-webkit-scrollbar-track {
            background: #f1f1f1;
            border-radius: 10px;
        }
        ::-webkit-scrollbar-thumb {
            background: #4682B4;
            border-radius: 10px;
        }
        ::-webkit-scrollbar-thumb:hover {
            background: #5F9EA0;
        }
        </style>
        """, unsafe_allow_html=True)

        # Main Electricity Metrics Section
        st.markdown("<div class='section-header'><h2 style='margin:0;'>⚡ Electricity Overview</h2></div>", unsafe_allow_html=True)
        
        # Key metrics in a dedicated row
        if len(electricity_columns) > 4:
            # Get the most recent year's data
            latest_year = electricity_data[electricity_columns[0]].iloc[-1]
            latest_data = electricity_data[electricity_data[electricity_columns[0]] == latest_year]
            
            # Calculate some derived metrics
            installed_capacity = latest_data[electricity_columns[1]].values[0]
            generation = latest_data[electricity_columns[2]].values[0]
            imports = latest_data[electricity_columns[3]].values[0]
            consumption = latest_data[electricity_columns[4]].values[0]
            
            # Calculate utilization rate
            utilization_rate = (generation / installed_capacity * 100) if installed_capacity > 0 else 0
            import_percentage = (imports / (generation + imports) * 100) if (generation + imports) > 0 else 0
            consumption_rate = (consumption / (generation + imports) * 100) if (generation + imports) > 0 else 0
            
            # Display key metrics
            st.markdown("<div class='metric-row'>", unsafe_allow_html=True)
            
            # Metric 1: Utilization Rate
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Capacity Utilization</div>
                <div class="metric-value">{utilization_rate:.1f}%</div>
                <div>of installed capacity</div>
            </div>
            """, unsafe_allow_html=True)
            
            # Metric 2: Import Percentage
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Import Dependency</div>
                <div class="metric-value">{import_percentage:.1f}%</div>
                <div>of total electricity</div>
            </div>
            """, unsafe_allow_html=True)
            
            # Metric 3: Consumption Rate
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Consumption Rate</div>
                <div class="metric-value">{consumption_rate:.1f}%</div>
                <div>of available electricity</div>
            </div>
            """, unsafe_allow_html=True)
            
            # Metric 4: Year
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Reporting Period</div>
                <div class="metric-value">{latest_year}</div>
                <div>latest data year</div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("</div>", unsafe_allow_html=True)

        # Main charts
        st.markdown("<div class='chart-container'>", unsafe_allow_html=True)

        # First Row - 3 charts per row
        col1, col2, col3 = st.columns(3)

        with col1:
            if len(electricity_columns) > 1:
                fig = create_gauge_chart(utilization_rate, "Capacity Utilization Rate (%)")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("Missing Installed Capacity Data")

        with col2:
            if len(electricity_columns) > 2:
                chart2 = alt.Chart(electricity_data).mark_bar(color="#2E8B57").encode(
                    x=alt.X(electricity_columns[0], title=electricity_columns[0]),
                    y=alt.Y(electricity_columns[2], title=electricity_columns[2]),
                    tooltip=[
                        alt.Tooltip(electricity_columns[0], title='Year'),
                        alt.Tooltip(electricity_columns[2], title='Generation (GWh)', format=',.1f')
                    ]
                ).properties(title="Electricity Generation")
                
                # Add trend line
                trend_line = alt.Chart(electricity_data).mark_line(color='red', strokeDash=[5,5]).encode(
                    x=electricity_columns[0],
                    y=f'mean({electricity_columns[2]})'
                )
                
                final_chart = (chart2 + trend_line).interactive()
                st.altair_chart(final_chart, use_container_width=True)
            else:
                st.warning("Missing Electricity Generation Data")

        with col3:
            if len(electricity_columns) > 3:
                chart3 = alt.Chart(electricity_data).mark_area(color="#CD5C5C", opacity=0.7).encode(
                    x=alt.X(electricity_columns[0], title=electricity_columns[0]),
                    y=alt.Y(electricity_columns[3], title=electricity_columns[3]),
                    tooltip=[
                        alt.Tooltip(electricity_columns[0], title='Year'),
                        alt.Tooltip(electricity_columns[3], title='Import (GWh)', format=',.1f')
                    ]
                ).properties(title="Electricity Import")
                st.altair_chart(chart3.interactive(), use_container_width=True)
            else:
                st.warning("Missing Electricity Import Data")

        # Second Row - remaining chart
        col1, col2, col3 = st.columns(3)
        with col1:
            if len(electricity_columns) > 4:
                chart4 = alt.Chart(electricity_data).mark_bar(color="#FF8C00").encode(
                    x=alt.X(electricity_columns[0], title=electricity_columns[0]),
                    y=alt.Y(electricity_columns[4], title=electricity_columns[4]),
                    tooltip=[
                        alt.Tooltip(electricity_columns[0], title='Year'),
                        alt.Tooltip(electricity_columns[4], title='Consumption (GWh)', format=',.1f')
                    ]
                ).properties(title="Electricity Consumption")
                st.altair_chart(chart4.interactive(), use_container_width=True)
            else:
                st.warning("Missing Electricity Consumption Data")
                
        with col2:
            # Create a stacked bar chart comparing generation, import and consumption
            if len(electricity_columns) > 4:
                # Prepare data for plotting
                chart_data = electricity_data.copy()
                chart_data = chart_data.rename(columns={
                    electricity_columns[2]: "Generation",
                    electricity_columns[3]: "Import",
                    electricity_columns[4]: "Consumption"
                })
                
                # Create a stacked bar chart
                fig = px.bar(
                    chart_data, 
                    x=electricity_columns[0],
                    y=["Generation", "Import"],
                    title="Energy Supply vs Consumption",
                    barmode="stack",
                    color_discrete_sequence=["#2E8B57", "#CD5C5C"]
                )
                
                # Add consumption as a line
                fig.add_trace(go.Scatter(
                    x=chart_data[electricity_columns[0]], 
                    y=chart_data["Consumption"],
                    mode='lines+markers',
                    name='Consumption',
                    line=dict(color='#FF8C00', width=3)
                ))
                
                fig.update_layout(
                    xaxis_title="Year",
                    yaxis_title="Energy (GWh)",
                    legend_title="Type",
                    yaxis=dict(range=[0, 120000]),
                    height=350,
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    margin=dict(l=40, r=20, t=50, b=40)
                )
                
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("Missing data for comparison chart")
                
        with col3:
            # Create a consumption vs generation pie chart for most recent year
            if len(electricity_columns) > 4:
                latest_data = electricity_data.iloc[-1]  # Get most recent year
                
                fig = go.Figure(data=[go.Pie(
                    labels=['Generation', 'Import', 'Consumption'],
                    values=[
                        latest_data[electricity_columns[2]], 
                        latest_data[electricity_columns[3]], 
                        latest_data[electricity_columns[4]]
                    ],
                    hole=.3,
                    marker_colors=["#2E8B57", "#CD5C5C", "#FF8C00"]
                )])
                
                fig.update_layout(
                    title_text=f"Energy Balance ({latest_data[electricity_columns[0]]})",
                    height=350,
                    paper_bgcolor="rgba(0,0,0,0)",
                    margin=dict(l=20, r=20, t=50, b=20)
                )
                
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("Missing data for pie chart")
                
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Line chart in its own full row
        st.markdown("<div class='line-chart-container'>", unsafe_allow_html=True)
        st.markdown("<h3 class='chart-title'>Electricity Trends Over Time</h3>", unsafe_allow_html=True)
        
        # Create an interactive line chart with Plotly
        if len(electricity_columns) > 1:
            fig = px.line(
                electricity_data, 
                x=electricity_columns[0], 
                y=[electricity_columns[1], electricity_columns[2], electricity_columns[3], electricity_columns[4]],
                title="Electricity Metrics Trend Analysis",
                labels={
                    electricity_columns[0]: "Year",
                    "value": "Energy (GWh)",
                    "variable": "Metric"
                },
                color_discrete_sequence=["#4682B4", "#2E8B57", "#CD5C5C", "#FF8C00"]
            )
            
            # Improve the layout
            fig.update_layout(
                xaxis_title="Year",
                yaxis_title="Energy (GWh)",
                legend_title="Energy Metric",
                hovermode="x unified",
                height=450,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)"
            )
            
            # Add grid lines
            fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(230, 230, 230, 0.8)')
            fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(230, 230, 230, 0.8)')
            
            st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Sector-wise Consumption Section
        st.markdown("<div class='section-header'><h2 style='margin:0;'>🏢 Sector-wise Electricity Consumption</h2></div>", unsafe_allow_html=True)
        st.markdown("<div class='chart-container'>", unsafe_allow_html=True)

        # First row of sector charts - 3 per row
        sec_col1, sec_col2, sec_col3 = st.columns(3)

        with sec_col1:
            if len(sector_columns) > 1:
                chart_data = sector_data.copy()
                chart_data = chart_data.rename(columns={
                    sector_columns[0]: "Year",
                    sector_columns[1]: "Residential"
                })
                
                fig = px.line(
                    chart_data, 
                    x="Year", 
                    y="Residential",
                    title="Residential Consumption",
                    markers=True
                )
                
                fig.update_traces(line=dict(color="#8A2BE2", width=3))
                fig.update_layout(
                    height=300,
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    margin=dict(l=40, r=20, t=50, b=40)
                )
                
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("Missing Residential Data")

        with sec_col2:
            if len(sector_columns) > 2:
                chart_data = sector_data.copy()
                chart_data = chart_data.rename(columns={
                    sector_columns[0]: "Year",
                    sector_columns[2]: "Commercial"
                })
                
                fig = px.line(
                    chart_data, 
                    x="Year", 
                    y="Commercial",
                    title="Commercial Consumption",
                    markers=True
                )
                
                fig.update_traces(line=dict(color="#1E90FF", width=3))
                fig.update_layout(
                    height=300,
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    margin=dict(l=40, r=20, t=50, b=40)
                )
                
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("Missing Commercial Data")

        with sec_col3:
            if len(sector_columns) > 3:
                chart_data = sector_data.copy()
                chart_data = chart_data.rename(columns={
                    sector_columns[0]: "Year",
                    sector_columns[3]: "Industrial"
                })
                
                fig = px.line(
                    chart_data, 
                    x="Year", 
                    y="Industrial",
                    title="Industrial Consumption",
                    markers=True
                )
                
                fig.update_traces(line=dict(color="#32CD32", width=3))
                fig.update_layout(
                    height=300,
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    margin=dict(l=40, r=20, t=50, b=40)
                )
                
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("Missing Industrial Data")

        # Second row of sector charts - 3 per row
        sec_col1, sec_col2, sec_col3 = st.columns(3)
        
        with sec_col1:
            if len(sector_columns) > 4:
                sec_chart4 = alt.Chart(sector_data).mark_area(color="#008080", opacity=0.7).encode(
                    x=alt.X(sector_columns[0], title=sector_columns[0]),
                    y=alt.Y(sector_columns[4], title=sector_columns[4]),
                    tooltip=[sector_columns[0], sector_columns[4]]
                ).properties(title="Agricultural Consumption")
                st.altair_chart(sec_chart4.interactive(), use_container_width=True)
            else:
                st.warning("Missing Agricultural Data")

        with sec_col2:
            if len(sector_columns) > 5:
                sec_chart5 = alt.Chart(sector_data).mark_area(color="#9370DB", opacity=0.7).encode(
                    x=alt.X(sector_columns[0], title=sector_columns[0]),
                    y=alt.Y(sector_columns[5], title=sector_columns[5]),
                    tooltip=[sector_columns[0], sector_columns[5]]
                ).properties(title="Street Light Consumption")
                st.altair_chart(sec_chart5.interactive(), use_container_width=True)
            else:
                st.warning("Missing Street Light Data")

        with sec_col3:
            if len(sector_columns) > 7:
                sec_chart7 = alt.Chart(sector_data).mark_area(color="#20B2AA", opacity=0.7).encode(
                    x=alt.X(sector_columns[0], title=sector_columns[0]),
                    y=alt.Y(sector_columns[7], title=sector_columns[7]),
                    tooltip=[sector_columns[0], sector_columns[7]]
                ).properties(title="Bulk Supply Consumption")
                st.altair_chart(sec_chart7.interactive(), use_container_width=True)
            else:
                st.warning("Missing Bulk Supply Data")

        # Third row of sector charts - 3 per row
        sec_col1, sec_col2, sec_col3 = st.columns(3)
        
        with sec_col1:
            if len(sector_columns) > 8:
                sec_chart8 = alt.Chart(sector_data).mark_area(color="#DAA520", opacity=0.7).encode(
                    x=alt.X(sector_columns[0], title=sector_columns[0]),
                    y=alt.Y(sector_columns[8], title=sector_columns[8]),
                    tooltip=[sector_columns[0], sector_columns[8]]
                ).properties(title="Other Govt Consumption")
                st.altair_chart(sec_chart8.interactive(), use_container_width=True)
            else:
                st.warning("Missing Other Govt Data")

        with sec_col2:
            if len(sector_columns) > 9:
                sec_chart9 = alt.Chart(sector_data).mark_area(color="#5F9EA0", opacity=0.7).encode(
                    x=alt.X(sector_columns[0], title=sector_columns[0]),
                    y=alt.Y(sector_columns[9], title=sector_columns[9]),
                    tooltip=[sector_columns[0], sector_columns[9]]
                ).properties(title="Total Consumption")
                st.altair_chart(sec_chart9.interactive(), use_container_width=True)
            else:
                st.warning("Missing Total Consumption Data")
                
        with sec_col3:
            # Create sector breakdown pie chart for the most recent year
            if len(sector_columns) > 9:
                latest_year = sector_data[sector_columns[0]].iloc[-1]
                latest_data = sector_data[sector_data[sector_columns[0]] == latest_year]
                
                # Extract sector values and names for the latest year
                sectors = [
                    sector_columns[1],  # Residential
                    sector_columns[2],  # Commercial
                    sector_columns[3],  # Industrial
                    sector_columns[4],  # Agricultural
                    sector_columns[5],  # Street Light
                    sector_columns[7],  # Bulk Supply
                    sector_columns[8],  # Other Govt
                ]
                
                sector_values = [latest_data[col].values[0] for col in sectors]
                sector_names = ["Residential", "Commercial", "Industrial", "Agricultural", 
                                "Street Light", "Bulk Supply", "Other Govt"]
                
                # Create the pie chart
                fig = go.Figure(data=[go.Pie(
                    labels=sector_names,
                    values=sector_values,
                    hole=.3,
                    marker_colors=px.colors.qualitative.Set2
                )])
                
                fig.update_layout(
                    title_text=f"Consumption by Sector ({latest_year})",
                    height=350,
                    paper_bgcolor="rgba(0,0,0,0)",
                    margin=dict(l=20, r=20, t=50, b=20)
                )
                
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("Missing data for sector breakdown")
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Line chart for sector data in its own full row
        st.markdown("<div class='line-chart-container'>", unsafe_allow_html=True)
        st.markdown("<h3 class='chart-title'>Sector-wise Consumption Comparison</h3>", unsafe_allow_html=True)
        
        if len(sector_columns) > 1:
            # Create an interactive plotly line chart for all sector data
            fig = px.line(
                sector_data, 
                x=sector_columns[0], 
                y=[sector_columns[1], sector_columns[2], sector_columns[3], sector_columns[4], 
                   sector_columns[5], sector_columns[7], sector_columns[8]],
                title="Sector-wise Electricity Consumption Trends",
                labels={
                    sector_columns[0]: "Year",
                    "value": "Consumption (GWh)",
                    "variable": "Sector"
                },
                color_discrete_sequence=px.colors.qualitative.Plotly
            )
            
            # Improve the layout
            fig.update_layout(
                xaxis_title="Year",
                yaxis_title="Consumption (GWh)",
                legend_title="Sector",
                hovermode="x unified",
                height=450,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)"
            )
            
            # Add grid lines
            fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(230, 230, 230, 0.8)')
            fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(230, 230, 230, 0.8)')
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Also add a stacked area chart to show composition over time
            fig2 = px.area(
                sector_data, 
                x=sector_columns[0], 
                y=[sector_columns[1], sector_columns[2], sector_columns[3], sector_columns[4], 
                   sector_columns[5], sector_columns[7], sector_columns[8]],
                title="Sectoral Composition of Electricity Consumption",
                labels={
                    sector_columns[0]: "Year",
                    "value": "Consumption (GWh)",
                    "variable": "Sector"
                },
                color_discrete_sequence=px.colors.qualitative.Bold
            )
            
            fig2.update_layout(
                xaxis_title="Year",
                yaxis_title="Consumption (GWh)",
                legend_title="Sector",
                hovermode="x unified",
                height=450,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)"
            )
            
            st.plotly_chart(fig2, use_container_width=True)
            
        st.markdown("</div>", unsafe_allow_html=True)
       
        # Province-wise Consumption Section
        st.markdown("<div class='section-header'><h2 style='margin:0;'>🗺️ Province-wise Electricity Consumption</h2></div>", unsafe_allow_html=True)
        st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
        
        # First row of province charts - 3 per row
        prov_col1, prov_col2, prov_col3 = st.columns(3)
        
        with prov_col1:
            if len(province_columns) > 1:
                prov_chart1 = alt.Chart(province_data).mark_bar(color="#4169E1").encode(
                    x=alt.X(province_columns[0], title=province_columns[0]),
                    y=alt.Y(province_columns[1], title=province_columns[1]),
                    tooltip=[province_columns[0], province_columns[1]]
                ).properties(title="Punjab Consumption")
                st.altair_chart(prov_chart1.interactive(), use_container_width=True)
            else:
                st.warning("Missing Punjab Data")

        with prov_col2:
            if len(province_columns) > 2:
                prov_chart2 = alt.Chart(province_data).mark_bar(color="#FF6347").encode(
                    x=alt.X(province_columns[0], title=province_columns[0]),
                    y=alt.Y(province_columns[2], title=province_columns[2]),
                    tooltip=[province_columns[0], province_columns[2]]
                ).properties(title="Sindh Consumption")
                st.altair_chart(prov_chart2.interactive(), use_container_width=True)
            else:
                st.warning("Missing Sindh Data")

        with prov_col3:
            if len(province_columns) > 3:
                prov_chart3 = alt.Chart(province_data).mark_bar(color="#3CB371").encode(
                    x=alt.X(province_columns[0], title=province_columns[0]),
                    y=alt.Y(province_columns[3], title=province_columns[3]),
                    tooltip=[province_columns[0], province_columns[3]]
                ).properties(title="KPK Consumption")
                st.altair_chart(prov_chart3.interactive(), use_container_width=True)
            else:
                st.warning("Missing KPK Data")

        # Second row of province charts - 3 per row
        prov_col1, prov_col2, prov_col3 = st.columns(3)
        
        with prov_col1:
            if len(province_columns) > 4:
                prov_chart4 = alt.Chart(province_data).mark_bar(color="#BA55D3").encode(
                    x=alt.X(province_columns[0], title=province_columns[0]),
                    y=alt.Y(province_columns[4], title=province_columns[4]),
                    tooltip=[province_columns[0], province_columns[4]]
                ).properties(title="Balochistan Consumption")
                st.altair_chart(prov_chart4.interactive(), use_container_width=True)
            else:
                st.warning("Missing Balochistan Data")
                
        with prov_col2:
            if len(province_columns) > 5:
                prov_chart5 = alt.Chart(province_data).mark_bar(color="#6495ED").encode(
                    x=alt.X(province_columns[0], title=province_columns[0]),
                    y=alt.Y(province_columns[5], title=province_columns[5]),
                    tooltip=[province_columns[0], province_columns[5]]
                ).properties(title="AJK Consumption")
                st.altair_chart(prov_chart5.interactive(), use_container_width=True)
            else:
                st.warning("Missing AJK Data")
                
        with prov_col3:
            if len(province_columns) > 6:
                prov_chart6 = alt.Chart(province_data).mark_bar(color="#DC143C").encode(
                    x=alt.X(province_columns[0], title=province_columns[0]),
                    y=alt.Y(province_columns[6], title=province_columns[6]),
                    tooltip=[province_columns[0], province_columns[6]]
                ).properties(title="T&D Losses")
                st.altair_chart(prov_chart6.interactive(), use_container_width=True)
            else:
                st.warning("Missing T&D Losses Data")
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Line chart for province data in its own full row
        st.markdown("<div class='line-chart-container'>", unsafe_allow_html=True)
        st.markdown("<h3 class='chart-title'>Provincial Consumption Comparison</h3>", unsafe_allow_html=True)
        
        # Create an interactive plotly line chart for province data
        if len(province_columns) > 1:
            # Standard line chart
            fig = px.line(
                province_data, 
                x=province_columns[0], 
                y=[province_columns[1], province_columns[2], province_columns[3], 
                   province_columns[4], province_columns[5], province_columns[6]],
                title="Province-wise Electricity Consumption Trends",
                labels={
                    province_columns[0]: "Year",
                    "value": "Consumption (GWh)",
                    "variable": "Province"
                },
                color_discrete_sequence=px.colors.qualitative.Dark24
            )
            
            fig.update_layout(
                xaxis_title="Year",
                yaxis_title="Consumption (GWh)",
                legend_title="Province",
                hovermode="x unified",
                height=450,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)"
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Also add a pie chart for the most recent year
            latest_year = province_data[province_columns[0]].iloc[-1]
            latest_data = province_data[province_data[province_columns[0]] == latest_year]
            
            # Extract province values and names for the latest year
            provinces = [
                province_columns[1],  # Punjab
                province_columns[2],  # Sindh
                province_columns[3],  # KPK
                province_columns[4],  # Balochistan
                province_columns[5],  # AJK
            ]
            
            province_values = [latest_data[col].values[0] for col in provinces]
            province_names = ["Punjab", "Sindh", "KPK", "Balochistan", "AJK"]
            
            # Create the pie chart
            fig2 = px.pie(
                values=province_values,
                names=province_names,
                title=f"Provincial Consumption Distribution ({latest_year})",
                color_discrete_sequence=px.colors.qualitative.Bold
            )
            
            fig2.update_layout(
                height=450,
                paper_bgcolor="rgba(0,0,0,0)",
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            
            # Add percentage annotations
            fig2.update_traces(textposition='inside', textinfo='percent+label')
            
            st.plotly_chart(fig2, use_container_width=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
    else:
          st.warning("No data available for the selected tables.")