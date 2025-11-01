import streamlit as st
import pyperclip

def custom_hash(input_string):
    hash_val = 0
    prime = 31  # prime number for Mixing
    mod = 2**32  # Limiit to 32-bit unsigned integer for memeory optimizatin
    for char in input_string:
        hash_val = (hash_val * prime + ord(char)) % mod
    return hex(hash_val)[2:].zfill(12)  # Convert to hex with consistent length by zero-padding

# Set page config
# st.set_page_config(page_title="Password Hash Generator", page_icon="🔒")
st.set_page_config(
    page_title="Password Hash Generator",
    page_icon="🔒",
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
            "• M. Farzam Baig\n"
 )
}
)

# Custom styling
st.markdown("""
<style>
    .main {
        padding: 2rem;
    }
    .header {
        text-align: center;
        color: #0b8793;
        margin-bottom: 2rem;
    }
    .stTextInput > div > div > input {
        padding: 0.5rem;
        font-size: 1rem;
        border: 2px solid #0b8793;
        border-radius: 5px;
    }
    .success-message {
        color: green;
        font-weight: bold;
        padding: 0.5rem;
        animation: fadeOut 2s forwards;
        animation-delay: 1s;
    }
    .hash-output {
        padding: 1rem;
        background-color: #f8f9fa;
        border-radius: 5px;
        font-family: monospace;
        margin: 1rem 0;
        border-left: 4px solid #0b8793;
    }
    .stButton button {
        background-color: #0b8793;
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 5px;
        border: none;
        cursor: pointer;
        font-weight: bold;
        width: 100%;
    }
    .stButton button:hover {
        background-color: #4AC29A;
        transform: translateY(-2px);
        transition: all 0.3s;
    }
    @keyframes fadeOut {
        from {opacity: 1;}
        to {opacity: 0;}
    }
</style>
""", unsafe_allow_html=True)

# Page header
st.markdown("<h1 class='header'>Password Hash Generator</h1>", unsafe_allow_html=True)

# Input field
password_input = st.text_input("Enter Password", type="password", key="password")

# Generate button
if st.button("Generate Hash"):
    if password_input:
        hashed_val = custom_hash(password_input)
        st.session_state.hashed_password = hashed_val
        st.markdown(f"<div class='hash-output'>{hashed_val}</div>", unsafe_allow_html=True)
    else:
        st.warning("Please enter a password to hash")

# Copy button (only show if there's a hashed password)
if 'hashed_password' in st.session_state:
    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("Copy Hash"):
            pyperclip.copy(st.session_state.hashed_password)
            st.markdown("<div class='success-message'>Copied to clipboard!</div>", unsafe_allow_html=True)
