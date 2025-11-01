import streamlit as st
from streamlit_folium import st_folium
import folium
import urllib.parse
import streamlit as st
import io
import os
import streamlit as st
from utils.logger import setup_logger

# Setup logger
logger = setup_logger("iesa_contact_us")
logger.info("IESA Contact Us page loaded")

st.set_page_config(
    page_title="Contact Us",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
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

#create a head tag to include font awesome icons
st.markdown(
    """
    <head>
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css" rel="stylesheet">
    </head>
    """,
    unsafe_allow_html=True,
)
# Custom CSS for styling with your gradient color updates
st.markdown(
    """
    <style>
    .stApp {
        margin-top: -70px !important; /* Adjust the top margin */
    }

    /* Contact Us section */
    div[data-testid="stColumn"]:first-child {
        padding: 40px;
        margin-right: -15px;
        border-top: 2px solid #cccccc;
        border-left: 2px solid #cccccc;
        border-bottom: 2px solid #cccccc;
        border-radius: 10px;
        background: white; /* White background for the form */
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1); /* Add subtle shadow for depth */
    }

    /* Gradient for form, button, and header borders */
    div[data-testid="stColumn"]:first-child .stTextInput > div, 
    div[data-testid="stColumn"]:first-child .stTextArea > div {
        border: 1px solid #cccccc; /* Updated borders */
        border-radius: 5px;
        padding: 4px; /* Add some padding */
        background-color: #f9f9f9; /* Light background for input fields */
    }

    /* Focus state for inputs */
    div[data-testid="stColumn"]:first-child .stTextInput > div:focus-within, 
    div[data-testid="stColumn"]:first-child .stTextArea > div:focus-within {
        border: 2px solid #4AC29A !important; /* Highlight on focus */
        box-shadow: 0 0 5px rgba(74, 194, 154, 0.3);
    }

    .stTextInput {
        width: 80%;
        margin-bottom: 15px !important; /* Increase spacing between fields */
       
    }

    .stTextArea {
        width: 80% !important;
        margin-bottom: 15px !important; /* Increase spacing between fields */
    }

    /* Placeholder text */
    .stTextInput input::placeholder, .stTextArea textarea::placeholder {
        color: black !important; /* Darker placeholder text for better visibility */
        font-weight: 400;
    }

    /* Button styling */
    div[data-testid="stButton"] > button {
        width: 80%;
        background-color: #4AC29A;
        color: white;
        font-size: 16px;
        font-weight: bold;
        border: none;
        border-radius: 5px;
        padding: 12px; /* Slightly larger button */
        cursor: pointer;
        transition: all 0.2s ease-in-out;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); /* Button shadow */
        margin-top: 10px;
    }

    div[data-testid="stButton"] > button:hover {
      background-color: #44A08D;
      color: white;
      transform: translateY(-2px);
      box-shadow: 0 6px 8px rgba(0, 0, 0, 0.15);
    }

    /* Map column with black gradient background */
    div[data-testid="stColumn"]:nth-child(2) {
        padding: 40px;
        background: linear-gradient(135deg, #232526, #414345); /* Improved contrast gradient */
        color: white; /* White text in the map column */
        border-radius: 10px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2); /* Add shadow for depth */
    }

    /* Heading and text styles for map column */
    div[data-testid="stColumn"]:nth-child(2) h2 {
        font-size: 28px;
        font-weight: bold;
        color: white;
        margin-bottom: 20px;
        border-bottom: 2px solid #4AC29A;
        padding-bottom: 10px;
        text-shadow: 1px 1px 3px rgba(0, 0, 0, 0.3); /* Text shadow for better readability */
    }

    div[data-testid="stColumn"]:nth-child(2) p {
        font-size: 18px;
        color: #f0f0f0 !important; /* Brighter text color */
        margin-bottom: 15px;
        line-height: 1.6;
    }

    /* Target specific image styling in map column */
    div[data-testid="stColumn"]:nth-child(2) img {
        border: 3px solid #4AC29A; /* Thicker border around the map */
        border-radius: 10px;
        width: 100%; /* Set image width */
        margin-top: 20px;
    }

    /* Header Styling */
    header {
        border-bottom: 3px solid #4AC29A !important; /* Updated border for header */
        height: 50px !important;
    }

    /* Text styling */
    h1 {
        font-size: 38px;
        margin-bottom: 16px;
        font-weight: bold;
        color: #0F403F; /* Darker text for better contrast */
        text-shadow: 1px 1px 0px rgba(255, 255, 255, 0.5);
    }

    h5 {
        font-size: 20px;
        margin-bottom: 12px;
        color: #333333;
    }
    
    .required-fields {
        font-size: 16px;
        margin-bottom: 20px;
        color: #666666; /* Darker grey for better visibility */
        font-style: italic;
    }

    /* Hide the tooltip "Press Ctrl+Enter to apply" */
    [data-testid="InputInstructions"] {
        display: None;
    }
    
    iframe {
        border: 4px solid #4AC29A;
        border-radius: 10px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
    }
    
    /* Contact Icons */
    .contact-icon {
        font-size: 22px;
        margin-right: 15px;
        width: 30px;
        display: inline-block;
        text-align: center;
    }
    
    /* CSS for success and error messages */
    .custom-success {
        background-color: #0b8793;  /* Application primary greenish-blue */
        color: #FFFFFF;
        padding: 15px;
        border-radius: 5px;
        margin: 15px 0;
        width: 80%;
        font-size: 16px;
        font-weight: bold;
        box-shadow: 0 4px 6px rgba(11, 135, 147, 0.2); /* Subtle shadow */
        border-left: 5px solid #066570; /* Left border for emphasis */
    }
    
    /* Custom error message styling */
    .custom-error {
        background-color: #FF6B6B;  /* Soft red with some muted tone to match style */
        color: #FFFFFF;
        padding: 15px;
        border-radius: 5px;
        margin: 15px 0;
        width: 80%;
        font-size: 16px;
        font-weight: bold;
        box-shadow: 0 4px 6px rgba(255, 107, 107, 0.2); /* Soft shadow */
        border-left: 5px solid #E84C4C; /* Left border for emphasis */
    }

    [data-testid="stBaseButton-secondary"] {
        background-color: #44A08D;
        color: white;
        border-radius: 5px;
        padding: 8px 16px;
        font-weight: bold;
        border: none;
        transition: all 0.2s ease;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    [data-testid="stBaseButton-secondary"]:hover {
        background-color: #4AC29A;
        transform: translateY(-2px);
        box-shadow: 0 6px 8px rgba(0, 0, 0, 0.15);
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Layout: Using separate columns for the form and contact info
col1, col2 = st.columns([1, 1])  # Both columns will have equal width

with col1:
    # Content for the contact form
    st.image("images/iesa_green.svg", width=130)
    st.markdown("<h1>Contact Us</h1>", unsafe_allow_html=True)
    st.markdown("<h5>We would love to hear from you.</h5>", unsafe_allow_html=True)
    st.markdown(
        "<div class='required-fields'>Please fill out the form below to get in touch.</div>",
        unsafe_allow_html=True,
    )

    # Input fields for the contact form
    name = st.text_input("", placeholder="Your Name *")
    email = st.text_input("", placeholder="Your Email *")
    message = st.text_area("", placeholder="Your Message *", height=150)
    logger.info(f"Contact form loaded. Name: {name}, Email: {email}, Message: {'[provided]' if message else '[empty]'}")

    # Send message button
    if st.button("Send Message"):
        logger.info(f"Send Message button clicked. Name: {name}, Email: {email}")
        if not name or not email or not message:
            logger.warning("Contact form submission failed: missing required fields")
            st.toast("Please fill in all required fields.", icon="⚠️")
            st.markdown(
                "<div class='custom-error'>⚠️ Please fill all the required fields</div>",
                unsafe_allow_html=True,
            )
        else:
            try:
                recipient = "nexzonsolutions@gmail.com"
                subject = f"Message from {name}"
                body = f"Name: {name}\nEmail: {email}\n\nMessage:\n{message}"
                gmail_draft_link = f"https://mail.google.com/mail/?view=cm&fs=1&to={recipient}&su={urllib.parse.quote(subject)}&body={urllib.parse.quote(body)}"
                st.components.v1.html(
                    f'<script>window.open("{gmail_draft_link}", "_black");</script>',
                    height=0,
                    width=0,
                )
                logger.info(f"Contact form submitted successfully. Name: {name}, Email: {email}")
                st.toast("Message sent successfully!", icon="✅")
                st.markdown(
                    "<div class='custom-success'>✅ Gmail draft has been opened in a new tab!</div>",
                    unsafe_allow_html=True,
                )
            except Exception as e:
                logger.error(f"Error during contact form submission: {e}")
                st.toast("Failed to send message. Please try again later.", icon="❌")
                st.markdown(
                    f"<div class='custom-error'>⚠️ An error occurred while sending your message. Please try again later.</div>",
                    unsafe_allow_html=True,
                )

with col2:
    # Contact information and map/image
    st.markdown("<h2>Reach Us Out</h2>", unsafe_allow_html=True)
    st.markdown(
    """
    <p><span class='contact-icon' style='color:#FF6B6B;'><i class="fa fa-envelope"></i></span>nexzonsolutions@gmail.com</p>
    <p><span class='contact-icon' style='color:#4AC29A;'><i class="fa fa-phone"></i></span> 051-5151437-38</p>
    <p><span class='contact-icon' style='color:#1E90FF;'><i class="fa fa-map-marker"></i></span>Foundation University Rawalpindi Campus</p>
    """,
    unsafe_allow_html=True,
    )
    
    # Add a map using folium
    map_center = [33.56118645224043, 73.07151744232765]  
    m = folium.Map(location=map_center, zoom_start=17)
    folium.Marker(
        location=map_center,
        popup="Your Location",
        icon=folium.Icon(color="blue", icon="info-sign"),
    ).add_to(m)
    st_folium(m, width=1000, height=500)
