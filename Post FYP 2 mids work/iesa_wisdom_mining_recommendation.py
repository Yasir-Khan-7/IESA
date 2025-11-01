import streamlit as st
import asyncio
import pandas as pd
import mysql.connector
from pydantic_ai import Agent
from pydantic_ai.models.groq import GroqModel
from pydantic_ai.providers.groq import GroqProvider
import random
from streamlit_option_menu import option_menu
import io
import os
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.utils import ImageReader
from textwrap import wrap

# Initialize sidebar state
if 'sidebar_state' not in st.session_state:
    st.session_state.sidebar_state = 'expanded'
if 'button_text' not in st.session_state:
    st.session_state.button_text = '← Hide'
if 'needs_rerun' not in st.session_state:
    st.session_state.needs_rerun = False
if 'toggle_triggered' not in st.session_state:
    st.session_state.toggle_triggered = False

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
# Local image path (Replace with your actual image path)
image_path = "images/iesa_green.svg"
# Load logo

# Apply Custom CSS for Chat Styling
st.markdown(
    """
    <style>
    header {
        border-bottom: 3px solid  #136a8a !important; 
        margin-bottom: 0 !important;
        position: relative !important;
        z-index: 99 !important;
    }
    [data-testid="stSidebar"] {
        background: linear-gradient(135deg, #73C8A9, #0b8793); /* Gradient background */
        color: white;
        margin-top: -10px;
        box-shadow: 2px 0 10px rgba(0,0,0,0.2);
        z-index: 98;
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
        margin: 5px auto;
        font-size: 14px;
        white-space: nowrap;
        display: block;
    }
    #MainMenu, footer, header {
        visibility: hidden;
    }
    div[data-testid="stHorizontalBlock"] > div .stButton button:hover {
        background-color: #4AC29A;
        transform: translateY(-1px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    
    /* Toggle button specific styles - target the first button in the first column */
    div[data-testid="stHorizontalBlock"] > div:first-child .stButton button {
        position: relative;
        z-index: 999;
        width: auto !important;
        min-width: 60px;
        max-width: 80px;
    }
    
    /* Highlighted button (active page) */
    [data-testid="stHorizontalBlock"] div:nth-child(5) .stButton button {
        background-color: #4AC29A !important;
        box-shadow: 0 4px 8px rgba(0,0,0,0.25) !important;
        border: 2px solid #73C8A9 !important;
        position: relative;
        transform: translateY(-2px);
    }
    
    /* Add a small indicator below the active button */
    [data-testid="stHorizontalBlock"] div:nth-child(5) .stButton button::after {
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

    [data-testid="stSidebar"]
    .sidebar-content {
        margin-top: -60px;
        padding: 20px;
    }
     [data-testid="stSidebarHeader"]{
     display: none;
     }
     h1{
     font-size: 32px !important;
     margin-top: 10px !important;
     text-align: center;
     text-shadow: 1px 1px 2px rgba(0,0,0,0.2);
     letter-spacing: 0.5px;
     }
    .logo-title-container {
        display: flex;
        flex-direction: row;
        align-items: center;
        justify-content: space-between;
    }
    .logo img {
        width: 60px;
        border-radius: 50%;
    }
    .app-name {
        font-size: 1.5em;
        font-weight: bold;
    }
    
    
    [data-testid="stSidebar"] h2 {
        font-size: 22px !important;
        margin-top: 0 !important;
        margin-bottom: 15px !important;
        padding-bottom: 5px;
        border-bottom: 2px solid rgba(255,255,255,0.3);
        text-shadow: 1px 1px 2px rgba(0,0,0,0.2);
    }
    
    [data-testid="stSidebar"] p {
        color: rgba(255,255,255,0.9) !important;
        font-weight: 500;
        margin-bottom: 8px;
    }
    
    [data-testid="stSidebar"] label {
        color: white !important;
        font-weight: 500;
        font-size: 15px;
        margin-bottom: 5px;
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
    
    [data-testid="stBaseButton-secondary"]{
            
            background-color: #0b8793 !important;
             width:100% !important;
             border: 1px solid #4AC29A;
            border-radius: 5px;
            }

      [data-testid="stBaseButton-secondary"]:hover {
        background-color: #0b8793;
        color: white !important;
    }       
    .stButton button {
        width:100%;
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

    .stButton button:hover {
        background-color: #4AC29A;
        color: white !important;
        box-shadow: 0 3px 7px rgba(0,0,0,0.15);
        transform: translateY(-1px);
    }
    
    .chat-container {
        display: flex;
        flex-direction: column;
        gap: 10px;
        padding: 10px;
    }
    .user-container {
        display: flex;
        align-content: flex-end;
        justify-content: flex-end;
        align-items: flex-end;
        font-size: 15px;
    }
    .bot-container {
        font-size: 15px;
    }
    .user-msg {
        width: fit-content;
        background-color: #e9f5ff;
        color: #222;
        padding: 12px 18px;
        border-radius: 18px 18px 0 18px;
        text-align: right;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        border: 1px solid #c9e6ff;
        font-weight: 500;
        letter-spacing: 0.2px;
        line-height: 1.4;
    }
    .bot-msg {
        width: fit-content;
        background-color: #f8f0e5;
        color: #222;
        padding: 12px 18px;
        border-radius: 18px 18px 18px 0;
        text-align: left;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        border: 1px solid #f1e2cc;
        font-weight: 500;
        letter-spacing: 0.2px;
        line-height: 1.4;
    }
    .chat-header {
        text-align: center;
        font-size: 24px;
        font-weight: bold;
        margin-bottom: 10px;
    }
    .chat-description {
        text-align: center;
        color: gray;
        font-size: 14px;
        margin-bottom: 20px;
    }
    
    /* Enhanced chat input styling */
    .stChatInput {
        background-color: white;
        border-radius: 30px !important;
        border: 2px solid #0b8793 !important;
        padding: 8px 15px !important;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1) !important;
        margin: 15px 0 !important;
    }
    
    .stChatInput:focus-within {
        border-color: #4AC29A !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15) !important;
    }
    
    [data-testid="stChatInput"] {
        padding: 0 !important;
        margin-bottom: 20px !important;
    }
    
    [data-testid="stChatInput"] > div {
        padding: 0 !important;
    }
    
    /* Input field container */
    [data-testid="stChatInputContainer"] {
        background-color: white !important;
        border-radius: 30px !important;
        border: 2px solid #0b8793 !important;
        padding: 5px 10px !important;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1) !important;
    }
    
    /* Input field */
    .stChatInput textarea, [data-testid="stChatInput"] textarea {
        padding: 10px 15px !important;
        font-size: 16px !important;
        background-color: transparent !important;
        border: none !important;
    }
    
    /* Fix placeholder text */
    [data-testid="stChatInput"] textarea::placeholder {
        color: #888 !important;
        font-size: 16px !important;
        font-weight: 400 !important;
        opacity: 0.8 !important;
    }
    
    /* Send button */
    [data-testid="stChatInputSubmitButton"] {
        background-color: #0b8793 !important;
        color: white !important;
        border-radius: 50% !important;
        box-shadow: 0 2px 5px rgba(0,0,0,0.2) !important;
        margin-right: 5px !important;
        width: 38px !important;
        height: 38px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        transform: translateY(0) !important;
    }
    
    [data-testid="stChatInputSubmitButton"]:hover {
        background-color: #4AC29A !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 8px rgba(0,0,0,0.25) !important;
    }
    
    [data-testid="stChatInputSubmitButton"] svg {
        fill: white !important;
        width: 20px !important;
        height: 20px !important;
    }
    
    [data-testid="stFullScreenFrame"]{
        display: flex;
        align-content: center;
        justify-content: center;
    }
    
    /* Remove extra spacing at the top */
    .block-container {
        padding-top: 0.1rem !important;
    }
    
    /* Adjust header margin */
    header {
        margin-bottom: 0 !important;
    }
    
    /* Main wrapper for streamlit app */
    .main .block-container {
        padding-top: 0.5rem !important;
        margin-top: 0 !important;
    }
    
    /* Fix for option menu container positioning */
    section[data-testid="stSectionContainer"] {
        position: relative;
        z-index: 100;
    }
    
    /* Adjust top margin for button row */
    div[data-testid="stHorizontalBlock"] {
        margin-top: 10px !important;
        margin-bottom: 20px !important;
    }
    
    /* Main content spacing adjustments */
    .main .block-container > div:nth-child(1) {
        margin-top: 5px !important;
    }
    
    /* Logo specific spacing */
    img {
        margin-top: 10px !important;
        margin-bottom: 10px !important;
    }
    
    /* Page title and description spacing */
    .main p {
        margin-top: 10px !important;
    }
    
    /* Style the option menu for better appearance */
    [data-testid="stHorizontalBlock"] .stButton button {
        border-radius: 6px !important;
    }
    
    /* Improved navigation styles */
    .nav-link {
        transition: all 0.3s ease !important;
        border-radius: 6px !important;
    }
    
    .nav-link:hover {
        transform: translateY(-2px) !important;
    }
    
    /* Style for the active navigation item - bottom bar instead of background */
    .nav-link-selected {
        background-color: transparent !important;
        position: relative !important;
        box-shadow: none !important;
    }
    
    /* Add bottom bar to active navigation item */
    .nav-link-selected::after {
        content: '' !important;
        position: absolute !important;
        bottom: -3px !important;
        left: 10% !important;
        width: 80% !important;
        height: 4px !important;
        background-color: #e53935 !important; 
        border-radius: 2px !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.2) !important;
    }
    
    /* Make the active tab text color the original color */
    .nav-link-selected {
        color: #106466 !important; 
        font-weight: bold !important;
    }
    
    /* Remove any background from active tab */
    .stTabs [data-baseweb="tab-list"] [data-baseweb="tab"][aria-selected="true"] {
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
    
    /* Remove grey background from navigation container */
    section[data-testid="stSectionContainer"] div[data-testid="stVerticalBlock"] {
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
    </style>
    """,
    unsafe_allow_html=True,
)

selected = option_menu(
    menu_title=None,
    options=["Dashboard","Data Planner", "Scenario","Wisdom Mining", "Prediction", "IESA Assistant"],
    icons=["clipboard-data", "bar-chart", "graph-up", "graph-up-arrow", "robot", "robot"],
    default_index=5,
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
if selected == "Data Planner":
    os.system("streamlit run iesa_data_planner.py")

elif selected == "Dashboard":
    os.system("streamlit run iesa_dashboard.py")
elif selected == "Scenario":
    os.system("streamlit run iesa_scenerio_analysis_with_k_means.py")

elif selected == "Prediction":
     os.system("streamlit run iesa_prediction_engine.py")

elif selected == "Wisdom Mining":
    os.system("streamlit run iesa_wisdom_mining.py")
     

# # Add the toggle button at the top with a narrower column
# toggle_col1, btn_col1, btn_col2, btn_col3, btn_col4 = st.columns([1, 2, 2, 2, 2])
# with toggle_col1:
#     st.button(st.session_state.button_text, key="toggle_sidebar_button", on_click=toggle_sidebar)
# with btn_col1:
#     data_planner_button = st.button("Data Planner", key="data_planner_button")
# with btn_col2:
#     scenario_button = st.button("Scenario", key="scenario_analysis_button")
# with btn_col3:
#     prediction_button = st.button("Prediction", key="prediction_engine_button")
# with btn_col4:
#     assistant_button = st.button("IESA Assistant", key="personalized_recommendation_button")

# # Handle button clicks
# if data_planner_button:
#     os.system("streamlit run iesa_data_planner.py")
# if scenario_button:
#     os.system("streamlit run iesa_scenerio_analysis.py")
# if prediction_button:
#     os.system("streamlit run iesa_prediction_engine.py")

api_keys = []

api_index = 0

def get_model():
    global api_index
    for _ in range(len(api_keys)):
        api_key = api_keys[api_index]
        api_index = (api_index + 1) % len(api_keys)
        try:
            return GroqModel(
                'llama-3.3-70b-versatile', 
                provider=GroqProvider(api_key=api_key)
            )
        except Exception:
            continue
    return None

def get_connection():
    return mysql.connector.connect(
        host="localhost",
        port="3306",
        user="root",
        passwd="admin123",
        db="iesa_db"
    )

def fetch_tables():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SHOW TABLES")
        tables = [table[0] for table in cursor.fetchall() if table[0] != "user_data"]
        conn.close()
        return tables
    except Exception as e:
        st.error(f"Error fetching tables: {e}")
        return []

def fetch_table_data(table_name):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        query = f"SELECT * FROM {table_name}"
        cursor.execute(query)
        rows = cursor.fetchall()
        data = pd.DataFrame(rows, columns=[desc[0] for desc in cursor.description])
        conn.close()
        return data
    except Exception as e:
        st.error(f"Error fetching data from {table_name}: {e}")
        return pd.DataFrame()

# Fetch scenario categories
def fetch_scenario_categories():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT category FROM scenario_definitions")
        categories = [row[0] for row in cursor.fetchall()]
        conn.close()
        return categories
    except Exception as e:
        st.error(f"Error fetching scenario categories: {e}")
        return []

# Fetch scenarios based on selected category
def fetch_scenarios(category):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        query = "SELECT scenario FROM scenario_definitions WHERE category = %s"
        cursor.execute(query, (category,))
        scenarios = [row[0] for row in cursor.fetchall()]
        conn.close()
        return scenarios
    except Exception as e:
        st.error(f"Error fetching scenarios: {e}")
        return []

st.sidebar.markdown("""
    <h1>IESA Assistant</h1>
""",unsafe_allow_html=True)
# Sidebar UI for scenario selection
st.sidebar.header("Table Selection")
# Add sidebar with table selection and action buttons
tables = fetch_tables()
selected_table = st.sidebar.selectbox("Select a Table", tables)


if "knowledge_base" not in st.session_state:
    st.session_state.knowledge_base = ""
    tables = fetch_tables()
    for table in tables:
        data = fetch_table_data(table)
        st.session_state.knowledge_base += f"\nTable: {table}\n{data.to_string(index=False)}\n"

if "conversation_history" not in st.session_state:
    st.session_state.conversation_history = []



async def get_response(user_input):
    st.session_state.conversation_history.append({"role": "user", "content": user_input})

    last_message = st.session_state.conversation_history[-1]  # Keep only the last user input

    for _ in range(len(api_keys)):
        model = get_model()
        if model:
            try:
                agent = Agent(model=model)
                
                # Only use the last user message while keeping the full knowledge base
                conversation_text = f"User: {last_message['content']}"

                prompt = """🔹 IESA AI Assistant: Provide energy-saving recommendations based on the user's query.
                Suggest cost-effective strategies even if no cost data is available.
                Consider solar panels, battery storage, and demand-side management as options"""

                result = await agent.run(prompt + "\n" + st.session_state.knowledge_base + "\n" + conversation_text)
                response = result.data
                st.session_state.conversation_history.append({"role": "assistant", "content": response})
                return response

            except Exception as e:
                st.warning(f"API call failed, switching API key... ({e})")
                await asyncio.sleep(5)  # Wait before switching API key

    return "Sorry, all API keys failed. Please try again later."

# Add extra spacing before content
st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)

st.image(image_path,width=160)

st.markdown(
    "<p style='text-align: center; color: #666; font-size: 18px; font-weight: 600; margin: 15px 0; line-height: 1.5;'>Your Intelligent Energy Scenario Analysis (IESA) assistant.<br>"
    "Analyze energy consumption, explore future scenarios, and receive personalized recommendations.</p>",
    unsafe_allow_html=True,
)

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    role_class = "user-msg" if message["role"] == "user" else "bot-msg"
    container_class = "user-container" if message["role"] == "user" else "bot-container"
    icon = "💬" if message["role"] == "user" else "⚡"
    st.markdown(
        f'<div class="chat-container {container_class}"><div class="{role_class}">{icon} {message["content"]}</div></div>',
        unsafe_allow_html=True
    )

user_input = st.chat_input("Type your message...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.spinner("Thinking..."):
        bot_reply = asyncio.run(get_response(user_input))
    st.session_state.messages.append({"role": "assistant", "content": bot_reply})
    st.rerun()


# Define buttons and actions
buttons = ["View Data", "Analyze Trends", "Generate Report"]
for btn in buttons:
    if st.sidebar.button(btn):
        user_input = f"{selected_table} - {btn}"
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.spinner("Thinking..."):
            bot_reply = asyncio.run(get_response(user_input))
        st.session_state.messages.append({"role": "assistant", "content": bot_reply})
        st.rerun()

# Sidebar UI for scenario selection
st.sidebar.header("Scenario Selection")

categories = fetch_scenario_categories()
selected_category = st.sidebar.selectbox("Select Category", categories)

if selected_category:
    scenarios = fetch_scenarios(selected_category)
    selected_scenario = st.sidebar.selectbox("Select Scenario", scenarios)

    # Display buttons for actions
    if selected_scenario:
        

        if st.sidebar.button("Generate Recommendation", key=f"rec_{selected_scenario}"):
            user_input = f"Generate recommendation for {selected_scenario}"
            st.session_state.messages.append({"role": "user", "content": user_input})
            with st.spinner("Thinking..."):
                bot_reply = asyncio.run(get_response(user_input))
            st.session_state.messages.append({"role": "assistant", "content": bot_reply})
            st.rerun()

        if st.sidebar.button("Analyze Trends", key=f"trends_{selected_scenario}"):
            user_input = f"Analyze trends for {selected_scenario}"
            st.session_state.messages.append({"role": "user", "content": user_input})
            with st.spinner("Thinking..."):
                bot_reply = asyncio.run(get_response(user_input))
            st.session_state.messages.append({"role": "assistant", "content": bot_reply})
            st.rerun()

        if st.sidebar.button("Generate Report", key=f"report_{selected_scenario}"):
            user_input = f"Generate report for {selected_scenario}"
            st.session_state.messages.append({"role": "user", "content": user_input})
            with st.spinner("Generating report..."):
                bot_reply = asyncio.run(get_response(user_input))
            st.session_state.messages.append({"role": "assistant", "content": bot_reply})
            st.rerun()

# Function to create PDF report for recommendations
def create_recommendation_report(messages=None):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    
    # Header with orange line and logo
    header_y = height - 45
    
    # Add orange line at top
    c.setStrokeColor(colors.HexColor("#F06C00"))  # Orange color
    c.setLineWidth(2)
    c.line(20, header_y, width - 20, header_y)
    
    # Add logo
    logo_path = "images/iesa_green.png"
    if os.path.exists(logo_path):
        logo = ImageReader(logo_path)
        c.drawImage(logo, width - 80, height - 42, width=60, height=24, mask='auto')
    
    # Title with proper spacing
    c.setFillColor(colors.HexColor("#504B38")) 
    c.setFont("Helvetica-Bold", 22)
    title_text = "IESA Recommendation Report"
    c.drawString((width - c.stringWidth(title_text, "Helvetica-Bold", 22)) / 2, height - 100, title_text)
    
    # Add description
    c.setFillColor(colors.black)
    c.setFont("Helvetica", 11)
    description = "This shows the conversation between you and the IESA Assistant with personalized energy recommendations."
    
    # Center the description
    desc_width = c.stringWidth(description, "Helvetica", 11)
    c.drawString((width - desc_width) / 2, height - 130, description)
    
    # Horizontal line
    c.setStrokeColor(colors.HexColor("#0b8793"))
    c.setLineWidth(1)
    c.line(60, height - 160, width - 60, height - 160)
    
    # Check if we have messages
    if messages and len(messages) > 0:
        # Draw section title for conversations
        conversation_y = height - 190
        c.setFillColor(colors.HexColor("#0b8793"))
        c.setFont("Helvetica-Bold", 16)
        c.drawString(60, conversation_y, "Energy Advisory Dialogue")
        
        # Add the conversation content
        content_y = conversation_y - 30
        
        page_number = 1
        
        # Process all messages in conversation
        for i, message in enumerate(messages):
            # Set colors and styles based on role
            if message["role"] == "user":
                # User message styling
                c.setFillColor(colors.HexColor("#136a8a"))  # Blue for user
                icon = "🧑"
                prefix = "User: "
            else:
                # Assistant message styling
                c.setFillColor(colors.HexColor("#4AC29A"))  # Green for assistant
                icon = "🤖"
                prefix = "IESA Assistant: "
            
            # Add message header with icon
            c.setFont("Helvetica-Bold", 12)
            message_header = f"{icon} {prefix}"
            c.drawString(40, content_y, message_header)
            content_y -= 20
            
            # Add message content
            c.setFillColor(colors.black)
            c.setFont("Helvetica", 10)
            
            # Add bubble-like background for the message
            if message["role"] == "user":
                bubble_color = colors.HexColor("#e9f5ff")  # Light blue background for user
            else:
                bubble_color = colors.HexColor("#f0f8f1")  # Light green background for assistant
            
            # Split the message into paragraphs
            paragraphs = message["content"].split('\n')
            
            for paragraph in paragraphs:
                if paragraph.strip():  # Skip empty paragraphs
                    # Wrap text to fit page width
                    wrapped_text = wrap(paragraph, width=75)
                    
                    # Calculate bubble height
                    bubble_height = len(wrapped_text) * 15 + 10  # text height + padding
                    
                    # Check if we need a new page
                    if content_y - bubble_height < 60:
                        # Add page number to current page
                        c.setFont("Helvetica", 8)
                        c.setFillColor(colors.gray)
                        c.drawString(width - 80, 15, f"Page {page_number}")
                        
                        # Create new page
                        c.showPage()
                        page_number += 1
                        
                        # Reset position and add header to new page
                        content_y = height - 60
                        
                        # Add orange line at top of new page
                        c.setStrokeColor(colors.HexColor("#F06C00"))
                        c.setLineWidth(2)
                        c.line(20, height - 30, width - 20, height - 30)
                        
                        # Add small report title to continuation pages
                        c.setFillColor(colors.HexColor("#504B38"))
                        c.setFont("Helvetica-Bold", 14)
                        c.drawString(40, height - 50, "IESA Recommendation Report (Continued)")
                    
                    # Draw message bubble
                    c.setStrokeColor(colors.lightgrey)
                    c.setFillColor(bubble_color)
                    if message["role"] == "user":
                        # User bubble (right aligned)
                        bubble_x = 120
                        bubble_width = width - 160
                        c.roundRect(bubble_x, content_y - bubble_height, bubble_width, bubble_height, 8, fill=1, stroke=1)
                    else:
                        # Assistant bubble (left aligned)
                        bubble_x = 60
                        bubble_width = width - 100
                        c.roundRect(bubble_x, content_y - bubble_height, bubble_width, bubble_height, 8, fill=1, stroke=1)
                    
                    # Draw text on bubble
                    c.setFillColor(colors.black)
                    c.setFont("Helvetica", 10)
                    
                    text_y = content_y - 15  # Start position for text
                    for line in wrapped_text:
                        c.drawString(bubble_x + 10, text_y, line)  # 10px padding inside bubble
                        text_y -= 15  # Move down for next line
                    
                    # Update content_y to below this bubble
                    content_y -= bubble_height + 20  # 20px space between messages
            
            # Add more space between different messages
            content_y -= 10
            
            # Add a separator line between different exchanges
            if i < len(messages) - 1 and message["role"] == "assistant" and messages[i+1]["role"] == "user":
                c.setStrokeColor(colors.lightgrey)
                c.setDash(1, 2)  # Dotted line
                c.line(40, content_y, width - 40, content_y)
                c.setDash(1, 0)  # Reset to solid line
                content_y -= 20
    else:
        # No conversation message
        c.setFillColor(colors.red)
        c.setFont("Helvetica", 12)
        c.drawString(60, height - 190, "No conversations have been generated yet.")
    
    # Add page footer
    c.setStrokeColor(colors.HexColor("#4389a2"))
    c.setLineWidth(2)
    c.line(20, 30, width - 20, 30)
    
    # Footer text
    c.setFont("Helvetica", 8)
    c.setFillColor(colors.gray)
    c.drawString(40, 15, "© 2025 IESA. All rights reserved.")
    c.drawString(width - 80, 15, "Page 4")
    
    c.save()
    buffer.seek(0)
    return buffer

# Move the Report Options section here to make it more visible
st.sidebar.header("Report Options")

# Add report generation button in a more visible location
if st.session_state.get("messages"):
    st.sidebar.markdown("---")
    st.sidebar.download_button(
        "Download Recommendation Report", 
        create_recommendation_report(st.session_state.messages),
        "IESA_Recommendation_Report.pdf",
        "application/pdf"
    )