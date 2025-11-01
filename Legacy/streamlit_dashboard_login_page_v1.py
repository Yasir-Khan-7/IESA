import streamlit as st

# Set page configuration
st.set_page_config(page_title="Login Page", layout="wide")

# Custom CSS for styling
st.markdown(
    """
    <style>
  
    .stApp{
    margin-top:-30px;
   background-color: white;
 


    }
    header{
      border-bottom: 3px solid  #136a8a !important; 

    }
    /* General layout styling */
    div[data-testid="stColumn"]:first-child {
        padding: 50px;
         margin-right:  -15px;
         border-top: 2px solid lightgrey;
         border-left:  2px solid lightgrey;
         border-bottom:  2px solid lightgrey;
         border-radius: 10px;
    }
    div[data-testid="stColumn"]:nth-child(2) {
    padding:0;
    background: linear-gradient(to right, #73C8A9, #0b8793);
    color: white;
    border-radius: 10px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items:center;
    text-align:center;
  
   
}
    /* Text styling */
    h1 {
        font-size: 36px;
        margin-bottom: 10px;
        font-weight: bold;
        color: #1a1a1a;
    }
    
     div[data-testid="stColumn"]:nth-child(2) h2{
        font-size: 24px !important;
        padding:0 !important;
        margin-left:25px;
        margin-bottom:8px;
        font-weight: bold;
        color: white;"
    
        
    }
    h5 {
        font-size: 18px;
        margin-bottom: 5px;
        color: #333333;
    }
    .required-fields {
        font-size: 14px;
        margin-bottom: 15px;
        color: grey;
    }
    
    /* Input field styling */
    .stTextInput  {
       
        width: 80%;
    }
    .stTextInput > div{
         border: 1px solid lightgrey;
        
    }
    /* Login button styling */
    div[data-testid="stButton"] > button {
        width: 80%;
        background-color: #4AC29A;
        color: white;
        font-size: 16px;
        font-weight: bold;
        border: none;
        border-radius: 5px;
        padding: 10px;
       
        cursor: pointer;
    }
    div[data-testid="stButton"] > button:hover {
      background-color: #44A08D;
      color: white;
    }

    /* Forgot password link */
    .forgot-password {
        margin-top: 10px;
        font-size: 14px;
        color: #49a09d !important;
        text-decoration: none;
        cursor: pointer;
        
    }
    .forgot-password:hover {
        text-decoration: underline;
    }

    /* Register section styling */
    div[data-testid="stColumn"]:nth-child(2) h2 {
        font-size: 28px;
        font-weight: bold;
    }
    
    /* Target specific image styling */
    div[data-testid="stColumn"]:nth-child(2) img {
        border: 2px solid #4AC29A; /* Add border */
        border-radius: 10px; /* Make corners rounded */
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); /* Add shadow */
        width:500px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Layout with two columns
col1, col2 = st.columns([0.7, 1])  # Adjust width ratio

# Left column: Login form
with col1:
    st.markdown("<h1>Welcome to IESA</h1>", unsafe_allow_html=True)
    st.markdown("<h5>Log in to your account.</h5>", unsafe_allow_html=True)
    st.markdown("<div class='required-fields'>Enter your username and password to login</div>", unsafe_allow_html=True)

    username = st.text_input("",placeholder="Username")
    password = st.text_input("", type="password",placeholder="Password")
     # Add forgot password link
    st.markdown('<a class="forgot-password">Forgot Password?</a>', unsafe_allow_html=True)
    if st.button("Login"):
        st.success("Login successful!")

   

# Right column: Register section
with col2:
  
    
    st.image("energy_centered_image.png")
    st.markdown(
        """
        <h2>
            Discover Intelligent Energy Solutions
        </h2>
        <p style="font-size: 14px; color: lightgrey;">
            Join IESA today to optimize energy usage and unlock smart analytics.
        </p>
        """,
        unsafe_allow_html=True,
    )