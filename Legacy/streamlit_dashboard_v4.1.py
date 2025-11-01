import streamlit as st
import pandas as pd
import plotly.express as px
import base64

# Set page configuration
st.set_page_config(page_title="IESA Dashboard", layout="wide", page_icon="🔌")
st.markdown("""
    <style>
    [data-testid="stSidebar"] {
        background: linear-gradient(135deg, #2980b9, #2c3e50);
        color: #FFFFFF;
    }
    .stApp {
        background-color: #F7F9FB;
    }
    .card {
        padding: 8px;
        border-radius: 15px;
        text-align: center;
        margin: 5px;
        box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);
        color: white;
    }
    .card:nth-child(1) { background: linear-gradient(135deg, #4B79A1, #283E51); }
    </style>
""", unsafe_allow_html=True)

def image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        return f"data:image/jpeg;base64,{base64.b64encode(image_file.read()).decode()}"

# Placeholder image path
image_path = "IESA_logo.png"

# Sidebar
with st.sidebar:
    st.image(image_path)
    st.title("IESA Dashboard")
    st.subheader("Input Data Type")
    input_type = st.selectbox("Select Data Type", ["Energy Data", "Gas Data", "Electricity Data"])
    uploaded_file = st.file_uploader(f"Upload {input_type} File", type=["xlsx"])

if uploaded_file:
    try:
        data = pd.read_excel(uploaded_file)
        st.success("Data uploaded successfully!")

        # Display cards
        st.markdown("### Key Metrics")
        card_cols = st.columns(4)
        with card_cols[0]:
            st.markdown(f'<div class="card">Sum<br><strong>{data.select_dtypes("number").sum().sum()}</strong></div>', unsafe_allow_html=True)
        with card_cols[1]:
            st.markdown(f'<div class="card">Count<br><strong>{data.shape[0]}</strong></div>', unsafe_allow_html=True)
        with card_cols[2]:
            st.markdown(f'<div class="card">Unique<br><strong>{data.nunique().sum()}</strong></div>', unsafe_allow_html=True)
        with card_cols[3]:
            if "Year" in data.columns:
                st.markdown(f'<div class="card">Years<br><strong>{len(data["Year"].unique())}</strong></div>', unsafe_allow_html=True)

        # Filters
        st.markdown("### Filter Data")
        if "Year" in data.columns:
            year_filter = st.multiselect("Select Year(s)", options=data["Year"].unique(), default=data["Year"].unique())
            filtered_data = data[data["Year"].isin(year_filter)] if year_filter else data
        else:
            filtered_data = data

        # Visualizations
        st.markdown("### Visualizations")
        chart_cols = st.columns(2)

        # Bar Chart
        with chart_cols[0]: 
            if "Year" in filtered_data.columns:
                bar_chart = px.bar(filtered_data, x="Year", y="Generation (GWh)", title="Yearly Generation (GWh)")
                st.plotly_chart(bar_chart, use_container_width=True)

        # Line Chart
        with chart_cols[1]:
            line_chart = px.line(filtered_data, x="Year", y="Consumption (GWh)", title="Yearly Consumption (GWh)", markers=True)
            st.plotly_chart(line_chart, use_container_width=True)

        # Pie Chart
        st.markdown("### Distribution")
        pie_chart = px.pie(filtered_data, names="Year", values="Installed Capacity (MW)", title="Installed Capacity Distribution")
        st.plotly_chart(pie_chart, use_container_width=True)

        # Scatter Plot
        scatter_chart = px.scatter(filtered_data, x="Year", y="Imports (GWh)", size="Consumption (GWh)", title="Imports vs. Year")
        st.plotly_chart(scatter_chart, use_container_width=True)

        # Area Chart
        area_chart = px.area(filtered_data, x="Year", y="Installed Capacity (MW)", title="Installed Capacity Over Years")
        st.plotly_chart(area_chart, use_container_width=True)

    except Exception as e:
        st.error(f"An error occurred: {e}")
