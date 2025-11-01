import mysql.connector
import pandas as pd
import streamlit as st
import os
import altair as alt
import locale
import io
from streamlit_option_menu import option_menu
import os
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import Image
from reportlab.lib.utils import ImageReader
import math
from textwrap import wrap
from utils.logger import setup_logger

# Setup logger
logger = setup_logger("iesa_data_planner")
logger.info("IESA Data Planner page loaded")

# Initialize sidebar state and button text
if 'sidebar_state' not in st.session_state:
    st.session_state.sidebar_state = 'expanded'
if 'button_text' not in st.session_state:
    st.session_state.button_text = '← Hide'
if 'needs_rerun' not in st.session_state:
    st.session_state.needs_rerun = False
if 'toggle_triggered' not in st.session_state:
    st.session_state.toggle_triggered = False
if 'rendered_charts' not in st.session_state:
    st.session_state.rendered_charts = {}

# Function to toggle sidebar
def toggle_sidebar():
    if st.session_state.sidebar_state == 'expanded':
        st.session_state.sidebar_state = 'collapsed'
        st.session_state.button_text = '→ Show'
    else:
        st.session_state.sidebar_state = 'expanded'
        st.session_state.button_text = '← Hide'
    st.session_state.needs_rerun = True
    st.session_state.toggle_triggered = True

# Function to auto-hide sidebar
def hide_sidebar():
    st.session_state.sidebar_state = 'collapsed'
    st.session_state.button_text = '→ Show'
    st.session_state.needs_rerun = True
    st.session_state.toggle_triggered = False

# Function to generate chart without saving image
def create_chart(table, chart_type, x_axis, y_axis, show_values, chart_data, selected_color_scheme):
    # Properly format title for better readability
    formatted_table = table.replace('_', ' ').title()
    chart_title = f"{formatted_table}: {x_axis} vs {y_axis}"
    
    # More aggressive wrapping for longer titles
    if len(chart_title) > 35:  # Reduced threshold for wrapping
        parts = chart_title.split(': ')
        if len(parts) > 1:
            chart_title = f"{parts[0]}:\n{parts[1]}"
    
    # Fixed dimensions - wider to accommodate titles
    fixed_width = 550  # Further increased width for better title display
    fixed_height = 350  # Fixed height in pixels
    
    # Add top padding to prevent title from being cut off
    padding = {"top": 30, "bottom": 10, "left": 10, "right": 10}
    
    # Title configuration with improved text handling
    title_config = {
        "text": chart_title,
        "fontSize": 16,  # Slightly smaller font to fit better
        "fontWeight": "bold",
        "color": "#0b8793",
        "font": "Arial",
        "anchor": "middle",  # Center horizontally
        "align": "center",   # Center text alignment
        "limit": 500,  # Limit width to ensure visibility
        "offset": 15   # Move title further from the chart area
    }
    
    if chart_type == "Bar":
        # Sort data by y-axis values before creating the chart
        chart_data = chart_data.sort_values(by=y_axis, ascending=True)
        
        # Create the base bar chart with fixed sizing
        bar_chart = alt.Chart(chart_data).mark_bar().encode(
            x=alt.X(
                x_axis,
                title=x_axis,
                axis=alt.Axis(
                    labelAngle=0,
                    titleFontSize=16,
                    labelFontSize=14,
                    titleFontWeight='bold',
                    labelFontWeight='bold',
                    titleColor='#333333',
                    labelColor='#333333',
                    grid=True,
                    gridColor='#e0e0e0',
                    tickSize=6,
                    tickWidth=2
                )
            ),
            y=alt.Y(
                y_axis,
                title=y_axis,
                axis=alt.Axis(
                    titleFontSize=16,
                    labelFontSize=14,
                    titleFontWeight='bold',
                    labelFontWeight='bold',
                    titleColor='#333333',
                    labelColor='#333333',
                    grid=True,
                    gridColor='#e0e0e0',
                    tickSize=6,
                    tickWidth=2
                )
            ),
            # Color gradient based on y-axis values (not x-axis) for better visualization of magnitude
            color=alt.Color(
                y_axis,
                scale=alt.Scale(scheme=selected_color_scheme),
                legend=None
            ),
            tooltip=[x_axis, alt.Tooltip(y_axis, format=',d')]  # Enhanced tooltip with formatted values
        )
        
        # If show_values is True, add value labels
        if show_values:
            try:
                # Calculate percentage but based on growth/change rather than total
                chart_data_copy = chart_data.copy()
                
                # Check and handle NaN/infinite values
                chart_data_copy['value_for_display'] = chart_data_copy[y_axis].copy()
                chart_data_copy['value_for_display'] = chart_data_copy['value_for_display'].fillna(0)
                chart_data_copy['value_for_display'] = chart_data_copy['value_for_display'].replace([float('inf'), -float('inf')], 0)
                
                # Calculate percentage values that show growth/trend rather than percentage of total
                # Find the minimum value (first or smallest value)
                min_value = chart_data_copy['value_for_display'].min()
                if min_value > 0:  # Avoid division by zero
                    # Calculate percentage compared to the minimum value
                    chart_data_copy['display_value'] = ((chart_data_copy['value_for_display'] - min_value) / min_value * 100).round(0).astype(int)
                    chart_data_copy['display_value'] = chart_data_copy['display_value'].clip(lower=0)  # Ensure no negative percentages
                    
                    # For the minimum value itself, show a small percentage
                    chart_data_copy.loc[chart_data_copy['value_for_display'] == min_value, 'display_value'] = 0
                    
                    # Display values without percentage sign
                    chart_data_copy['display_text'] = chart_data_copy['display_value'].astype(str)
                else:
                    # Fallback if minimum is zero or negative
                    chart_data_copy['display_text'] = chart_data_copy['value_for_display'].astype(int).astype(str)
                
                # Add percentage labels on top of bars with improved visibility
                text = alt.Chart(chart_data_copy).mark_text(
                    align='center',
                    baseline='middle',
                    dy=-14,  # Position above the bar
                    fontSize=14,  # Slightly smaller font size
                    fontWeight='bold',  # Make values bold
                    stroke='white',  # White outline for better visibility
                    strokeWidth=0.5,  # Thinner outline to avoid overwhelming the text
                    strokeOpacity=0.8  # Semi-transparent outline
                ).encode(
                    x=alt.X(x_axis),
                    y=alt.Y(y_axis),
                    text='display_text:N',  # Use the formatted text without % sign
                    color=alt.value('#000000')  # Pure black for maximum contrast
                )
                # Use fixed size instead of container size
                chart = (bar_chart + text).properties(
                    title=title_config,
                    width=fixed_width,
                    height=fixed_height
                )
            except Exception as e:
                # If there's an error showing values, fall back to chart without values
                st.warning(f"Could not display values on chart: {str(e)}")
                chart = bar_chart.properties(
                    title=title_config,
                    width=fixed_width,
                    height=fixed_height
                )
        else:
            # Use fixed size instead of container size
            chart = bar_chart.properties(
                title=title_config,
                width=fixed_width,
                height=fixed_height
            )
        
        # Apply common configuration
        chart = chart.configure_view(
            strokeWidth=1,
            stroke='#cccccc',
            continuousHeight=fixed_height + padding["top"] + padding["bottom"],
            continuousWidth=fixed_width + padding["left"] + padding["right"]
        ).configure_axis(
            grid=True,
            gridColor='#e6e6e6',
            domainColor='#666666',
            tickColor='#666666',
            domainWidth=2,
            tickWidth=2
        ).configure_title(
            fontSize=16,
            font='Arial',
            fontWeight='bold',
            anchor='middle',
            align='center',  # Center text alignment
            color='#0b8793',
            offset=20,  # Increased offset to move title down and prevent cut-off
            limit=500,  # Set maximum width for title text
            lineHeight=20  # Add line height for wrapped text
        ).configure_header(
            titleFontSize=16,
            titleColor='#0b8793',
            titleAlign='center'  # Center header text alignment
        ).properties(
            padding=padding
        )
        
    elif chart_type == "Line":
        chart = alt.Chart(chart_data).mark_line(
            color='#0066cc',
            strokeWidth=3
        ).encode(
            x=alt.X(
                x_axis,
                title=x_axis,
                axis=alt.Axis(
                    labelAngle=0,
                    titleFontSize=16,
                    labelFontSize=14,
                    titleFontWeight='bold',
                    labelFontWeight='bold',
                    titleColor='#333333',
                    labelColor='#333333',
                    grid=True,
                    gridColor='#e0e0e0',
                    tickSize=6,
                    tickWidth=2
                )
            ),
            y=alt.Y(
                y_axis,
                title=y_axis,
                axis=alt.Axis(
                    titleFontSize=16,
                    labelFontSize=14,
                    titleFontWeight='bold',
                    labelFontWeight='bold',
                    titleColor='#333333',
                    labelColor='#333333',
                    grid=True,
                    gridColor='#e0e0e0',
                    tickSize=6,
                    tickWidth=2
                )
            )
        ).properties(
            title=title_config,
            width=fixed_width,
            height=fixed_height
        ).configure_view(
            strokeWidth=1,
            stroke='#cccccc',
            continuousHeight=fixed_height + padding["top"] + padding["bottom"],
            continuousWidth=fixed_width + padding["left"] + padding["right"]
        ).configure_axis(
            grid=True,
            gridColor='#e6e6e6',
            domainColor='#666666',
            tickColor='#666666',
            domainWidth=2,
            tickWidth=2
        ).configure_title(
            fontSize=16,
            font='Arial',
            fontWeight='bold',
            anchor='middle',
            color='#0b8793',
            offset=20,  # Increased offset to move title down
            limit=500,   # Set maximum width for title text
            lineHeight=20  # Add line height for wrapped text
        ).configure_header(
            titleFontSize=16,
            titleColor='#0b8793'
        ).properties(
            padding=padding
        )
        
        # If show_values is true for line chart, add points and text labels
        if show_values:
            try:
                # Add points to the line
                points = alt.Chart(chart_data).mark_circle(
                    size=80,
                    color='#0066cc',
                    opacity=1
                ).encode(
                    x=alt.X(x_axis),
                    y=alt.Y(y_axis),
                    tooltip=[x_axis, alt.Tooltip(y_axis, format=',d')]
                )
                
                # Apply formatting to values for percentage display
                chart_data_copy = chart_data.copy()
                chart_data_copy['value_for_display'] = chart_data_copy[y_axis].copy()
                chart_data_copy['value_for_display'] = chart_data_copy['value_for_display'].fillna(0)
                chart_data_copy['value_for_display'] = chart_data_copy['value_for_display'].replace([float('inf'), -float('inf')], 0)
                
                # Calculate percentage values that show growth/trend rather than percentage of total
                # Find the minimum value (first or smallest value)
                min_value = chart_data_copy['value_for_display'].min()
                if min_value > 0:  # Avoid division by zero
                    # Calculate percentage compared to the minimum value
                    chart_data_copy['display_value'] = ((chart_data_copy['value_for_display'] - min_value) / min_value * 100).round(0).astype(int)
                    chart_data_copy['display_value'] = chart_data_copy['display_value'].clip(lower=0)  # Ensure no negative percentages
                    
                    # For the minimum value itself, show a small percentage
                    chart_data_copy.loc[chart_data_copy['value_for_display'] == min_value, 'display_value'] = 0
                    
                    # Display values without percentage sign
                    chart_data_copy['display_text'] = chart_data_copy['display_value'].astype(str)
                else:
                    # Fallback if minimum is zero or negative
                    chart_data_copy['display_text'] = chart_data_copy['value_for_display'].astype(int).astype(str)
                
                # Replace the text layer with formatted text
                text = alt.Chart(chart_data_copy).mark_text(
                    align='center',
                    baseline='bottom',
                    dy=-10,
                    fontSize=14,  # Smaller text size
                    fontWeight='bold',
                    stroke='white',
                    strokeWidth=0.5,
                    strokeOpacity=0.8
                ).encode(
                    x=alt.X(x_axis),
                    y=alt.Y(y_axis),
                    text='display_text:N',
                    color=alt.value('#000000')
                )
                
                chart = alt.layer(chart, points, text).properties(
                    title=title_config,
                    width=fixed_width,
                    height=fixed_height
                ).configure_view(
                    strokeWidth=1,
                    stroke='#cccccc'
                ).configure_axis(
                    grid=True,
                    gridColor='#e6e6e6',
                    domainColor='#666666',
                    tickColor='#666666'
                ).configure_title(
                    fontSize=16,
                    font='Arial',
                    fontWeight='bold',
                    anchor='middle',
                    color='#0b8793'
                )
            except Exception as e:
                # Fall back to the regular line chart if there's an error
                st.warning(f"Could not display values on line chart: {str(e)}")
                # Chart remains as originally defined
    
    return chart

st.set_page_config(
    page_title="IESA Dashboard",
    page_icon="📊",
    initial_sidebar_state=st.session_state.sidebar_state,
    layout="wide",
    menu_items={
        'Get Help': 'https://www.linkedin.com/company/104830960',
        'Report a bug': 'https://www.linkedin.com/company/104830960',
        'About': (
            "Intelligent Energy Scenario Analysis (IESA) is an AI-based business intelligence project "
            "that will revolutionize energy scenario analysis by utilizing AI and machine learning to "
            "provide accurate and efficient insights.\n\n"
            "Developers:\n\n"
            "• M. Suffian Tafoor\n\n"
            "• M. Yasir Khan\n\n"
            "• M. Farzam Baig\n\n"
        )
    }
)


# Load logo
LOGO_PATH = "images/iesa_green.png"  # Update path if needed

# Session state for user actions
if "user_actions" not in st.session_state:
    st.session_state.user_actions = []

if "chart_paths" not in st.session_state:
    st.session_state.chart_paths = []

def add_chart(chart_path):
    if chart_path not in st.session_state.chart_paths:
        st.session_state.chart_paths.append(chart_path)

# Function to create PDF
def create_pdf(chart_paths=None, user_actions=None):
    # First, create real charts from the database and save them
    try:
        # Connect to the database and fetch actual data
        conn = get_connection()
        cursor = conn.cursor()
        
        # Query to get data from annual_electricity_data table
        query = "SELECT * FROM annual_electricity_data"
        cursor.execute(query)
        rows = cursor.fetchall()
        
        # Get column names
        column_names = [desc[0] for desc in cursor.description]
        
        # Create DataFrame
        electricity_data = pd.DataFrame(rows, columns=column_names)
        
        # Close connection
        conn.close()
        
        # Create folder for chart images if it doesn't exist
        chart_folder = "chart_images"
        os.makedirs(chart_folder, exist_ok=True)
        
        # Create and save 4 charts - 2 bar and 2 line charts
        real_chart_paths = []
        
        # Make sure we have the necessary columns
        year_column = column_names[0]  # Usually 'Year'
        data_columns = column_names[1:5] if len(column_names) > 4 else column_names[1:]
        
        # Ensure data is properly sorted by year
        electricity_data = electricity_data.sort_values(by=year_column)
        
        # Define chart colors
        bar_colors = ["#73C8A9", "#0b8793"]
        line_colors = ["#2F80ED", "#F06C00"]
        
        # Chart 1: Bar chart of Installed Capacity
        if 'Installed Capacity (MW)' in column_names:
            capacity_chart = alt.Chart(electricity_data).mark_bar().encode(
                x=alt.X(year_column, title=year_column, axis=alt.Axis(labelAngle=-45)),
                y=alt.Y('Installed Capacity (MW)', title='Installed Capacity (MW)'),
                color=alt.value(bar_colors[0]),
                tooltip=[year_column, 'Installed Capacity (MW)']
            ).properties(
                title="Installed Capacity (MW) by Year",
                width=500,
                height=350
            ).configure_title(
                fontSize=16,
                font='Arial',
                fontWeight='bold',
                color='#0b8793'
            )
            chart1_path = os.path.join(chart_folder, "capacity_chart.png")
            capacity_chart.save(chart1_path)
            real_chart_paths.append(chart1_path)
        
        # Chart 2: Line chart of Generation
        if 'Generation (GWh)' in column_names:
            generation_chart = alt.Chart(electricity_data).mark_line(point=True, color=line_colors[0]).encode(
                x=alt.X(year_column, title=year_column, axis=alt.Axis(labelAngle=-45)),
                y=alt.Y('Generation (GWh)', title='Generation (GWh)'),
                tooltip=[year_column, 'Generation (GWh)']
            ).properties(
                title="Generation (GWh) by Year",
                width=500,
                height=350
            ).configure_title(
                fontSize=16,
                font='Arial',
                fontWeight='bold',
                color='#0b8793'
            )
            chart2_path = os.path.join(chart_folder, "generation_chart.png")
            generation_chart.save(chart2_path)
            real_chart_paths.append(chart2_path)
        
        # Chart 3: Bar chart of Consumption
        if 'Consumption (GWh)' in column_names:
            consumption_chart = alt.Chart(electricity_data).mark_bar().encode(
                x=alt.X(year_column, title=year_column, axis=alt.Axis(labelAngle=-45)),
                y=alt.Y('Consumption (GWh)', title='Consumption (GWh)'),
                color=alt.value(bar_colors[1]),
                tooltip=[year_column, 'Consumption (GWh)']
            ).properties(
                title="Consumption (GWh) by Year",
                width=500,
                height=350
            ).configure_title(
                fontSize=16,
                font='Arial',
                fontWeight='bold',
                color='#0b8793'
            )
            chart3_path = os.path.join(chart_folder, "consumption_chart.png")
            consumption_chart.save(chart3_path)
            real_chart_paths.append(chart3_path)
        
        # Chart 4: Line chart of Imports
        if 'Imports (GWh)' in column_names:
            imports_chart = alt.Chart(electricity_data).mark_line(point=True, color=line_colors[1]).encode(
                x=alt.X(year_column, title=year_column, axis=alt.Axis(labelAngle=-45)),
                y=alt.Y('Imports (GWh)', title='Imports (GWh)'),
                tooltip=[year_column, 'Imports (GWh)']
            ).properties(
                title="Imports (GWh) by Year",
                width=500,
                height=350
            ).configure_title(
                fontSize=16,
                font='Arial',
                fontWeight='bold',
                color='#0b8793'
            )
            chart4_path = os.path.join(chart_folder, "imports_chart.png")
            imports_chart.save(chart4_path)
            real_chart_paths.append(chart4_path)
        
        # Now create the PDF with these real chart images
        chart_paths = real_chart_paths
    except Exception as e:
        print(f"Error creating charts: {e}")
        # Will fall back to any existing chart_paths or empty PDF

    # Create the PDF
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    # Header with just orange line and logo - no date text
    header_y = height - 45
    
    # Add orange line at top
    c.setStrokeColor(colors.HexColor("#F06C00"))  # Orange color
    c.setLineWidth(2)
    c.line(20, header_y, width - 20, header_y)
    
    # Add logo
    if os.path.exists(LOGO_PATH):
            logo = ImageReader(LOGO_PATH)
    c.drawImage(logo, width - 80, height - 42, width=60, height=24, mask='auto')

    # Title with proper spacing - add more space at the top
    c.setFillColor(colors.HexColor("#504B38")) 
    c.setFont("Helvetica-Bold", 22)
    title_text = "Data Planner Report"
    c.drawString((width - c.stringWidth(title_text, "Helvetica-Bold", 22)) / 2, height - 100, title_text)
    
    # Add shorter description with more space around it
    c.setFillColor(colors.black)
    c.setFont("Helvetica", 11)
    description = "This report presents electricity data trends from 2002 to 2019."
    
    # Center the description
    desc_width = c.stringWidth(description, "Helvetica", 11)
    c.drawString((width - desc_width) / 2, height - 130, description)
    
    # Horizontal line with more space above and below
    c.setStrokeColor(colors.HexColor("#0b8793"))
    c.setLineWidth(1)
    c.line(60, height - 160, width - 60, height - 160)
    
    # Draw section title for charts with more padding
    chart_y = height - 190
    c.setFillColor(colors.HexColor("#0b8793"))
    c.setFont("Helvetica-Bold", 16)
    c.drawString(60, chart_y, "Electricity Data Visualization")
    
    # Shorter chart description with more spacing
    c.setFillColor(colors.black)
    c.setFont("Helvetica", 10)
    chart_desc = "Trends in Pakistan's electricity sector (2002-2019)"
    
    # Center this description too
    chart_desc_width = c.stringWidth(chart_desc, "Helvetica", 10)
    c.drawString((width - chart_desc_width) / 2, chart_y - 25, chart_desc)
    
    # Position for charts - increase spacing
    chart_width = 230
    chart_height = 160  # Slightly smaller to allow more spacing
    
    # Check if we have real chart images
    if chart_paths and len(chart_paths) > 0:
        # Calculate positions for 4 charts in a 2x2 grid with more space between them
        charts_top_y = chart_y - 60  # More space after description
        chart1_x = 60
        chart2_x = chart1_x + chart_width + 30  # More space between charts
        charts_bottom_y = charts_top_y - chart_height - 50  # More space between rows
        
        # Simplified chart titles - shorter
        chart_titles = [
            "Installed Capacity Growth",
            "Electricity Generation Trend",
            "Consumption Pattern",
            "Import Requirements"
        ]
        
        # Simplified chart descriptions - single line only with key values
        chart_descriptions = [
            "17,787 MW to 35,114 MW",
            "75,682 GWh to 128,532 GWh",
            "51,655 GWh to 109,461 GWh",
            "73 GWh to 556 GWh"
        ]
        
        # Draw up to 4 charts in a 2x2 grid
        for i, chart_path in enumerate(chart_paths[:4]):
            if os.path.exists(chart_path):
                # Calculate position based on index
                row = i // 2  # 0 for top row, 1 for bottom row
                col = i % 2    # 0 for left column, 1 for right column
                
                x_pos = chart1_x if col == 0 else chart2_x
                y_pos = charts_top_y if row == 0 else charts_bottom_y
                
                # Draw chart with border - more padding in border
                c.setStrokeColor(colors.HexColor("#0b8793"))
                c.roundRect(x_pos - 5, y_pos - chart_height - 5, chart_width + 10, chart_height + 10, 5, stroke=1, fill=0)

                # Draw the chart image
                c.drawImage(chart_path, x_pos, y_pos - chart_height, width=chart_width, height=chart_height, mask='auto')

                # Add chart title and description with better spacing
                if i < len(chart_titles):
                    # Title - center it
                    c.setFillColor(colors.HexColor("#0b8793"))
                    c.setFont("Helvetica-Bold", 10)
                    title = chart_titles[i]
                    title_width = c.stringWidth(title, "Helvetica-Bold", 10)
                    c.drawString(x_pos + (chart_width - title_width)/2, y_pos - chart_height - 18, title)
                    
                    # Description - center it with clean spacing
                    c.setFillColor(colors.black)
                    c.setFont("Helvetica", 9)
                    desc = chart_descriptions[i]
                    desc_width = c.stringWidth(desc, "Helvetica", 9)
                    c.drawString(x_pos + (chart_width - desc_width)/2, y_pos - chart_height - 35, desc)
        
        # Add insight section with more space and cleaner text
        # Add more space after the last row of charts
        insight_y = charts_bottom_y - chart_height - 70
        
        # Add a subtle separator line above the insights
        c.setStrokeColor(colors.HexColor("#0b8793"))
        c.setLineWidth(1)
        c.line(60, insight_y + 15, width - 60, insight_y + 15)
        
        # Add "Key Insights" heading - centered
        c.setFillColor(colors.HexColor("#0b8793"))
        c.setFont("Helvetica-Bold", 14)
        insight_title = "Key Insights:"
        insight_title_width = c.stringWidth(insight_title, "Helvetica-Bold", 14)
        c.drawString((width - insight_title_width) / 2, insight_y, insight_title)
        
        # Simpler, cleaner summary text
        c.setFillColor(colors.black)
        c.setFont("Helvetica", 10)
        
        summary_text = (
            "Pakistan's electricity sector doubled capacity while increasing generation by 70% and consumption by 112%. "
            "Rising imports indicate growing demand challenges despite capacity expansion."
        )
        
        # Draw the summary with better spacing - centered paragraphs
        text_object = c.beginText(60, insight_y - 25)
        text_object.setFont("Helvetica", 10)
        for wrapped_line in wrap(summary_text, width=75):  # Narrower width for cleaner look
            text_object.textLine(wrapped_line)
        c.drawText(text_object)
    else:
        # Error message if no chart images
        c.setFillColor(colors.red)
        c.setFont("Helvetica", 12)
        c.drawString(60, chart_y - 50, "Error: Unable to generate charts from electricity data.")
    
    # Add footer with blue line
    c.setStrokeColor(colors.HexColor("#4389a2"))
    c.setLineWidth(2)
    c.line(20, 30, width - 20, 30)
    
    # Footer text
    c.setFont("Helvetica", 8)
    c.setFillColor(colors.gray)
    c.drawString(40, 15, "© 2025 IESA. All rights reserved.")
    c.drawString(width - 80, 15, "Page 1")
    
    c.save()
    buffer.seek(0)
    return buffer

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
        logger.info(f"Fetched tables: {tables}")
        return tables
    except Exception as e:
        logger.error(f"Error fetching tables: {e}")
        st.toast("Error fetching tables!", icon="❌")
        return []

# Function to fetch data from a specific table
def fetch_table_data(table_name):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        query = f"SELECT * FROM {table_name}"
        cursor.execute(query)
        rows = cursor.fetchall()
        data = pd.DataFrame(rows, columns=[desc[0] for desc in cursor.description])
        conn.close()
        logger.info(f"Fetched data for table: {table_name}, {len(data)} rows")
        return data
    except Exception as e:
        logger.error(f"Error fetching data from {table_name}: {e}")
        st.toast("Error fetching data!", icon="❌")
        return pd.DataFrame()

# Local image path (Replace with your actual image path)
image_path = "images/iesa_white.svg"

# [data-testid="stSidebar"]  gradient
# background: linear-gradient(135deg, #73C8A9, #0b8793); /* Gradient background */

# CSS and JavaScript for dynamic button states
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
    
    /* Add a small indicator below the active button */
    [data-testid="stHorizontalBlock"] div:nth-child(2) .stButton button::after {
        content: '';
        position: absolute;
        bottom: -8px;
        left: 50%;
        transform: translateX(-50%);
        width: 8px;
        height: 8px;
        background-color: #73C8A9;
        border-radius: 50%;
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



 
 
selected = option_menu(
    menu_title=None,
    options=["Dashboard","Data Planner", "Scenario","Wisdom Mining", "Prediction", "IESA Assistant"],
    icons=["clipboard-data", "bar-chart", "graph-up", "graph-up-arrow", "robot", "robot"],
    default_index=1,
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
    logger.info("User navigated to Dashboard page from Data Planner")
    os.system("streamlit run iesa_dashboard.py")

elif selected == "Scenario":
    logger.info("User navigated to Scenario Analysis page from Data Planner")
    os.system("streamlit run iesa_scenerio_analysis_with_k_means.py")

elif selected == "Prediction":
    logger.info("User navigated to Prediction Engine page from Data Planner")
    os.system("streamlit run iesa_prediction_engine.py")

elif selected == "IESA Assistant":
    logger.info("User navigated to IESA Assistant page from Data Planner")
    os.system("streamlit run iesa_personalized_recommendations.py")

elif selected == "Wisdom Mining":
    logger.info("User navigated to Wisdom Mining page from Data Planner")
    os.system("streamlit run iesa_wisdom_mining.py")

# Initialize session state
if "charts" not in st.session_state:
    st.session_state["charts"] = []

if "metrics" not in st.session_state:
    st.session_state["metrics"] = []

if "selected_table" not in st.session_state:
    st.session_state["selected_table"] = None

if "chart_images_generated" not in st.session_state:
    st.session_state["chart_images_generated"] = False

# Add extra spacing to move the content down
st.markdown("<div style='margin-top: 60px;'></div>", unsafe_allow_html=True)

# Sidebar for table selection
st.sidebar.image(image_path,width=150)
st.sidebar.markdown("""
    <h2>Data Planner Dashboard</h2>
""",unsafe_allow_html=True)
st.sidebar.markdown("""
    <h3>Table and Chart Selection</h3>
""",unsafe_allow_html=True)

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
    
    # Add option to show values on charts
    show_values = st.sidebar.checkbox("Show values on chart", value=False, key="show_values")
    
    add_chart = st.sidebar.button("Add Chart", key="add_chart_button")

    # Metric selection
    st.sidebar.markdown("### Metric Options")
    metric_column = st.sidebar.selectbox("Select Column for Metric", columns, key="metric_column")
    metric_type = st.sidebar.selectbox("Select Metric Type", ["Sum", "Count", "Average", "Unique"])
    add_metric = st.sidebar.button("Add Metric", key="add_metric_button")

    reset_button = st.sidebar.button("Reset Dashboard")
    
    # Add charts to session state (retain charts from all tables)
    if add_chart:
        st.session_state["charts"].append((selected_table, chart_type, x_axis, y_axis, show_values))
        # Hide sidebar when chart is added
        hide_sidebar()
        logger.info(f"Chart added: Table={selected_table}, Type={chart_type}, X={x_axis}, Y={y_axis}, ShowValues={show_values}")
        st.toast(f"Chart added: {chart_type} of {y_axis} vs {x_axis}", icon="📊")

    # Add metrics to session state (retain metrics from all tables)
    if add_metric:
        st.session_state["metrics"].append((selected_table, metric_column, metric_type))
        # Hide sidebar when metric is added
        hide_sidebar()
        logger.info(f"Metric added: Table={selected_table}, Column={metric_column}, Type={metric_type}")
        st.toast(f"Metric added: {metric_type} of {metric_column}", icon="📈")

    # Reset button functionality
    if reset_button:
        # Reset session state
        st.session_state["charts"] = []
        st.session_state["metrics"] = []
        st.session_state["selected_table"] = None
        logger.info("Dashboard reset by user")
        st.toast("Dashboard reset!", icon="🔄")

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

    # Only regenerate chart images if this is not a toggle-triggered rerun
    if not st.session_state.toggle_triggered:
        # Clear previous chart paths 
        st.session_state.chart_paths = []

    # Only generate chart images for PDF - don't display them
    for idx, chart_info in enumerate(st.session_state["charts"]):
        table, chart_type, x_axis, y_axis = chart_info if len(chart_info) == 4 else chart_info[:4]
        show_values = chart_info[4] if len(chart_info) > 4 else False
        chart_data = fetch_table_data(table)
        
        # Generate the chart for saving as image
        chart_key = f"{table}_{chart_type}_{x_axis}_{y_axis}_{show_values}"
        chart = create_chart(table, chart_type, x_axis, y_axis, show_values, chart_data, selected_color_scheme)
        
        # Save chart image for PDF
        chart_folder = "chart_images"
        os.makedirs(chart_folder, exist_ok=True)
        chart_path = os.path.join(chart_folder, f"chart_{idx + 1}.png")
        chart.save(chart_path)
        st.session_state.chart_paths.append(chart_path)
            
    # Display each chart in its own column, regenerating them for display
    for idx, chart_info in enumerate(st.session_state["charts"]):
        col_idx = idx % num_cols  # Determine which column to use
        
        # Extract chart info and generate a fresh chart
        table, chart_type, x_axis, y_axis = chart_info if len(chart_info) == 4 else chart_info[:4]
        show_values = chart_info[4] if len(chart_info) > 4 else False
        chart_data = fetch_table_data(table)
        
        # Create chart specifically for display
        chart = create_chart(table, chart_type, x_axis, y_axis, show_values, chart_data, selected_color_scheme)
        
        # Display the chart in its column with explicit height
        with cols[col_idx]:
            # Display chart on top of the div (the negative margin pulls it up over the div)
            st.markdown('<div style="margin-top: -420px;"></div>', unsafe_allow_html=True)
            st.altair_chart(chart, use_container_width=False)
            
# Streamlit interaction
if selected_table:
    if st.sidebar.button("Logout", key="logout_button"):
        logger.info("User logged out from Data Planner")
        os.system("streamlit run iesa_login.py")

    if st.sidebar.button("Contact Us", key="contact_us_button"):
        logger.info("User clicked Contact Us from Data Planner (navigating to Contact Us page)")
        os.system("streamlit run iesa_contact_us.py")

    # Generate and provide PDF download
    if st.session_state.chart_paths:
        pdf_buffer = create_pdf(st.session_state.chart_paths, st.session_state.user_actions)
        st.sidebar.download_button("Download Report", pdf_buffer, "IESA_Report.pdf", "application/pdf")
        logger.info(f"PDF report generated with {len(st.session_state.chart_paths)} charts")
        st.toast("PDF report ready for download!", icon="📄")

# Check if we need to rerun the script
if st.session_state.needs_rerun:
    st.session_state.needs_rerun = False
    st.rerun()