import streamlit as st
from reportlab.lib.pagesizes import A4, portrait
from reportlab.pdfgen import canvas
from reportlab.lib import colors
import io
import base64
from datetime import datetime
import os
from reportlab.lib.utils import ImageReader
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPDF

# Function to create a minimalist cover page with simple IESA text and "Report"
def create_minimalist_cover():
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=portrait(A4))
    width, height = portrait(A4)  # Get page size
    
    # Draw white background
    c.setFillColor(colors.white)
    c.rect(0, 0, width, height, fill=1, stroke=0)
    
    # Draw top horizontal line (blue)
    c.setStrokeColor(colors.HexColor("#0055A4"))
    c.setLineWidth(2)
    c.line(10, height-20, width-10, height-20)
    
    # Draw bottom horizontal line (red)
    c.setStrokeColor(colors.red)
    c.setLineWidth(2)
    c.line(10, 20, width-10, 20)
    
    # Simple IESA text - just plain text with no styling
    c.setFillColor(colors.HexColor("#00A67E"))  # Green color
    c.setFont("Helvetica-Bold", 60)
    
    # Center the text
    iesa_text = "IESA"
    text_width = c.stringWidth(iesa_text, "Helvetica-Bold", 60)
    text_x = (width - text_width) / 2
    text_y = height/2 + 30
    
    # Draw the plain text
    c.drawString(text_x, text_y, iesa_text)
    
    # Add "ENERGY REPORT" text below - with more style
    # Position it closer to IESA text
    report_y = text_y - 60  # Closer to IESA text
    
    # Add a subtle underline for REPORT text
    report_text = "ENERGY REPORT"
    c.setFont("Helvetica-Bold", 38)  # Slightly larger
    c.setFillColor(colors.HexColor("#222222"))  # Darker for more contrast
    report_width = c.stringWidth(report_text, "Helvetica-Bold", 38)
    report_x = (width - report_width) / 2
    
    # Draw REPORT text
    c.drawString(report_x, report_y, report_text)
    
    # Add decorative underline
    c.setStrokeColor(colors.HexColor("#222222"))
    c.setLineWidth(1.5)
    c.line(report_x, report_y - 8, report_x + report_width, report_y - 8)
    
    # Add small decorative elements on sides of REPORT
    c.setFillColor(colors.HexColor("#222222"))
    c.circle(report_x - 15, report_y - 4, 3, fill=1, stroke=0)
    c.circle(report_x + report_width + 15, report_y - 4, 3, fill=1, stroke=0)
    
    # Add current date at the bottom
    c.setFont("Helvetica", 10)
    c.setFillColor(colors.HexColor("#666666"))
    current_date = "25 April 2025"
    c.drawCentredString(width/2, 40, current_date)
    
    c.save()
    buffer.seek(0)
    return buffer

# Function to create a comprehensive IESA application cover page with enhanced professional design
def create_iesa_cover(title="Comprehensive Energy Analysis Report", 
                      subtitle="Intelligent Energy Scenario Analysis Platform", 
                      prepared_for="Energy Department",
                      prepared_by="IESA Analytics Team",
                      report_period="Annual Review"):
    
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=portrait(A4))
    width, height = portrait(A4)  # Get page dimensions
    
    # Professional color palette
    primary_color = colors.HexColor("#003F5C")  # Deep blue
    secondary_color = colors.HexColor("#58508D")  # Purple
    accent_color = colors.HexColor("#BC5090")  # Magenta
    highlight_color = colors.HexColor("#FF6361")  # Coral
    neutral_color = colors.HexColor("#444444")  # Dark gray
    light_neutral = colors.HexColor("#F5F5F5")  # Off-white
    
    # Create full background
    c.setFillColor(light_neutral)
    c.rect(0, 0, width, height, fill=1, stroke=0)
    
    # Add professional side panel
    panel_width = 140
    c.setFillColor(primary_color)
    c.rect(0, 0, panel_width, height, fill=1, stroke=0)
    
    # Add decorative elements to side panel
    for i in range(6):
        y_pos = height - 100 - i * 120
        if y_pos > 0:
            c.setFillColor(secondary_color)
            c.setStrokeColor(secondary_color)
            c.setLineWidth(0)
            
            # Draw decorative shapes
            if i % 2 == 0:
                # Diamond
                c.circle(panel_width/2, y_pos, 15, fill=1, stroke=0)
            else:
                # Square
                c.rect(panel_width/2 - 12, y_pos - 12, 24, 24, fill=1, stroke=0)
    
    # Add top accent band
    c.setFillColor(secondary_color)
    c.rect(panel_width, height - 60, width - panel_width, 60, fill=1, stroke=0)
    
    # Add angled graphic element
    c.setFillColor(highlight_color)
    p = c.beginPath()
    p.moveTo(panel_width, height - 60)
    p.lineTo(panel_width + 80, height)
    p.lineTo(panel_width, height)
    p.close()
    c.drawPath(p, fill=1, stroke=0)
    
    # Add IESA text on side panel
    c.saveState()
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 36)
    
    # Vertical "IESA" text along side panel
    c.translate(panel_width/2, height/2)
    c.rotate(90)
    iesa_text = "IESA"
    text_width = c.stringWidth(iesa_text, "Helvetica-Bold", 36)
    c.drawCentredString(0, 0, iesa_text)
    c.restoreState()
    
    # Add subtitle on side panel
    c.saveState()
    c.setFillColor(colors.white)
    c.setFont("Helvetica", 9)
    
    # Vertical subtitle text below IESA
    c.translate(panel_width/2 + 25, height/2)
    c.rotate(90)
    side_subtitle = "Intelligent Energy Solutions"
    c.drawCentredString(0, 0, side_subtitle)
    c.restoreState()
    
    # Main title with professional styling
    title_x = panel_width + 40
    title_y = height - 130
    
    # Add title background
    c.setFillColor(colors.white)
    c.roundRect(title_x - 10, title_y - 40, width - title_x - 30, 80, 3, fill=1, stroke=0)
    
    # Add title
    c.setFillColor(primary_color)
    c.setFont("Helvetica-Bold", 26)
    title_width = c.stringWidth(title, "Helvetica-Bold", 26)
    # Make sure the title fits within the available space
    available_width = width - title_x - 30
    
    # Check if title needs to be truncated or wrapped
    if title_width > available_width:
        # Title is too long, we'll need to wrap it
        wrapped_title = []
        words = title.split()
        current_line = ""
        
        for word in words:
            test_line = current_line + " " + word if current_line else word
            test_width = c.stringWidth(test_line, "Helvetica-Bold", 26)
            
            if test_width <= available_width:
                current_line = test_line
            else:
                wrapped_title.append(current_line)
                current_line = word
        
        if current_line:
            wrapped_title.append(current_line)
        
        # Draw the wrapped title
        line_height = 30
        for i, line in enumerate(wrapped_title):
            c.drawString(title_x, title_y - i * line_height, line)
        
        # Adjust subtitle position if title is wrapped
        subtitle_y = title_y - len(wrapped_title) * line_height + 5
    else:
        # Title fits on one line
        c.drawString(title_x, title_y, title)
        subtitle_y = title_y - 25
    
    # Add subtitle with adjusted position
    c.setFillColor(secondary_color)
    c.setFont("Helvetica", 14)
    subtitle_width = c.stringWidth(subtitle, "Helvetica", 14)
    
    # Check if subtitle needs wrapping
    if subtitle_width > available_width:
        # Similar approach for subtitle
        wrapped_subtitle = []
        words = subtitle.split()
        current_line = ""
        
        for word in words:
            test_line = current_line + " " + word if current_line else word
            test_width = c.stringWidth(test_line, "Helvetica", 14)
            
            if test_width <= available_width:
                current_line = test_line
            else:
                wrapped_subtitle.append(current_line)
                current_line = word
        
        if current_line:
            wrapped_subtitle.append(current_line)
        
        # Draw the wrapped subtitle
        line_height = 20
        for i, line in enumerate(wrapped_subtitle):
            c.drawString(title_x, subtitle_y - i * line_height, line)
        
        # Adjust decorative line position
        line_y = subtitle_y - len(wrapped_subtitle) * line_height - 10
    else:
        # Subtitle fits on one line
        c.drawString(title_x, subtitle_y, subtitle)
        line_y = subtitle_y - 10
    
    # Add decorative element with adjusted position
    c.setStrokeColor(accent_color)
    c.setLineWidth(3)
    c.line(title_x, line_y, title_x + 100, line_y)
    
    # Add circular logo in the center
    center_x = panel_width + (width - panel_width) / 2
    center_y = height / 2
    logo_radius = 70
    
    # Main circle with gradient effect
    for i in range(logo_radius, 0, -2):
        shade = (logo_radius - i) / logo_radius  # 0 to 1
        r, g, b = primary_color.rgb()
        r2, g2, b2 = secondary_color.rgb()
        blend_r = r + (r2 - r) * shade
        blend_g = g + (g2 - g) * shade
        blend_b = b + (b2 - b) * shade
        
        c.setFillColor(colors.Color(blend_r, blend_g, blend_b))
        c.circle(center_x, center_y, i, fill=1, stroke=0)
    
    # White inner circle
    c.setFillColor(colors.white)
    c.circle(center_x, center_y, logo_radius * 0.7, fill=1, stroke=0)
    
    # IESA text in logo
    c.setFillColor(primary_color)
    c.setFont("Helvetica-Bold", 42)
    logo_text = "IESA"
    logo_text_width = c.stringWidth(logo_text, "Helvetica-Bold", 42)
    c.drawString(center_x - logo_text_width / 2, center_y - 15, logo_text)
    
    # Create a cleaner center emblem
    # Main outer circle with solid color
    c.setFillColor(primary_color)
    c.setStrokeColor(primary_color)
    c.circle(center_x, center_y, logo_radius, fill=1, stroke=0)
    
    # Clean white inner circle
    c.setFillColor(colors.white)
    inner_radius = logo_radius * 0.85
    c.circle(center_x, center_y, inner_radius, fill=1, stroke=0)
    
    # Draw IESA text in logo with better positioning and size
    c.setFillColor(primary_color)
    c.setFont("Helvetica-Bold", 38)  # Slightly smaller for better fit
    logo_text = "IESA"
    logo_text_width = c.stringWidth(logo_text, "Helvetica-Bold", 38)
    # Ensure text is vertically centered
    text_y_offset = 13  # Adjust this value to center text vertically
    c.drawString(center_x - logo_text_width / 2, center_y - text_y_offset, logo_text)
    
    # Add thin ring around the logo for more professional appearance
    c.setStrokeColor(accent_color)
    c.setLineWidth(1.5)
    c.setFillColor(None)  # No fill, just stroke
    c.circle(center_x, center_y, logo_radius + 3, fill=0, stroke=1)
    
    # Report details section
    details_x = panel_width + 40
    details_y = 200
    
    # Add details background with subtle shadow effect
    c.setFillColor(colors.white)
    c.roundRect(details_x - 5, details_y - 115, width - details_x - 30, 145, 5, fill=1, stroke=0)
    
    # Add decorative header bar
    c.setFillColor(secondary_color)
    c.roundRect(details_x - 5, details_y + 10, width - details_x - 30, 20, 5, fill=1, stroke=0)
    
    # Add "REPORT DETAILS" text
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(details_x + 5, details_y + 15, "REPORT DETAILS")
    
    # Add report information with improved layout
    info_x = details_x + 15
    
    labels = ["Prepared For:", "Prepared By:", "Report Period:", "Date Generated:"]
    values = [prepared_for, prepared_by, report_period, datetime.now().strftime("%B %d, %Y")]
    
    for i, (label, value) in enumerate(zip(labels, values)):
        y_pos = details_y - 5 - i*25
        
        # Label with icon-like element
        c.setFont("Helvetica-Bold", 11)
        c.setFillColor(primary_color)
        c.circle(info_x - 8, y_pos - 3, 3, fill=1, stroke=0)
        c.drawString(info_x, y_pos, label)
        
        # Value with more professional formatting
        c.setFont("Helvetica", 11)
        c.setFillColor(neutral_color)
        c.drawString(info_x + 120, y_pos, value)
        
        # Subtle separator line
        if i < len(labels) - 1:
            c.setStrokeColor(colors.HexColor("#EEEEEE"))
            c.setLineWidth(0.5)
            c.line(info_x, y_pos - 12, width - 70, y_pos - 12)
    
    # Add footer band
    c.setFillColor(primary_color)
    c.rect(panel_width, 0, width - panel_width, 25, fill=1, stroke=0)
    
    # Add copyright text
    c.setFillColor(colors.white)
    c.setFont("Helvetica", 8)
    c.drawString(panel_width + 15, 10, "© 2025 IESA | CONFIDENTIAL: FOR INTERNAL USE ONLY")
    
    # Add QR code placeholder
    qr_size = 60
    qr_x = width - qr_size - 30
    qr_y = 80
    
    c.setFillColor(colors.white)
    c.rect(qr_x, qr_y, qr_size, qr_size, fill=1, stroke=0)
    
    c.setStrokeColor(primary_color)
    c.setLineWidth(1)
    c.rect(qr_x, qr_y, qr_size, qr_size, fill=0, stroke=1)
    
    # Add QR code text
    c.setFillColor(primary_color)
    c.setFont("Helvetica", 7)
    c.drawCentredString(qr_x + qr_size/2, qr_y - 10, "Scan for Digital Version")
    
    # Add signature line with improved styling
    sig_y = 60
    sig_x = panel_width + 100
    sig_width = 150
    
    c.setStrokeColor(primary_color)
    c.setLineWidth(0.8)
    c.line(sig_x, sig_y, sig_x + sig_width, sig_y)
    
    c.setFillColor(primary_color)
    c.setFont("Helvetica", 8)
    c.drawCentredString(sig_x + sig_width/2, sig_y - 15, "Authorized Signature")
    
    c.save()
    buffer.seek(0)
    return buffer

# Function to create a dark-themed modern annual report
def create_annual_report_style(title="Energy Report", 
                            subtitle="Intelligent Energy Scenario Analysis",
                            year=datetime.now().year,
                            prepared_for="Energy Sector",
                            prepared_by="IESA Team"):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=portrait(A4))
    width, height = portrait(A4)  # Get page size
    
    # Define colors - dark theme with green accents
    bg_color = colors.HexColor("#333333")       # Dark gray background
    darker_gray = colors.HexColor("#2A2A2A")    # Darker gray for sections
    accent_color = colors.HexColor("#00A67E")   # Green color
    white = colors.white                        # White text
    light_gray = colors.HexColor("#CCCCCC")     # Light gray for secondary text
    
    # Draw dark background
    c.setFillColor(bg_color)
    c.rect(0, 0, width, height, fill=1, stroke=0)
    
    # Add logo and company name in top left
    logo_x, logo_y = 30, height - 30
    
    # Use the SVG logo if it exists
    svg_logo_path = "images/iesa_white.svg"
    if os.path.exists(svg_logo_path):
        try:
            # Convert SVG to ReportLab graphics and render to PDF context
            drawing = svg2rlg(svg_logo_path)
            # Scale the logo to fit nicely
            logo_width = 100  # Width for the SVG logo
            logo_height = 30  # Height for the SVG logo
            
            scale_x = logo_width / drawing.width
            scale_y = logo_height / drawing.height
            
            drawing.scale(scale_x, scale_y)
            drawing.width = logo_width
            drawing.height = logo_height
            
            # Render the drawing to the PDF canvas
            renderPDF.draw(drawing, c, logo_x, logo_y - 20)
        except Exception as e:
            # Fallback to the simple circle and text if SVG rendering fails
            c.setFillColor(accent_color)
            c.circle(logo_x + 10, logo_y - 10, 12, fill=1, stroke=0)
            c.setFillColor(white)
            c.setFont("Helvetica-Bold", 14)
            c.drawString(logo_x + 30, logo_y - 15, "IESA")
            print(f"Error loading SVG: {e}")
    else:
        # Fallback to the simple circle and text if SVG doesn't exist
        c.setFillColor(accent_color)
        c.circle(logo_x + 10, logo_y - 10, 12, fill=1, stroke=0)
        c.setFillColor(white)
        c.setFont("Helvetica-Bold", 14)
        c.drawString(logo_x + 30, logo_y - 15, "IESA")
    
    # Add main title (Energy)
    title_x, title_y = 30, height - 100
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 40)
    c.drawString(title_x, title_y, "Energy")
    
    # Add "report" in green and lowercase as shown in example
    report_y = title_y - 50
    c.setFillColor(accent_color)
    c.setFont("Helvetica-Bold", 48)
    c.drawString(title_x, report_y, "report")
    
    # Add white line below report
    c.setStrokeColor(white)
    c.setLineWidth(1)
    c.line(title_x, report_y - 20, title_x + 200, report_y - 20)
    
    # Add session subtitle
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 14)
    c.drawString(title_x, report_y - 40, subtitle)
    
    # Add small description text
    c.setFillColor(light_gray)
    c.setFont("Helvetica", 8)
    description_lines = [
        "IESA is decision support system that help energy planners to make data driven decision",
        "and generate personalized recommendations."
    ]
    
    desc_y = report_y - 65
    for line in description_lines:
        c.drawString(title_x, desc_y, line)
        desc_y -= 12
    
    # Add decorative dots on right side (like in the example)
    dot_x = width - 60
    dot_y = report_y + 10
    dot_radius = 3
    dot_spacing = 15
    
    c.setFillColor(accent_color)
    # Pattern of dots (filled and unfilled)
    dot_pattern = [1, 0, 1, 0, 1, 0, 1]  # 1=filled, 0=unfilled
    
    for i, is_filled in enumerate(dot_pattern):
        if is_filled:
            c.circle(dot_x, dot_y - i*dot_spacing, dot_radius, fill=1, stroke=0)
        else:
            c.setStrokeColor(accent_color)
            c.circle(dot_x, dot_y - i*dot_spacing, dot_radius, fill=0, stroke=1)
    
    # Add white background box for lower section
    lower_height = height * 0.45  # Lower section takes about 45% of the page
    c.setFillColor(white)
    c.rect(0, 0, width, lower_height, fill=1, stroke=0)
    
    # Add a nice green box for report details on the left side
    details_box_width = width * 0.8
    details_box_height = lower_height * 0.6
    details_box_x = width / 2 - details_box_width / 2  # Center horizontally
    details_box_y = lower_height / 2 - details_box_height / 2  # Center vertically
    
    # Dark green color for border
    dark_green_border = colors.HexColor("#007C59")
    # Dark green for label text
    dark_green_text = colors.HexColor("#007C59")
    # Black for value text
    black_text = colors.black
    
    # Draw the main white box with dark green borders
    c.setFillColor(colors.white)
    c.setStrokeColor(dark_green_border)
    c.setLineWidth(2)
    c.roundRect(details_box_x, details_box_y, details_box_width, details_box_height, 8, fill=1, stroke=1)
    
    # Add a header to the box
    c.setFillColor(dark_green_text)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(details_box_x + 20, details_box_y + details_box_height - 30, "REPORT DETAILS")
    
    # Add a green line below the header
    c.setStrokeColor(dark_green_border)
    c.setLineWidth(1)
    c.line(details_box_x + 20, details_box_y + details_box_height - 40, 
           details_box_x + details_box_width - 20, details_box_y + details_box_height - 40)
    
    # Add prepared by/for and other details in the box
    details_content_y = details_box_y + details_box_height - 80
    
    # Define the labels and values
    details = [
        ("Prepared For:", prepared_for),
        ("Prepared By:", prepared_by),
        ("Report Period:", "2002 to 2019"),
        ("Date Generated:", "25 April 2025")
    ]
    
    # Set up formatting
    label_x = details_box_x + 40
    value_x = details_box_x + 180
    line_height = 35
    
    # Draw each detail row
    for i, (label, value) in enumerate(details):
        y_pos = details_content_y - (i * line_height)
        
        # Label (bold) in dark green
        c.setFillColor(dark_green_text)
        c.setFont("Helvetica-Bold", 12)
        c.drawString(label_x, y_pos, label)
        
        # Value (regular) in black
        c.setFillColor(black_text)
        c.setFont("Helvetica", 12)
        c.drawString(value_x, y_pos, value)
        
        # Add a small circle icon before each label (in dark green)
        c.setFillColor(dark_green_border)
        c.circle(label_x - 15, y_pos + 4, 3, fill=1, stroke=0)
    
    c.save()
    buffer.seek(0)
    return buffer

# Function to display PDF preview in Streamlit
def display_pdf(pdf_bytes):
    base64_pdf = base64.b64encode(pdf_bytes.read()).decode("utf-8")
    pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="700" height="500" type="application/pdf"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)
st.set_page_config(
    page_title="IESA Report Cover Generator",
    page_icon="📊",
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
# Streamlit UI
st.title("IESA Report Cover Generator")

st.markdown("""
## Generate Professional Cover Pages for IESA Reports
Create customized cover pages for all your IESA-related reports with consistent branding and professional styling.
""")

# Create tabs
tab1, tab2, tab3, tab4 = st.tabs(["IESA Dark Theme", "Annual Report Style", "IESA Application Cover", "Minimalist Cover"])

with tab1:
    st.subheader("IESA Dark Theme")
    st.markdown("Features the official IESA logo, a modern dark theme with green accent colors, and a clean white report details box with elegant green borders.")
    
    # Input fields for customization
    col1, col2 = st.columns(2)
    
    with col1:
        title = st.text_input("Report Title", "Energy Report", key="dark_title")
        subtitle = st.text_input("Subtitle", "Intelligent Energy Scenario Analysis", key="dark_subtitle")
    
    with col2:
        year = st.number_input("Year", min_value=2000, max_value=2050, value=2025, key="dark_year")
        prepared_for = st.text_input("Prepared For", "Energy Sector", key="dark_prep_for")
    
    prepared_by = st.text_input("Prepared By", "IESA Team", key="dark_prep_by")
    
    # Generate button
    if st.button("Generate Dark Theme Cover"):
        pdf_buffer = create_annual_report_style(title, subtitle, year, prepared_for, prepared_by)
        
        # Display PDF Preview
        st.subheader("📄 Cover Page Preview:")
        display_pdf(pdf_buffer)
        
        # Provide Download Button
        st.download_button("📥 Download Cover Page", pdf_buffer, "IESA_Energy_Report_Cover.pdf", "application/pdf")

with tab2:
    st.subheader("Annual Report Style Cover")
    
    # Input fields for customization
    col1, col2 = st.columns(2)
    
    with col1:
        title = st.text_input("Report Title", "Energy Report", key="annual_title")
        subtitle = st.text_input("Subtitle", "Intelligent Energy Scenario Analysis", key="annual_subtitle")
    
    with col2:
        year = st.number_input("Year", min_value=2020, max_value=2050, value=datetime.now().year, key="annual_year")
        prepared_for = st.text_input("Prepared For", "Energy Sector", key="annual_prep_for")
    
    prepared_by = st.text_input("Prepared By", "IESA Team", key="annual_prep_by")
    
    # Generate button
    if st.button("Generate Annual Report Cover"):
        pdf_buffer = create_annual_report_style(title, subtitle, year, prepared_for, prepared_by)
        
        # Display PDF Preview
        st.subheader("📄 Cover Page Preview:")
        display_pdf(pdf_buffer)
        
        # Provide Download Button
        st.download_button("📥 Download Cover Page", pdf_buffer, "IESA_Annual_Report_Cover.pdf", "application/pdf")

with tab3:
    st.subheader("IESA Application Cover Page")
    
    # Input fields for customization
    col1, col2 = st.columns(2)
    
    with col1:
        title = st.text_input("Report Title", "Comprehensive Energy Analysis Report")
        subtitle = st.text_input("Subtitle", "Intelligent Energy Scenario Analysis Platform")
    
    with col2:
        prepared_for = st.text_input("Prepared For", "Energy Department")
        prepared_by = st.text_input("Prepared By", "IESA Analytics Team")
    
    report_period = st.text_input("Report Period", "Annual Review 2025")
    
    # Generate button
    if st.button("Generate IESA Application Cover"):
        pdf_buffer = create_iesa_cover(title, subtitle, prepared_for, prepared_by, report_period)
        
        # Display PDF Preview
        st.subheader("📄 Cover Page Preview:")
        display_pdf(pdf_buffer)
        
        # Provide Download Button
        st.download_button("📥 Download Cover Page", pdf_buffer, "IESA_Application_Cover.pdf", "application/pdf")

with tab4:
    st.subheader("Minimalist Cover Design")
    # Generate button
    if st.button("Generate Minimalist Cover Page"):
        pdf_buffer = create_minimalist_cover()
        
        # Display PDF Preview
        st.subheader("📄 Cover Page Preview:")
        display_pdf(pdf_buffer)
        
        # Provide Download Button
        st.download_button("📥 Download Cover Page", pdf_buffer, "IESA_Cover.pdf", "application/pdf")