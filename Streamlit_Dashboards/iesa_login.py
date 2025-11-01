import streamlit as st
from mysql_con import validate_user
import os
from utils.logger import setup_logger

# Setup logger
logger = setup_logger("iesa_login")
logger.info("IESA Login page loaded")

st.set_page_config(
    page_title="Login Page",
    page_icon="🔒",
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

# Custom CSS for styling
st.markdown(
    """
    <style>
    /* Application Wrapper Styling */
    .stApp {
        margin-top: -30px;
        background-color: white;
    }

    /* Header Styling */
    header {
        border-bottom: 3px solid #0b8793 !important;
    }

    /* General Layout Styling */
    div[data-testid="stColumn"]:first-child {
        padding: 50px;
        margin-right: -15px;
        border-top: 2px solid #dddddd;
        border-left: 2px solid #dddddd;
        border-bottom: 2px solid #dddddd;
        border-radius: 10px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
    }

    div[data-testid="stColumn"]:nth-child(2) {
        padding: 0;
        background: linear-gradient(135deg, #73C8A9, #0b8793);
        color: white;
        border-radius: 10px;
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.15);
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        text-align: center;
    }

    /* Text Styling */
    h1 {
        font-size: 38px;
        margin-bottom: 15px;
        font-weight: bold;
        color: #0F403F;
        text-shadow: 1px 1px 0px rgba(255, 255, 255, 0.5);
    }

    div[data-testid="stColumn"]:nth-child(2) h2 {
        font-size: 28px !important;
        padding: 0 !important;
        margin-left: 25px;
        margin-top: 20px;
        margin-bottom: 12px;
        font-weight: bold;
        color: white;
        text-shadow: 1px 1px 3px rgba(0, 0, 0, 0.2);
    }

    h5 {
        font-size: 20px;
        margin-bottom: 8px;
        color: #333333;
        font-weight: 500;
    }

    .required-fields {
        font-size: 16px;
        margin-bottom: 20px;
        color: #666666;
        font-style: italic;
    }

    /* Input Field Styling*/
    .stTextInput {
        width: 80%;
        margin-bottom: 15px;
    }

    .stTextInput > div {
        border: 1px solid #cccccc;
        border-radius: 5px;
        padding: 4px;
        background-color: #f9f9f9;
    }
    
    .stTextInput > div:focus-within {
        border: 2px solid #4AC29A !important;
        box-shadow: 0 0 5px rgba(74, 194, 154, 0.3);
    }
    
    /* Input placeholder styling */
    .stTextInput input::placeholder {
        color: black !important;
        font-weight: 400;
        font-size: 15px;
    }

    /* Login Button Styling */
    div[data-testid="stButton"] > button {
        width: 80%;
        background-color: #4AC29A;
        color: white;
        font-size: 17px;
        font-weight: bold;
        border: none;
        border-radius: 5px;
        padding: 12px;
        cursor: pointer;
        transition: all 0.2s ease-in-out;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-top: 10px;
    }

    div[data-testid="stButton"] > button:hover {
        background-color: #44A08D;
        color: white;
        transform: translateY(-2px);
        box-shadow: 0 6px 8px rgba(0, 0, 0, 0.15);
    }
    
    /* Styling for Success and Error Messages */
    .stAlert {
        width: 80%;
        border-radius: 5px;
        font-size: 15px;
        font-weight: bold;
    }

    /* Custom Success Message Styling */
    .custom-success {
        background-color: #0b8793;
        color: #FFFFFF;
        padding: 15px;
        border-radius: 5px;
        margin: 15px 0;
        width: 80%;
        font-size: 16px;
        font-weight: bold;
        box-shadow: 0 4px 6px rgba(11, 135, 147, 0.2);
        border-left: 5px solid #066570;
    }

    /* Custom Error Message Styling */
    .custom-error {
        background-color: #FF6B6B;
        color: #FFFFFF;
        padding: 15px;
        border-radius: 5px;
        margin: 15px 0;
        width: 80%;
        font-size: 16px;
        font-weight: bold;
        box-shadow: 0 4px 6px rgba(255, 107, 107, 0.2);
        border-left: 5px solid #E84C4C;
    }
 div[data-testid="stColumn"]:nth-child(2) div[data-testid="stFullScreenFrame"] {
          
            display:flex;
            justify-content: center;
            align-items: center;
           
        }
    /* Responsive Design for Columns */
    @media (max-width: 768px) {
        div[data-testid="stColumn"] {
            flex: 1 1 100%;
            margin: 10px 0;
        }
        div[data-testid="stColumn"]:nth-child(2) img {
            width: 70%; /* Adjust max width for smaller screens */
        }
    }
    
    /* Target specific image styling */
    div[data-testid="stColumn"]:nth-child(2) img {
        border: 3px solid #4AC29A; /* Thicker border */
        border-radius: 12px; /* Make corners more rounded */
        box-shadow: 0 8px 15px rgba(0, 0, 0, 0.15); /* Enhanced shadow */
        width: 100%; /* Adjust width dynamically */
        max-width: 500px; /* Limit the maximum width */
        height: auto; /* Maintain aspect ratio */
        object-fit: contain; /* Ensures the image fits within its container */
        transition: transform 0.3s ease;
    }
    
    div[data-testid="stColumn"]:nth-child(2) img:hover {
        transform: scale(1.02); /* Subtle zoom effect on hover */
    }

    /* Secondary button (Contact us) styling */
    div[data-testid="stButton"] button[data-testid="stBaseButton-secondary"]:nth-of-type(1) {
        background-color: transparent !important;
        color: #0b8793 !important;
        border: none !important;
        font-size: 15px !important;
        float: right;
        padding: 20px !important;
        cursor: pointer;
        width: 58%;
        font-weight: 600;
        transition: all 0.2s ease;
    }
    
    div[data-testid="stButton"] button[data-testid="stBaseButton-secondary"]:nth-of-type(1):hover {
        text-decoration: underline !important;
        color: #44A08D !important;
        transform: translateY(-1px);
    }
    
    /* Right column text styling */
    div[data-testid="stColumn"]:nth-child(2) p {
        font-size: 16px !important;
        color: rgba(255, 255, 255, 0.9) !important;
        line-height: 1.5;
        margin-left: 25px;
        margin-right: 25px;
        margin-bottom: 25px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Layout with two columns
col1, col2 = st.columns([0.7, 1])  # Adjust width ratio

# Left column: Login form
with col1:
    st.image("images/iesa_green.svg", width=170)
    st.markdown("<h1>Welcome to IESA</h1>", unsafe_allow_html=True)
    st.markdown("<h5>Log in to your account.</h5>", unsafe_allow_html=True)
    st.markdown("<div class='required-fields'>Enter your username and password to login</div>", unsafe_allow_html=True)

    username = st.text_input("", placeholder="Username *")
    password = st.text_input("", type="password", placeholder="Password *")
    logger.info(f"Login form loaded. Username field: {username}, Password field: {'***' if password else ''}")

    login = st.button("Login", type="primary")

    if login:
        logger.info(f"Login attempt for username: {username}")
        if not username and not password:
            logger.warning("Login attempt failed: Both username and password are empty")
            st.toast("Please enter both username and password.", icon="⚠️")
            st.markdown(
                "<div class='custom-error'>⚠️ Please enter both username and password.</div>",
                unsafe_allow_html=True,
            )
        elif not username:
            logger.warning("Login attempt failed: Username is empty")
            st.toast("Please enter your username.", icon="⚠️")
            st.markdown(
                "<div class='custom-error'>⚠️ Please enter your username.</div>",
                unsafe_allow_html=True,
            )
        elif not password:
            logger.warning("Login attempt failed: Password is empty")
            st.toast("Please enter your password.", icon="⚠️")
            st.markdown(
                "<div class='custom-error'>⚠️ Please enter your password.</div>",
                unsafe_allow_html=True,
            )
        else:
            try:
                if validate_user(username, password):
                    logger.info(f"Successful login for user: {username}")
                    st.toast("Login successful!", icon="✅")
                    st.markdown(
                        "<div class='custom-success'>✅ Login successful!</div>",
                        unsafe_allow_html=True,
                    )
                    if(username=="inputentryoperator@iesa"):
                        logger.info(f"Redirecting user {username} to input entry operator page")
                        os.system("streamlit run iesa_input_entry_operator.py")  
                    else:
                        logger.info(f"Redirecting user {username} to data planner page")
                        os.system("streamlit run iesa_data_planner.py")
                else:
                    logger.warning(f"Failed login attempt for user: {username}")
                    st.toast("Invalid username or password.", icon="❌")
                    st.markdown(
                        "<div class='custom-error'>⚠️ Invalid username or password. Please try again.</div>",
                        unsafe_allow_html=True,
                    )
            except Exception as e:
                logger.error(f"Error during login validation for user {username}: {e}")
                st.toast("An error occurred during login. Please try again later.", icon="❌")
                st.markdown(
                    f"<div class='custom-error'>⚠️ An error occurred during login. Please try again later.</div>",
                    unsafe_allow_html=True,
                )
    # Add the "Contact Us" button
    if st.button("Contact us", type="secondary"):
        logger.info("User clicked Contact Us from Login page (navigating to Contact Us page)")
        os.system("streamlit run iesa_contact_us.py")
# Right column: Display image and text
with col2:
    st.image("images/energy_centered_image.png", width=500)
    st.markdown(
        """
        <h2>
            Discover Intelligent Energy Solutions
        </h2>
        <p style="font-size: 16px;">
            Join IESA today to optimize energy usage and unlock smart analytics for sustainable future.
        </p>
        """,
        unsafe_allow_html=True,
    )
