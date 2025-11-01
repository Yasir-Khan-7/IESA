import streamlit as st
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.utils import ImageReader
import io
import datetime
import os
import base64

# Load the logo (Update the path if needed)
LOGO_PATH = "images/iesa_green.png"  # Ensure this path is correct

# Function to create a custom PDF template
def create_pdf(actions):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4  # Get page size
    page_num = 1  # Start page number

    def draw_header_footer():
       # Adjusted Top Border (1px Gradient) to move upward
        header_y = height - 45  # Moved higher
        c.setStrokeColor(colors.HexColor("#4389a2"))  # Gradient Start Color
        c.setLineWidth(2)  # 1px thickness
        c.line(20, header_y, width - 20, header_y)  # Draw top border higher
        # Footer Bottom Border (Solid Red, 2px)
        c.setStrokeColor(colors.red)
        c.setLineWidth(2)
        c.line(20, 30, width - 20, 30)  # Bottom border only

        # Add Logo at the Right Top End (if exists)
        if os.path.exists(LOGO_PATH):
            logo = ImageReader(LOGO_PATH)
            logo_width, logo_height = 50, 20  # Adjust logo size
            c.drawImage(logo, width - 70, height - 40, width=logo_width, height=logo_height, mask='auto')
        else:
            print("⚠️ Logo file not found:", LOGO_PATH)  # Debug message

    # Draw header and footer on first page
    draw_header_footer()

   # Title Section
    c.setFont("Helvetica-Bold", 18)
    c.setFillColor(colors.black)
    title_text = "IESA Report"
    title_width = c.stringWidth(title_text, "Helvetica-Bold", 18)
    c.drawString((width - title_width) / 2, height - 80, title_text)  # Centered title

    # Generated Date
    c.setFont("Helvetica", 12)
    c.setFillColor(colors.black)
    # c.drawString(150, height - 120, f"Generated on: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Content Section
    c.setFont("Helvetica-Bold", 14)
    # c.drawString(40, height - 120, "Activity Log:")

    y = height - 140  # Start below header
    for action in actions:
        y -= 20
        if y < 70:  # Prevent text overflow, add a new page
            c.setFont("Helvetica", 10)
            c.setFillColor(colors.black)
            c.drawString(width - 50, 15, f"Page {page_num}")  # Page number in footer

            c.showPage()
            page_num += 1

            # Redraw header and footer on new page
            draw_header_footer()

            c.setFont("Helvetica", 12)
            y = height - 50
            c.setFont("Helvetica-Bold", 14)
            c.drawString(40, y, "Activity Log (cont.):")
            y -= 20
        
        c.setFont("Helvetica", 12)
        c.drawString(60, y, f" {action}")

    # Footer Section (Page Number on Right)
    c.setFont("Helvetica-Oblique", 10)
    c.setFillColor(colors.gray)
    c.drawString(40, 15, "© 2025 IESA. All rights reserved.")  # Left side
    c.setFillColor(colors.black)
    c.drawString(width - 50, 15, f"Page {page_num}")  # Right side (page number)

    c.save()
    buffer.seek(0)
    return buffer

# Function to display PDF preview in Streamlit
def display_pdf(pdf_bytes):
    base64_pdf = base64.b64encode(pdf_bytes.read()).decode("utf-8")
    pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="700" height="500" type="application/pdf"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)

# Initialize session state for user actions
if "user_actions" not in st.session_state:
    st.session_state.user_actions = []

# Streamlit UI
st.title("Custom PDF Reporting App")

if st.button("Perform Action"):
    action_text = ""
    st.session_state.user_actions.append(action_text)
    st.success("Action recorded!")

if st.button("Generate PDF Report"):
    if st.session_state.user_actions:
        pdf_buffer = create_pdf(st.session_state.user_actions)

        # Display PDF Preview
        st.subheader("📄 PDF Preview:")
        display_pdf(pdf_buffer)

        # Provide Download Button
        st.download_button("📥 Download Report", pdf_buffer, "IESA_Report.pdf", "application/pdf")
    else:
        st.warning("No actions recorded yet!")
