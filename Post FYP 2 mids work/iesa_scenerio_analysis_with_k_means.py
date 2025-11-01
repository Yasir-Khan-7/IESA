import streamlit as st
import pandas as pd
import mysql.connector
import groq
import altair as alt
from smolagents import Tool
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import numpy as np
from sklearn.decomposition import PCA

# Initialize sidebar state
if 'sidebar_state' not in st.session_state:
    st.session_state.sidebar_state = 'expanded'
if 'button_text' not in st.session_state:
    st.session_state.button_text = '← Hide'
if 'previous_scenarios' not in st.session_state:
    st.session_state.previous_scenarios = []
if 'should_rerun' not in st.session_state:
    st.session_state.should_rerun = False
if 'scenario_analyses' not in st.session_state:
    st.session_state.scenario_analyses = {}
if 'toggle_triggered' not in st.session_state:
    st.session_state.toggle_triggered = False
if 'rendered_charts' not in st.session_state:
    st.session_state.rendered_charts = {}
if 'chart_keys' not in st.session_state:
    st.session_state.chart_keys = set()
if 'current_action' not in st.session_state:
    st.session_state.current_action = None
# New clustering state variables
if 'clustering_results' not in st.session_state:
    st.session_state.clustering_results = {}
if 'selected_features' not in st.session_state:
    st.session_state.selected_features = []
if 'num_clusters' not in st.session_state:
    st.session_state.num_clusters = 3

# Function to toggle sidebar
def toggle_sidebar():
    if st.session_state.sidebar_state == 'expanded':
        st.session_state.sidebar_state = 'collapsed'
        st.session_state.button_text = '→ Show'
    else:
        st.session_state.sidebar_state = 'expanded'
        st.session_state.button_text = '← Hide'
    st.session_state.should_rerun = True
    st.session_state.toggle_triggered = True

# Function to auto-hide sidebar
def auto_hide_sidebar():
    st.session_state.sidebar_state = 'collapsed'
    st.session_state.button_text = '→ Show'
    st.session_state.should_rerun = True
    st.session_state.toggle_triggered = False

# Function to auto-hide sidebar without rerunning
def auto_hide_sidebar_no_rerun():
    st.session_state.sidebar_state = 'collapsed'
    st.session_state.button_text = '→ Show'
    st.session_state.toggle_triggered = False

# Set page config with initial sidebar state
st.set_page_config(
    page_title="IESA Scenario Analysis", 
    layout="wide", 
    page_icon="📊",
    initial_sidebar_state=st.session_state.sidebar_state
)

# Database connection
def get_connection():
    return mysql.connector.connect(
        host="localhost",
        port="3306",
        user="root",
        passwd="admin123",
        db="iesa_db"
    )

# Fetch Scenarios from Database
def fetch_scenarios():
    conn = get_connection()
    query = "SELECT category, scenario FROM scenario_definitions;"
    df = pd.read_sql(query, conn)
    conn.close()
    return df

# Fetch predefined query results
def fetch_data(query):
    conn = get_connection()
    df = pd.read_sql(query, conn)
    conn.close()
    return df

# AI-powered Scenario Analysis
client = groq.Client(api_key=None)  # API key removed for security. Use environment variable or .env file.

class ScenarioAnalysisTool(Tool):
    name = "scenario_analysis"
    description = "Analyzes a generated scenario and provides structured insights."
    inputs = {
        "scenario": {"type": "string", "description": "Scenario title."},
        "data_string": {"type": "string", "description": "String representation of the dataset."}
    }
    output_type = "string"

    def forward(self, scenario: str, data_string: str):
        prompt = (f"Analyze the following dataset based on actual trends:\n\n"
                  f"{data_string}\n\n"
                  f"Scenario: {scenario}\n\n"
                  "Provide a concise yet informative analysis with 2-3 main sections. Each section should have a clear heading and 2-3 bullet points with specific insights. Focus exclusively on the data provided.\n\n"
                  "Format your response as follows:\n\n"
                  "## Key Trend Analysis\n"
                  "- Include specific numbers and percentages from the data\n"
                  "- Highlight the most significant pattern observed\n\n"
                  "## Impact Assessment\n"
                  "- Describe direct implications based on the data\n"
                  "- Use comparative analysis when relevant\n\n"
                  "Keep each bullet point concise but informative with data-backed observations.")

        response = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[{"role": "user", "content": prompt}]
        )
        
        return response.choices[0].message.content.strip()

# Function to perform K-means clustering
def perform_kmeans_clustering(data, features, n_clusters=3):
    """
    Perform K-means clustering on selected features
    
    Args:
        data: DataFrame containing the data
        features: List of column names to use for clustering
        n_clusters: Number of clusters to form
    
    Returns:
        Dictionary containing:
        - 'data': Original data with cluster assignments
        - 'centers': Cluster centers
        - 'inertia': Sum of squared distances of samples to their closest cluster center
        - 'pca_data': PCA-transformed data for visualization (if >2 dimensions)
        - 'pca_centers': PCA-transformed cluster centers (if >2 dimensions)
    """
    # Select only numeric features and drop rows with missing values
    X = data[features].dropna()
    
    # Store index mapping between X and original data
    index_mapping = {i: idx for i, idx in enumerate(X.index)}
    
    # Standardize the features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Apply K-means clustering
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    cluster_labels = kmeans.fit_predict(X_scaled)
    
    # Add cluster labels to the data
    clustered_data = data.copy()
    clustered_data.loc[X.index, 'Cluster'] = cluster_labels
    
    # For visualization, apply PCA if more than 2 features
    if len(features) > 2:
        pca = PCA(n_components=2)
        pca_result = pca.fit_transform(X_scaled)
        pca_centers = pca.transform(scaler.transform(kmeans.cluster_centers_))
        
        # Create DataFrame for PCA results
        pca_df = pd.DataFrame(
            data=pca_result,
            columns=['PC1', 'PC2']
        )
        pca_df['Cluster'] = cluster_labels
        pca_df['Year'] = X.index.map(lambda idx: data.loc[idx, 'Year'])
        
        explained_variance = pca.explained_variance_ratio_
    else:
        pca_df = None
        pca_centers = None
        explained_variance = None
    
    return {
        'data': clustered_data,
        'centers': kmeans.cluster_centers_,
        'inertia': kmeans.inertia_,
        'pca_data': pca_df,
        'pca_centers': pca_centers,
        'explained_variance': explained_variance,
        'features': features,
        'scaler': scaler
    }

# Function to create cluster visualization
def create_cluster_chart(cluster_results, original_features):
    """Create Altair visualization for clusters"""
    if len(original_features) <= 2:
        # Direct visualization using original features
        plot_df = cluster_results['data'].dropna(subset=['Cluster'])
        x_col = original_features[0]
        y_col = original_features[1] if len(original_features) > 1 else original_features[0]
        
        # Create the scatter plot
        scatter = alt.Chart(plot_df).mark_circle(size=80).encode(
            x=alt.X(f'{x_col}:Q', title=x_col),
            y=alt.Y(f'{y_col}:Q', title=y_col),
            color=alt.Color('Cluster:N', scale=alt.Scale(scheme='category10'),
                           legend=alt.Legend(title="Cluster")),
            tooltip=['Year', x_col, y_col, 'Cluster']
        ).properties(
            width=600,
            height=400,
            title=f'Clusters based on {", ".join(original_features)}'
        )
        
        return scatter

    else:
        # Use PCA results for visualization
        pca_df = cluster_results['pca_data']
        
        # Add a title with explained variance
        ev = cluster_results['explained_variance']
        title = f'Clusters based on {len(original_features)} features (PCA: {ev[0]:.1%}, {ev[1]:.1%} variance explained)'
        
        # Create scatter plot with PCA components
        scatter = alt.Chart(pca_df).mark_circle(size=80).encode(
            x=alt.X('PC1:Q', title='Principal Component 1'),
            y=alt.Y('PC2:Q', title='Principal Component 2'),
            color=alt.Color('Cluster:N', scale=alt.Scale(scheme='category10'),
                           legend=alt.Legend(title="Cluster")),
            tooltip=['Year', 'PC1', 'PC2', 'Cluster']
        ).properties(
            width=600,
            height=400,
            title=title
        )
        
        return scatter

# CSS and JavaScript for dynamic button states
st.markdown("""
    <style>
    /* General Styling */
    header {
        border-bottom: 3px solid  #136a8a !important; 
    }
    [data-testid="stSidebar"] {
        background: linear-gradient(135deg, #73C8A9, #0b8793); /* Gradient background */
        color: white;
        margin-top:58px;
        box-shadow: 2px 0 10px rgba(0,0,0,0.2);
    }
    .sidebar-content {
        margin-top: -60px;
        padding: 20px;
    }
    
    /* Toggle button styles */
    div[data-testid="stHorizontalBlock"] > div:first-child button {
        background-color: #0b8793;
        color: white !important;
        border: 1px solid #4AC29A;
        border-radius: 5px;
        padding: 8px 15px;
        font-weight: bold;
        box-shadow: 0 2px 5px rgba(0,0,0,0.2);
        transition: all 0.3s ease;
    }

    div[data-testid="stHorizontalBlock"] > div:first-child button:hover {
        background-color: #4AC29A;
        transform: translateY(-1px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    
    [data-testid="stSidebar"] h2 {
        font-size: 22px !important;
        margin-top: 25px !important;
        margin-bottom: 15px !important;
        padding-bottom: 5px;
        border-bottom: 2px solid rgba(255,255,255,0.3);
        text-shadow: 1px 1px 2px rgba(0,0,0,0.2);
    }
    
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] label {
        color: rgba(255,255,255,0.9) !important;
        font-weight: 500;
        margin-bottom: 8px;
        font-size: 15px;
    }
    
    [data-testid="stSidebar"] .stSelectbox > div, [data-testid="stSidebar"] .stMultiSelect > div {
        background-color: rgba(255,255,255,0.1) !important;
        border: 1px solid rgba(255,255,255,0.2) !important;
        border-radius: 5px;
        color: white !important;
        margin-bottom: 15px;
    }
    
    [data-testid="stSidebar"] .stSelectbox > div:hover, [data-testid="stSidebar"] .stMultiSelect > div:hover {
        border: 1px solid rgba(255,255,255,0.4) !important;
    }
    
    [data-testid="stSidebar"] span[data-baseweb="tag"] {
        background-color: #73C8A9 !important;
        border: none !important;
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
    
    a{
        text-decoration: none;
        color: #0F403F !important;
    }
    a:hover{
        color: #0F403F !important;
        text-decoration: none;
    }
    
    /* Chart Improvements */
    .marks{
        border-radius: 15px; /* Rounded corners for the SVG canvas */
        border: 1px solid  #0b8793; /* Greenish border */
        box-shadow: 0px 8px 15px rgba(0, 0, 0, 0.2);
        margin-top: 20px; /* Add some spacing from the buttons */
        padding: 20px; /* Add padding inside the canvas */
        width: 99%; /* Full width */
        background-color: #f9fcfc;
    }
    
    /* Make axes and labels more visible but sharper */
    .chart-wrapper {
        margin-bottom: 30px;
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
    
    .marks .mark-rule line {
        stroke: #ddd !important;
        stroke-width: 1px !important;
    }
    
    /* Numbers on axes */
    .marks text.role-axis-label {
        font-size: 16px !important;
        font-weight: bold !important;
        fill: #333 !important;
    }
    
    /* Analysis text formatting */
    .scenario-analysis {
        background-color: #f9fcfc;
        border-left: 4px solid #0b8793;
        padding: 20px;
        margin-top: 20px;
        border-radius: 0 5px 5px 0;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    }
    
    .scenario-analysis h3 {
        color: #0b8793;
        margin-bottom: 15px;
    }
    
    .scenario-analysis ul {
        padding-left: 20px;
    }
    
    .scenario-analysis li {
        margin-bottom: 8px;
        line-height: 1.5;
    }
    
    /* Scenario header styling */
    h2 {
        color: #0b8793;
        border-bottom: 2px solid #73C8A9;
        padding-bottom: 8px;
        margin-top: 30px;
        margin-bottom: 20px;
    }
    
    /* Clustering Section */
    .clustering-section {
        background-color: #f8f9fa;
        padding: 20px;
        border-radius: 10px;
        margin: 20px 0;
        border-left: 4px solid #0b8793;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    }
    
    .cluster-chart {
        background-color: white;
        border-radius: 8px;
        padding: 15px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        margin-top: 15px;
    }
    
    .feature-selector {
        background-color: white;
        border-radius: 8px;
        padding: 15px;
        margin: 15px 0;
        border: 1px solid #e0e0e0;
    }
    
    .cluster-insights {
        background-color: #f0f7fa;
        padding: 15px;
        border-radius: 8px;
        margin-top: 15px;
        border-left: 3px solid #0b8793;
    }
    </style>
""", unsafe_allow_html=True)

# Add the toggle button at the top with a narrower column
toggle_col1, toggle_col2 = st.columns([1, 11])
with toggle_col1:
    st.button(st.session_state.button_text, key="toggle_sidebar_button", on_click=toggle_sidebar)

# Streamlit UI
st.sidebar.image("images/iesa_white.svg", width=150)
st.sidebar.markdown("""<h2>IESA Scenario Analysis</h2>""", unsafe_allow_html=True)

# Fetch available scenarios from DB
scenarios_df = fetch_scenarios()
scenario_categories = {category: list(group["scenario"]) for category, group in scenarios_df.groupby("category")}

# Sidebar - Category Selection
selected_category = st.sidebar.selectbox("Select Category", list(scenario_categories.keys()), key="category_select")

# Query Dictionary for Analysis
query_dict = {
    "Future Electricity Demand Growth": "SELECT Year, `Consumption (GWh)`, ((`Consumption (GWh)` - LAG(`Consumption (GWh)`, 1) OVER (ORDER BY Year)) / LAG(`Consumption (GWh)`, 1) OVER (ORDER BY Year) * 100) AS Growth_Rate FROM annual_electricity_data;",
    "Renewable Energy Contribution": "SELECT Year, `Renewable Electricity`, `Total`, (`Renewable Electricity` / `Total`) * 100 AS Renewable_Percentage FROM primary_energy_supplies_by_source_toe;",
    "Power Shortage Risk": "SELECT Year, `Generation (GWh)`, `Consumption (GWh)`, (`Generation (GWh)` - `Consumption (GWh)`) AS Surplus_Deficit FROM annual_electricity_data;",
    "Impact of Industrial Expansion on Electricity Demand": "SELECT Year, Industrial, (Industrial - LAG(Industrial, 1) OVER (ORDER BY Year)) / LAG(Industrial, 1) OVER (ORDER BY Year) * 100 AS Industrial_Growth_Rate FROM electricity_consumption_by_sector_gwh;",
    "Future Gas Demand Forecast": "SELECT Year, `Natural Gas Consumption`, ((`Natural Gas Consumption` - LAG(`Natural Gas Consumption`, 1) OVER (ORDER BY Year)) / LAG(`Natural Gas Consumption`, 1) OVER (ORDER BY Year)) * 100 AS Growth_Rate FROM natural_gas_production_and_consumption;",
    "Gas Production vs. Consumption Balance": "SELECT Year, `Natural Gas Production`, `Natural Gas Consumption`, (`Natural Gas Production` - `Natural Gas Consumption`) AS Surplus_Deficit FROM natural_gas_production_and_consumption;",
    "Total Energy Demand vs. Supply Balance": "SELECT YEAR, `Total Primary Energy Supply (MTOE)`, `Total Final Consumption of Energy (MTOE)`, (`Total Primary Energy Supply (MTOE)` - `Total Final Consumption of Energy (MTOE)`) AS Surplus_Deficit FROM energy_supply_and_consumption_analysis;",
    "Supply Chain Disruptions in Gas Imports": "SELECT Year, `Imports` FROM total_imports_lng;",
    "Sector-Wise Energy Consumption Changes": "SELECT Year, Total FROM sector_wise_energy_consumption;"
}

# Sidebar - Multi-Select Scenarios within Category
selected_scenarios = st.sidebar.multiselect("Select Scenarios", scenario_categories[selected_category], key="scenarios_multiselect")

# Add clustering option to sidebar
st.sidebar.markdown("---")
st.sidebar.markdown("### Data Clustering")
st.sidebar.markdown("Discover patterns with K-means clustering")
enable_clustering = st.sidebar.checkbox("Enable clustering analysis", key="enable_clustering")

# Add clustering controls when enabled
if enable_clustering and selected_scenarios:
    # Get all data for clustering
    all_data = {}
    numeric_columns = {}
    
    for scenario in selected_scenarios:
        if scenario in query_dict:
            query = query_dict[scenario]
            data = fetch_data(query)
            
            if data is not None and not data.empty:
                # Store data by scenario
                all_data[scenario] = data
                
                # Track numeric columns for each scenario (excluding Year)
                numeric_cols = data.select_dtypes(include=['number']).columns.tolist()
                if 'Year' in numeric_cols:
                    numeric_cols.remove('Year')
                numeric_columns[scenario] = numeric_cols

    # Only show controls if we have data with numeric columns
    if numeric_columns:
        # Select scenario for clustering
        cluster_scenario = st.sidebar.selectbox(
            "Select scenario for clustering",
            options=list(numeric_columns.keys()),
            key="cluster_scenario"
        )
        
        # Select features for clustering
        if cluster_scenario and cluster_scenario in numeric_columns:
            available_features = numeric_columns[cluster_scenario]
            
            selected_features = st.sidebar.multiselect(
                "Select features for clustering",
                options=available_features,
                default=available_features[:min(2, len(available_features))],
                key="clustering_features"
            )
            
            # Number of clusters - using the session state value as default
            num_clusters = st.sidebar.slider(
                "Number of clusters",
                min_value=2,
                max_value=10,
                value=st.session_state.num_clusters,
                key="num_clusters"
            )
            
            # Update only the selected_features in session state
            # (not updating num_clusters since it's bound to widget)
            st.session_state.selected_features = selected_features
            
            # Run clustering button
            if st.sidebar.button("Run Clustering Analysis", key="run_clustering"):
                if len(selected_features) > 0:
                    with st.spinner("Performing clustering analysis..."):
                        # Store the selected data for clustering
                        scenario_data = all_data[cluster_scenario]
                        
                        # Run clustering using the current slider value
                        clustering_results = perform_kmeans_clustering(
                            scenario_data, 
                            selected_features, 
                            num_clusters  # Using slider value directly
                        )
                        
                        # Store results in session state
                        st.session_state.clustering_results = {
                            'scenario': cluster_scenario,
                            'results': clustering_results
                        }
                else:
                    st.sidebar.error("Please select at least one feature for clustering")

# Check if scenarios selection has changed and auto-hide sidebar if so
if selected_scenarios and selected_scenarios != st.session_state.previous_scenarios:
    st.session_state.current_action = "new_selection"  # Mark that selection changed
    auto_hide_sidebar()
    st.session_state.previous_scenarios = selected_scenarios.copy()

# Function to create chart with fixed dimensions
def create_chart(data, scenario, y_col):
    # Fixed dimensions for consistency
    fixed_width = 550  # Increased fixed width
    fixed_height = 350  # Increased fixed height
    
    # Create a more visible color scheme
    color_scheme = alt.Scale(range=['#0b67a0', '#d62728', '#2ca02c', '#9467bd', '#8c564b'])
    
    # Create a base chart with fixed dimensions
    base = alt.Chart(data).encode(
        x=alt.X("Year:O", title="Year", axis=alt.Axis(
            labelAngle=0,
            titleFontSize=16,
            titleFontWeight='bold',
            labelFontSize=14,
            labelFontWeight='bold',
            tickWidth=2,
            tickColor='#333333',
            labelColor='#333333',
            titleColor='#333333',
            domainColor='#666666',
            domainWidth=2
        )),
        y=alt.Y(y_col, title=y_col, axis=alt.Axis(
            titleFontSize=16,
            titleFontWeight='bold',
            labelFontSize=14,
            labelFontWeight='bold',
            grid=True,
            gridColor='#e0e0e0',
            tickWidth=2,
            tickColor='#333333',
            labelColor='#333333',
            titleColor='#333333',
            domainColor='#666666',
            domainWidth=2,
            format=',.0f'  # Format numbers without decimals
        ))
    ).properties(
        title={
            "text": f"{scenario}: Year vs {y_col}",
            "fontSize": 18,
            "fontWeight": "bold",
            "color": "#0b8793"
        },
        width=fixed_width,
        height=fixed_height
    )
    
    # Add line layer
    line = base.mark_line(
        strokeWidth=3.5,
        clip=True,
        color='#0066cc'
    ).encode(
        tooltip=list(data.columns)
    )
    
    # Add points with enhanced visibility
    points = base.mark_circle(
        size=80,
        opacity=1,
        stroke='#fff',
        strokeWidth=1.5,
        color='#0066cc'
    ).encode(
        tooltip=list(data.columns)
    )
    
    # Combine layers
    final_chart = alt.layer(line, points).configure_view(
        strokeWidth=1,
        stroke='#ddd'
    ).configure_axis(
        domainWidth=2,
        domainColor='#666666',
        labelFontWeight='bold',
        labelColor='#333333',
        titleColor='#333333',
        tickColor='#666666'
    ).configure_title(
        fontSize=18,
        font='Arial',
        fontWeight='bold',
        anchor='start',
        color='#0b8793'
    )
    
    return final_chart

# Loop through selected scenarios
for scenario in selected_scenarios:
    st.markdown(f"## Scenario: {scenario}")

    # Fetch data
    if scenario in query_dict:
        query = query_dict[scenario]
        data = fetch_data(query)
        
        if data is not None and not data.empty:
            # Dynamic Charts (Two-column layout)
            num_cols = 2
            cols = st.columns(num_cols)
            y_columns = list(data.columns[1:])  # Exclude 'Year' column

            for idx, y_col in enumerate(y_columns):
                col_idx = idx % num_cols
                chart_key = f"{scenario}_{y_col}"
                
                # Add to tracking of currently displayed charts
                st.session_state.chart_keys.add(chart_key)
                
                with cols[col_idx]:
                    # Create a fixed sized container to ensure consistency
                    container = st.container()
                    
                    # Only create new chart when needed (selection changed, first load, or analysis)
                    if (chart_key not in st.session_state.rendered_charts or 
                        st.session_state.current_action in ["new_selection", "analysis", None]):
                        final_chart = create_chart(data, scenario, y_col)
                        st.session_state.rendered_charts[chart_key] = final_chart
                    else:
                        final_chart = st.session_state.rendered_charts[chart_key]
                    
                    # Use precise dimensions for chart display
                    with container:
                        st.altair_chart(final_chart, use_container_width=False)
        else:
            st.error(f"No data available for scenario: {scenario}")

    # AI Analysis Button for Each Scenario with auto-hide on click
    if st.sidebar.button(f"Analyze {scenario}", on_click=auto_hide_sidebar_no_rerun, key=f"analyze_{scenario}"):
        st.session_state.current_action = "analysis"  # Mark that we're running analysis
        with st.spinner(f"Analyzing {scenario}... This may take a moments"):
            analysis_tool = ScenarioAnalysisTool()
            data_string = data.to_string(index=False)
            analysis = analysis_tool.forward(scenario, data_string)
            # Store analysis in session state
            st.session_state.scenario_analyses[scenario] = analysis
        
    # Display saved analyses for this scenario
    if scenario in st.session_state.scenario_analyses:
        st.subheader(f"Analysis for {scenario}")
        # Wrap the analysis in a styled div
        st.markdown(f'<div class="scenario-analysis">{st.session_state.scenario_analyses[scenario]}</div>', unsafe_allow_html=True)

# Display clustering results if available
if enable_clustering and 'clustering_results' in st.session_state and st.session_state.clustering_results:
    st.markdown("---")
    st.markdown("## Cluster Analysis")
    
    # Get clustering results from session state
    cluster_data = st.session_state.clustering_results
    scenario = cluster_data['scenario']
    results = cluster_data['results']
    features = results['features']
    
    # Create a styled container for the clustering section
    st.markdown('<div class="clustering-section">', unsafe_allow_html=True)
    
    # Display information about the clustering
    st.subheader(f"K-means Clustering for '{scenario}'")
    st.markdown(f"""
    <div class="cluster-insights">
        <h4>Clustering Information:</h4>
        <ul>
            <li><strong>Number of clusters:</strong> {st.session_state.num_clusters}</li>
            <li><strong>Features used:</strong> {", ".join(features)}</li>
            <li><strong>Clustering metric (inertia):</strong> {results['inertia']:.2f}</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    # Display the cluster chart
    st.markdown('<div class="cluster-chart">', unsafe_allow_html=True)
    cluster_chart = create_cluster_chart(results, features)
    st.altair_chart(cluster_chart, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Display cluster statistics
    st.subheader("Cluster Statistics")
    
    # Get the clustered data
    clustered_df = results['data'].dropna(subset=['Cluster'])
    
    # Calculate statistics per cluster
    cluster_stats = clustered_df.groupby('Cluster')[features].agg(['mean', 'min', 'max', 'std']).round(2)
    st.dataframe(cluster_stats, use_container_width=True)
    
    # Show a sample of data points from each cluster
    st.subheader("Samples from Each Cluster")
    
    # Create tabs for each cluster
    tabs = st.tabs([f"Cluster {i}" for i in range(st.session_state.num_clusters)])
    for i, tab in enumerate(tabs):
        with tab:
            cluster_samples = clustered_df[clustered_df['Cluster'] == i].reset_index(drop=True)
            if not cluster_samples.empty:
                st.dataframe(cluster_samples[['Year'] + features], use_container_width=True)
            else:
                st.info(f"No data points in Cluster {i}")
    
    st.markdown('</div>', unsafe_allow_html=True)

# Check if we should rerun the app at the end
if st.session_state.should_rerun:
    st.session_state.should_rerun = False
    # Reset current action after rerun
    st.session_state.current_action = None
    st.rerun()