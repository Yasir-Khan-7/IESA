import mysql.connector
import pandas as pd
import streamlit as st
import altair as alt
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Function to get a database connection
def get_connection():
    return mysql.connector.connect(
        host="localhost",
        port="3306",
        user="root",
        passwd="admin123",
        db="iesa_db"
    )

def circular_progress(label, value, max_value, color):
    """Create a circular progress indicator with custom styling"""
    # Calculate the percentage
    percent = min(max(value, 0), max_value) / max_value
    
    # HTML for the circular progress
    html = f"""
    <div class="circular-progress-container">
        <div class="circular-progress" style="background: conic-gradient({color} {percent * 360}deg, #f3f3f3 0deg);">
            <div class="circular-progress-inner">
                <div class="circular-progress-value">{value:.1f}%</div>
            </div>
        </div>
        <div class="circular-progress-label">{label}</div>
    </div>
    """
    
    st.markdown(html, unsafe_allow_html=True)

# Fetch data from a table
def fetch_table_data(table_name):
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            query = f"SELECT * FROM `{table_name}`"
            cursor.execute(query)
            rows = cursor.fetchall()
            if not rows:
                return pd.DataFrame()
            columns = [desc[0] for desc in cursor.description]
            data = pd.DataFrame(rows, columns=columns)

            # Convert numeric columns to float
            for col in data.columns[1:]:
                data[col] = pd.to_numeric(data[col], errors="coerce")
            data.fillna(0, inplace=True)
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        data = pd.DataFrame()
    finally:
        conn.close()

    return data

# Create a gauge chart for plotly visualization
def create_gauge_chart(value, title, min_val=0, max_val=100, threshold_values=None):
    """Create an attractive gauge chart with plotly"""
    if threshold_values is None:
        threshold_values = {
            'low': {'color': '#FF4136', 'range': [min_val, max_val * 0.3]},
            'medium': {'color': '#FFDC00', 'range': [max_val * 0.3, max_val * 0.7]},
            'high': {'color': '#2ECC40', 'range': [max_val * 0.7, max_val]}
        }
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=value,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': title, 'font': {'size': 24}},
        delta={'reference': max_val/2, 'increasing': {'color': "#2ECC40"}},
        gauge={
            'axis': {'range': [min_val, max_val], 'tickwidth': 1, 'tickcolor': "darkblue"},
            'bar': {'color': "#19647E"},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': threshold_values['low']['range'], 'color': threshold_values['low']['color']},
                {'range': threshold_values['medium']['range'], 'color': threshold_values['medium']['color']},
                {'range': threshold_values['high']['range'], 'color': threshold_values['high']['color']}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': value
            }
        }
    ))
    
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        height=250,
        margin=dict(l=25, r=25, t=50, b=25)
    )
    
    return fig

# Gas Dashboard for Business Intelligence
def gas_dashboard():
    st.title("📊 Natural Gas BI Dashboard")
    
    # Add custom styling
    st.markdown("""
    <style>
    /* General dashboard styling */
    .chart-container {
        border-radius: 10px;
        background-color: rgba(255, 255, 255, 0.95);
        padding: 20px;
        margin-bottom: 25px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    .chart-container:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
    }
    
    /* Section headers */
    .section-header {
        background: linear-gradient(90deg, #106466, #329D9C);
        color: white;
        padding: 15px 20px;
        border-radius: 8px;
        margin: 25px 0 20px 0;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        position: relative;
        overflow: hidden;
    }
    
    /* Animated accent for section headers */
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
    
    /* Metric containers */
    .metric-container {
        background-color: rgba(255, 255, 255, 0.95);
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
        margin-bottom: 20px;
    }
    
    /* Metric cards */
    .metric-row {
        display: flex;
        flex-wrap: wrap;
        justify-content: space-between;
        gap: 15px;
        margin-bottom: 20px;
    }
    .metric-card {
        background: linear-gradient(135deg, #f8f9fa, #e9ecef);
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        flex: 1;
        min-width: 200px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 15px rgba(0, 0, 0, 0.1);
    }
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        margin: 10px 0;
        color: #106466;
    }
    .metric-label {
        color: #555;
        font-size: 1rem;
        font-weight: 500;
    }
    .metric-trend {
        font-size: 0.9rem;
        margin-top: 5px;
    }
    .metric-trend.positive {
        color: #2ECC40;
    }
    .metric-trend.negative {
        color: #FF4136;
    }
    
    /* Circular progress */
    .circular-progress-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        margin: 20px 0;
    }
    .circular-progress {
        width: 150px;
        height: 150px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        background: #f3f3f3;
        box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
    }
    .circular-progress-inner {
        width: 120px;
        height: 120px;
        border-radius: 50%;
        background: white;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    .circular-progress-value {
        font-size: 1.5rem;
        font-weight: bold;
        color: #333;
    }
    .circular-progress-label {
        margin-top: 10px;
        font-size: 1rem;
        color: #555;
        font-weight: 500;
    }
    
    /* Custom divider */
    .custom-divider {
        height: 3px;
        background: linear-gradient(90deg, rgba(16,100,102,0.2), rgba(16,100,102,0.8), rgba(16,100,102,0.2));
        margin: 30px 0;
        border-radius: 2px;
    }
    
    /* Line chart container */
    .line-chart-container {
        background-color: rgba(255, 255, 255, 0.95);
        padding: 20px;
        border-radius: 10px;
        margin: 25px 0;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
    }
    
    /* Chart title */
    .chart-title {
        font-size: 1.2rem;
        font-weight: 600;
        color: #333;
        margin-bottom: 15px;
        text-align: center;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
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
        background: #106466;
        border-radius: 10px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: #329D9C;
    }
    </style>
    """, unsafe_allow_html=True)
    
    table_name = "natural_gas_production_and_consumption"
    gas_data = fetch_table_data(table_name)

    if not gas_data.empty:
        gas_columns = gas_data.columns.tolist()
        
        # No longer filtering by year - using all data
        filtered_data = gas_data

        # Ensure we have all required columns for visualization
        if len(gas_columns) < 5:
            st.error("Insufficient data columns for comprehensive visualization.")
            return

        # Section Header for Key Metrics
        st.markdown("<div class='section-header'><h2>📈 Key Performance Indicators</h2></div>", unsafe_allow_html=True)
        
        # Calculate metrics
        total_production = filtered_data[gas_columns[1]].sum()
        total_consumption = filtered_data[gas_columns[2]].sum()
        consumption_ratio = (total_consumption / total_production * 100) if total_production > 0 else 0
        
        latest_year = filtered_data[gas_columns[0]].max()
        latest_data = filtered_data[filtered_data[gas_columns[0]] == latest_year]
        
        current_production = latest_data[gas_columns[1]].values[0]
        current_consumption = latest_data[gas_columns[2]].values[0]
        current_revenue = latest_data[gas_columns[3]].values[0]
        current_import = latest_data[gas_columns[4]].values[0]
        
        # Get previous year's data for trend calculation
        previous_year = filtered_data[gas_columns[0]].iloc[-2] if len(filtered_data) > 1 else None
        previous_data = filtered_data[filtered_data[gas_columns[0]] == previous_year] if previous_year else None
        
        # Calculate trends
        production_trend = 0
        consumption_trend = 0
        if previous_data is not None and not previous_data.empty:
            prev_production = previous_data[gas_columns[1]].values[0]
            prev_consumption = previous_data[gas_columns[2]].values[0]
            production_trend = ((current_production - prev_production) / prev_production * 100) if prev_production > 0 else 0
            consumption_trend = ((current_consumption - prev_consumption) / prev_consumption * 100) if prev_consumption > 0 else 0
        
        # Display top KPI metrics in attractive cards
        st.markdown("<div class='metric-row'>", unsafe_allow_html=True)
        
        # Production Metric
        trend_class = "positive" if production_trend >= 0 else "negative"
        trend_icon = "↑" if production_trend >= 0 else "↓"
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Gas Production</div>
            <div class="metric-value">{current_production:,.2f} Bcf</div>
            <div class="metric-trend {trend_class}">{trend_icon} {abs(production_trend):.1f}% from previous year</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Consumption Metric
        trend_class = "positive" if consumption_trend <= 0 else "negative"  # Lower consumption is positive
        trend_icon = "↓" if consumption_trend <= 0 else "↑"
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Gas Consumption</div>
            <div class="metric-value">{current_consumption:,.2f} Bcf</div>
            <div class="metric-trend {trend_class}">{trend_icon} {abs(consumption_trend):.1f}% from previous year</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Consumption Ratio
        surplus = current_production - current_consumption
        status = "Surplus" if surplus > 0 else "Deficit"
        status_class = "positive" if surplus > 0 else "negative"
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Natural Gas {status}</div>
            <div class="metric-value">{abs(surplus):,.2f} Bcf</div>
            <div class="metric-trend {status_class}">{abs(100-consumption_ratio):.1f}% {status.lower()}</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Revenue Metric 
        revenue_to_import_ratio = (current_revenue / current_import * 100) if current_import > 0 else 0
        profit = current_revenue - current_import
        fin_status = "Profit" if profit > 0 else "Loss"
        fin_class = "positive" if profit > 0 else "negative"
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Financial {fin_status}</div>
            <div class="metric-value">{abs(profit):,.2f} PKR B</div>
            <div class="metric-trend {fin_class}">{revenue_to_import_ratio:.1f}% Revenue to Import ratio</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Main Charts Section
        st.markdown("<div class='section-header'><h2>📊 Production & Consumption Analysis</h2></div>", unsafe_allow_html=True)
        st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
        
        # First row of charts
        col1, col2 = st.columns(2)
        
        with col1:
            # Create gauge chart for consumption vs production ratio
            fig = create_gauge_chart(
                consumption_ratio, 
                "Consumption vs Production (%)",
                0, 
                150,
                {
                    'low': {'color': '#2ECC40', 'range': [0, 70]},      # Green (low consumption relative to production is good)
                    'medium': {'color': '#FFDC00', 'range': [70, 100]}, # Yellow
                    'high': {'color': '#FF4136', 'range': [100, 150]}   # Red (consumption exceeds production)
                }
            )
            st.plotly_chart(fig, use_container_width=True)
            
        with col2:
            # Financial gauge
            fig2 = create_gauge_chart(
                revenue_to_import_ratio, 
                "Revenue to Import Costs (%)",
                0, 
                200,
                {
                    'low': {'color': '#FF4136', 'range': [0, 100]},     # Red (revenue lower than import costs)
                    'medium': {'color': '#FFDC00', 'range': [100, 150]},# Yellow
                    'high': {'color': '#2ECC40', 'range': [150, 200]}   # Green (revenue much higher than costs)
                }
            )
            st.plotly_chart(fig2, use_container_width=True)
        
        # Add a stylish divider
        st.markdown("<div class='custom-divider'></div>", unsafe_allow_html=True)
        
        # Second row - trends over time
        col1, col2 = st.columns(2)
        
        with col1:
            # Create production trend chart with plotly
            fig3 = px.line(
                filtered_data, 
                x=gas_columns[0], 
                y=gas_columns[1],
                title=f"Gas Production Trend Over Time",
                markers=True,
                color_discrete_sequence=["#106466"]
            )
            
            # Add area beneath the line
            fig3.add_trace(
                go.Scatter(
                    x=filtered_data[gas_columns[0]],
                    y=filtered_data[gas_columns[1]],
                    mode='lines',
                    line=dict(width=0),
                    fillcolor='rgba(16, 100, 102, 0.2)',
                    fill='tozeroy',
                    showlegend=False
                )
            )
            
            # Update layout
            fig3.update_layout(
                xaxis_title="Year",
                yaxis_title="Production (Bcf)",
                hovermode="x unified",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)"
            )
            
            # Add grid lines
            fig3.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(230, 230, 230, 0.8)')
            fig3.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(230, 230, 230, 0.8)')
            
            st.plotly_chart(fig3, use_container_width=True)
            
        with col2:
            # Create consumption trend chart with plotly
            fig4 = px.line(
                filtered_data, 
                x=gas_columns[0], 
                y=gas_columns[2],
                title=f"Gas Consumption Trend Over Time",
                markers=True,
                color_discrete_sequence=["#A30000"]
            )
            
            # Add area beneath the line
            fig4.add_trace(
                go.Scatter(
                    x=filtered_data[gas_columns[0]],
                    y=filtered_data[gas_columns[2]],
                    mode='lines',
                    line=dict(width=0),
                    fillcolor='rgba(163, 0, 0, 0.2)',
                    fill='tozeroy',
                    showlegend=False
                )
            )
            
            # Update layout
            fig4.update_layout(
                xaxis_title="Year",
                yaxis_title="Consumption (Bcf)",
                hovermode="x unified",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)"
            )
            
            # Add grid lines
            fig4.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(230, 230, 230, 0.8)')
            fig4.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(230, 230, 230, 0.8)')
            
            st.plotly_chart(fig4, use_container_width=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Comparative Analysis Section
        st.markdown("<div class='line-chart-container'>", unsafe_allow_html=True)
        st.markdown("<h3 class='chart-title'>Production vs. Consumption Comparative Analysis</h3>", unsafe_allow_html=True)
        
        # Create an interactive comparison chart
        fig5 = go.Figure()
        
        # Add production line
        fig5.add_trace(
            go.Scatter(
                x=filtered_data[gas_columns[0]], 
                y=filtered_data[gas_columns[1]],
                mode='lines+markers',
                name='Production',
                line=dict(color='#106466', width=3),
                marker=dict(size=8)
            )
        )
        
        # Add consumption line
        fig5.add_trace(
            go.Scatter(
                x=filtered_data[gas_columns[0]], 
                y=filtered_data[gas_columns[2]],
                mode='lines+markers',
                name='Consumption',
                line=dict(color='#A30000', width=3),
                marker=dict(size=8)
            )
        )
        
        # Add surplus/deficit area
        y_surplus = []
        for i in range(len(filtered_data)):
            prod = filtered_data[gas_columns[1]].iloc[i]
            cons = filtered_data[gas_columns[2]].iloc[i]
            y_surplus.append(prod - cons)
            
        fig5.add_trace(
            go.Bar(
                x=filtered_data[gas_columns[0]],
                y=y_surplus,
                name='Surplus/Deficit',
                marker=dict(
                    color=['#2ECC40' if val >= 0 else '#FF4136' for val in y_surplus]
                ),
                opacity=0.6
            )
        )
        
        # Update layout
        fig5.update_layout(
            title="Production vs. Consumption with Surplus/Deficit",
            xaxis_title="Year",
            yaxis_title="Natural Gas (Bcf)",
            legend_title="Metrics",
            hovermode="x unified",
            barmode='relative',
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)"
        )
        
        # Add grid lines
        fig5.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(230, 230, 230, 0.8)')
        fig5.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(230, 230, 230, 0.8)')
        
        st.plotly_chart(fig5, use_container_width=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Financial Analysis Section
        st.markdown("<div class='section-header'><h2>💰 Financial Analysis</h2></div>", unsafe_allow_html=True)
        st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Revenue trend
            fig6 = px.bar(
                filtered_data,
                x=gas_columns[0],
                y=gas_columns[3],
                title="Gas Revenue Over Time",
                color_discrete_sequence=['#3CB371']
            )
            
            # Update layout
            fig6.update_layout(
                xaxis_title="Year",
                yaxis_title="Revenue (PKR Billions)",
                yaxis=dict(range=[0, 2000]),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)"
            )
            
            # Add grid lines
            fig6.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(230, 230, 230, 0.8)')
            fig6.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(230, 230, 230, 0.8)')
            
            st.plotly_chart(fig6, use_container_width=True)
            
        with col2:
            # Import costs trend
            fig7 = px.bar(
                filtered_data,
                x=gas_columns[0],
                y=gas_columns[4],
                title="Gas Import Costs Over Time",
                color_discrete_sequence=['#FF8C00']
            )
            
            # Update layout
            fig7.update_layout(
                xaxis_title="Year",
                yaxis_title="Import Costs (PKR Billions)",
                yaxis=dict(range=[0, 2000]),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)"
            )
            
            # Add grid lines
            fig7.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(230, 230, 230, 0.8)')
            fig7.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(230, 230, 230, 0.8)')
            
            st.plotly_chart(fig7, use_container_width=True)
        
        # Add a divider
        st.markdown("<div class='custom-divider'></div>", unsafe_allow_html=True)
        
        # Financial balance analysis
        # Create net balance (profit/loss)
        filtered_data["Net Balance"] = filtered_data[gas_columns[3]] - filtered_data[gas_columns[4]]
        
        # Create financial waterfall chart
        fig8 = go.Figure(go.Waterfall(
            name="Financial Balance",
            orientation="v",
            measure=["relative"] * len(filtered_data),
            x=filtered_data[gas_columns[0]],
            y=filtered_data["Net Balance"],
            textposition="outside",
            text=[f"{val:+.2f}" for val in filtered_data["Net Balance"]],
            connector={"line": {"color": "rgb(63, 63, 63)"}},
            increasing={"marker": {"color": "#2ECC40"}},
            decreasing={"marker": {"color": "#FF4136"}}
        ))
        
        fig8.update_layout(
            title="Yearly Financial Balance (Revenue - Import Costs)",
            xaxis_title="Year",
            yaxis_title="Net Balance (PKR Billions)",
            waterfallgap=0.2,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)"
        )
        
        st.plotly_chart(fig8, use_container_width=True)
        
        # Create revenue vs import costs comparison chart
        fig9 = go.Figure()
        
        # Add revenue line
        fig9.add_trace(
            go.Scatter(
                x=filtered_data[gas_columns[0]], 
                y=filtered_data[gas_columns[3]],
                mode='lines+markers',
                name='Revenue',
                line=dict(color='#3CB371', width=3),
                marker=dict(size=8)
            )
        )
        
        # Add import costs line
        fig9.add_trace(
            go.Scatter(
                x=filtered_data[gas_columns[0]], 
                y=filtered_data[gas_columns[4]],
                mode='lines+markers',
                name='Import Costs',
                line=dict(color='#FF8C00', width=3),
                marker=dict(size=8)
            )
        )
        
        # Add profit/loss area
        fig9.add_trace(
            go.Scatter(
                x=filtered_data[gas_columns[0]],
                y=filtered_data["Net Balance"],
                mode='lines',
                name='Profit/Loss',
                line=dict(color='#106466', width=2, dash='dot'),
                fill='tozeroy',
                fillcolor='rgba(16, 100, 102, 0.2)'
            )
        )
        
        # Update layout
        fig9.update_layout(
            title="Revenue vs. Import Costs with Profit/Loss",
            xaxis_title="Year",
            yaxis_title="Financial Value (PKR Billions)",
            legend_title="Financial Metrics",
            hovermode="x unified",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)"
        )
        
        st.plotly_chart(fig9, use_container_width=True)
        
        st.markdown("</div>", unsafe_allow_html=True)

    else:
        st.warning("⚠ No data available for natural gas production and consumption.")
