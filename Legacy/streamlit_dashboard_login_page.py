import streamlit as st
import os
import base64

# Set page configuration
st.set_page_config(page_title="Login Page", layout="wide")

# Function to convert image to base64 string
def image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        encoded_image = base64.b64encode(image_file.read()).decode()
    return f"data:image/jpeg;base64,{encoded_image}"

# Local image path (Replace with the local path of your image)
image_path = "background.jpg"  # Replace with your local image path

# Convert image to base64 string
image_base64 = image_to_base64(image_path)

st.markdown(
    f"""
    <style>
    /* Import Poppins font from Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');

    body {{
        margin: 0;
        font-family: 'Poppins', sans-serif;
    }}

    /* Gradient for the entire app background with overlay for better text visibility */
    .stApp {{
        background: linear-gradient(rgba(0, 0, 0, 0.5), rgba(0, 0, 0, 0.5)), url("{image_base64}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
    }}

    /* Gradient for the Streamlit header */
    header {{
        background: linear-gradient(135deg, rgba(0, 0, 0, 0.5), rgba(0, 0, 0, 0.5)) !important;
        color: white;
    }}

    /* Style all text input fields */
    .stTextInput input {{
        background-color: #333;  /* Dark background for better contrast */
        color: #fff;  /* White text */
        font-family: 'Poppins', sans-serif;  /* Apply Poppins font */
        padding: 10px;  /* Add some padding for better readability */
        caret-color: white;
    }}
    .stTextInput > div{{
        color:white;
        background: linear-gradient(135deg, #4c2e20, #8b4513); /* Dark brown to burnt orange gradient */
    }}
    .stTextInput svg {{
    fill: white !important;
    }}
    /* Apply gradient with orange tone to input fields */
    input {{
        padding: 10px;
        font-size: 1rem;
        margin-bottom: 20px;
        border-radius: 5px;
        background: linear-gradient(135deg, #4c2e20, #8b4513); /* Dark brown to burnt orange gradient */
        color:#D6CFB4 ;
    }}

    input:focus {{
        border-color: #ff6600; /* Bright orange on focus */
        box-shadow: 0 0 10px rgba(255, 102, 0, 0.8); /* Glow effect on focus */
        background: linear-gradient(135deg, #4c2e20, #8b4513); /* Dark brown to burnt orange gradient */
        color:#D6CFB4 ;
    }}

    /* Style the "show password" icon to match input fields */
    button {{
        background: linear-gradient(135deg, #4c2e20, #8b4513) !important; /* Dark brown to burnt orange gradient */
        border: 2px solid #ffa500; /* Orange border */
        color: white;
        border-radius: 5px;
        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.5); /* Consistent shadow with inputs */
        cursor: pointer;
    }}

    button:hover {{
        background: linear-gradient(135deg, #a0522d, #ff7f50); /* Slightly darker on hover */
        border-color: #ff4500; /* Bright orange on hover */
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.5);
    }}

    /* Updated Button Styling - Using the same gradient style as header */
    .stButton > button {{
        background: linear-gradient(135deg, #4c2e20, #8b4513); /* Dark brown to burnt orange gradient */
        color: white;
        font-size: 1rem;
        padding: 12px 25px;
        border-radius: 25px;
        cursor: pointer;
        margin: 0 auto;  /* Center the button horizontally */
        border: 2px solid rgba(255, 255, 255, 0.5); /* Light border to match the background */
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2); /* Subtle shadow for depth */
    }}

    .stButton > button:hover {{
        background: linear-gradient(135deg, rgba(0, 0, 0, 0.7), rgba(0, 0, 0, 0.7)) !important; /* Darker on hover */
        color: white;
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.3);
    }}

    /* Style for the links in the login form */
    .options {{
        display: flex;
        justify-content: space-between;
        width: 100%;
        margin-top: 10px;
        font-size: 1rem;
        color: white;
    }}

    .options a:hover {{
        color: white;
    }}

    /* Adjust the title and text styles for contrast */
    h1, h2, h3, h4, h5, h6 {{
        font-family: 'Poppins', sans-serif;
    }}

    h1{{
        color:#D6CFB4;
    }}
    p {{
        color:#D6CFB4 !important;
        font-family: 'Poppins', sans-serif;
    }}

    .stTitle {{
    color: #00c9ff !important;  /* Cyan color */
    font-family: 'Poppins', sans-serif;
    }}

    .stText {{
       color:#D6CFB4;
        font-family: 'Poppins', sans-serif;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

# Define the login page
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

def login_page():
    col1, col2 = st.columns([1, 0.5])

    with col1:
        # Use Streamlit container for left side content
        with st.container():
            st.markdown('<h1 style="font-size: 3rem; color: #D6CFB4;;">Welcome to IESA</h1>', unsafe_allow_html=True)
            st.markdown('<p style="font-size: 1.2rem;">IESA leverages AI and advanced analytics to optimize energy use, reduce operational costs, and promote sustainability. By analyzing historical data and forecasting energy patterns, it empowers businesses to make informed decisions for a greener, more efficient future.</p>', unsafe_allow_html=True)

    with col2:
        # Use Streamlit container for right side content (login form)
        with st.container():
            st.title("User Login")

            username = st.text_input("Username", "")
            password = st.text_input("Password", type="password")

            if st.button("Login"):
                if username == "admin" and password == "password123":
                    st.session_state["authenticated"] = True
                    # st.experimental_rerun()
                else:
                    st.error("Invalid username or password. Please try again.")

            col3, col4 = st.columns([1, 1])
            with col3:
                st.checkbox("Remember")
            with col4:
                st.markdown('<a href="#" style="color: white; font-weight: bold;">Forgot password?</a>', unsafe_allow_html=True)

# Define the home page
def home_page():
    st.title("Welcome to the IESA Dashboard")
    st.write("This is the main content of the dashboard.")

# App flow
if st.session_state["authenticated"]:
    home_page()
else:
    login_page()
