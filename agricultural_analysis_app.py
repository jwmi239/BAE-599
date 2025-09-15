import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Page configuration
st.set_page_config(
    page_title="Agricultural Data Analysis",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Main title
st.title("🌾 Agricultural Data Analysis Dashboard")
st.markdown("Interactive analysis of agricultural land values, crop prices, and price indices")

# Sidebar for navigation
st.sidebar.header("📊 Navigation")
analysis_type = st.sidebar.selectbox(
    "Choose Analysis:",
    ["🏞️ Regional Cropland Values", "🌾 National Crop Prices", "📈 National Price Index", "📋 All Charts"]
)

# Data loading functions
@st.cache_data
def load_cropland_data():
    df = pd.read_csv('Cropland Value.csv')
    df['Value'] = pd.to_numeric(df['Value'].astype(str).str.replace(',', ''), errors='coerce')
    return df

@st.cache_data
def load_crop_prices_data():
    df = pd.read_csv('Crop Prices.csv')
    df['Value'] = pd.to_numeric(df['Value'], errors='coerce')
    return df

@st.cache_data
def load_index_data():
    df = pd.read_csv('Index Prices.csv')
    df['Value'] = pd.to_numeric(df['Value'], errors='coerce')
    return df

# Load all data
cropland_df = load_cropland_data()
crop_prices_df = load_crop_prices_data()
index_df = load_index_data()

# Function to create cropland values chart
def create_cropland_chart(selected_states, year_range, chart_type):
    filtered_df = cropland_df[
        (cropland_df['State'].isin(selected_states)) & 
        (cropland_df['Year'] >= year_range[0]) & 
        (cropland_df['Year'] <= year_range[1])
    ].copy()
    
    if filtered_df.empty:
        return None, None
    
    filtered_df['State_Display'] = filtered_df['State'].str.title()
    
    if chart_type == 'Line Chart':
        fig = px.line(filtered_df, x='Year', y='Value', color='State_Display',
                      markers=True, title=f'Cropland Values per Acre ({year_range[0]}-{year_range[1]})')
    elif chart_type == 'Area Chart':
        fig = px.area(filtered_df, x='Year', y='Value', color='State_Display',
                      title=f'Cropland Values per Acre ({year_range[0]}-{year_range[1]})')
    else:  # Bar Chart
        fig = px.bar(filtered_df, x='Year', y='Value', color='State_Display',
                     title=f'Cropland Values per Acre ({year_range[0]}-{year_range[1]})')
    
    fig.update_layout(
        xaxis_title='Year',
        yaxis_title='Price per Acre ($)',
        yaxis_tickformat='$,.0f',
        height=500,
        hovermode='x unified'
    )
    
    return fig, filtered_df

# Function to create crop prices chart
def create_crop_prices_chart():
    commodities = ['WHEAT', 'CORN', 'SOYBEANS']
    filtered_data = crop_prices_df[crop_prices_df['Commodity'].isin(commodities)].copy()
    
    fig = px.line(filtered_data, x='Year', y='Value', color='Commodity',
                  markers=True, title='National Crop Prices (1975-2025)')
    
    fig.update_layout(
        xaxis_title='Year',
        yaxis_title='Price per Bushel ($)',
        yaxis_tickformat='$,.2f',
        height=500,
        hovermode='x unified'
    )
    
    return fig, filtered_data

# Function to create price index chart
def create_price_index_chart():
    filtered_data = index_df[(index_df['Year'] >= 1990) & (index_df['Year'] <= 2025)].copy()
    
    fig = px.line(filtered_data, x='Year', y='Value', markers=True,
                  title='National Food Commodity Price Index (1990-2025)<br><sub>Base Year: 2011 = 100</sub>')
    
    fig.update_layout(
        xaxis_title='Year',
        yaxis_title='Price Index (2011 = 100)',
        yaxis_tickformat='.1f',
        height=500,
        showlegend=False
    )
    
    # Add reference line at 100
    fig.add_hline(y=100, line_dash="dash", line_color="gray",
                  annotation_text="2011 Base Year (100)")
    
    fig.update_traces(line=dict(width=3), marker=dict(size=6))
    
    return fig, filtered_data

# Regional Cropland Values Analysis
if analysis_type in ["🏞️ Regional Cropland Values", "📋 All Charts"]:
    st.header("🏞️ Regional Cropland Values Analysis")
    
    col1, col2 = st.columns([1, 3])
    
    with col1:
        st.subheader("Filter Options")
        
        # State selection
        available_states = ['KENTUCKY', 'INDIANA', 'OHIO', 'TENNESSEE']
        selected_states = st.multiselect(
            'Select States:',
            available_states,
            default=available_states,
            key="cropland_states"
        )
        
        # Year range
        min_year = int(cropland_df['Year'].min())
        max_year = int(cropland_df['Year'].max())
        year_range = st.slider(
            'Year Range:',
            min_value=min_year,
            max_value=max_year,
            value=(1997, 2025),
            key="cropland_years"
        )
        
        # Chart type
        chart_type = st.selectbox(
            'Chart Type:',
            ['Line Chart', 'Area Chart', 'Bar Chart'],
            key="cropland_chart_type"
        )
    
    with col2:
        if selected_states:
            fig, filtered_df = create_cropland_chart(selected_states, year_range, chart_type)
            if fig:
                st.plotly_chart(fig, use_container_width=True)
                
                # Summary statistics
                st.subheader("📊 Summary Statistics")
                summary_stats = filtered_df.groupby('State_Display')['Value'].agg(['mean', 'min', 'max', 'std']).round(0)
                summary_stats.columns = ['Average ($)', 'Minimum ($)', 'Maximum ($)', 'Std Dev ($)']
                st.dataframe(summary_stats, use_container_width=True)
            else:
                st.warning("No data available for selected filters.")
        else:
            st.warning("Please select at least one state.")
    
    if analysis_type == "📋 All Charts":
        st.markdown("---")

# National Crop Prices Analysis
if analysis_type in ["🌾 National Crop Prices", "📋 All Charts"]:
    st.header("🌾 National Crop Prices Analysis")
    
    fig, crop_data = create_crop_prices_chart()
    st.plotly_chart(fig, use_container_width=True)
    
    # Show latest prices
    st.subheader("📈 Latest Prices (2024)")
    latest_prices = crop_data[crop_data['Year'] == crop_data['Year'].max()][['Commodity', 'Value']]
    latest_prices = latest_prices.sort_values('Value', ascending=False)
    latest_prices['Value'] = latest_prices['Value'].apply(lambda x: f"${x:.2f}")
    st.dataframe(latest_prices.set_index('Commodity'), use_container_width=True)
    
    if analysis_type == "📋 All Charts":
        st.markdown("---")

# National Price Index Analysis
if analysis_type in ["📈 National Price Index", "📋 All Charts"]:
    st.header("📈 National Price Index Analysis")
    
    fig, index_data = create_price_index_chart()
    st.plotly_chart(fig, use_container_width=True)
    
    # Show key statistics
    col1, col2, col3, col4 = st.columns(4)
    
    current_index = index_data['Value'].iloc[0]  # Most recent value
    avg_index = index_data['Value'].mean()
    max_index = index_data['Value'].max()
    min_index = index_data['Value'].min()
    
    with col1:
        st.metric("Current Index (2024)", f"{current_index:.1f}", f"{current_index-100:.1f} vs 2011")
    with col2:
        st.metric("Average Index", f"{avg_index:.1f}")
    with col3:
        st.metric("Highest Index", f"{max_index:.1f}")
    with col4:
        st.metric("Lowest Index", f"{min_index:.1f}")

# Footer
st.markdown("---")
st.markdown("**Data Sources:** USDA Agricultural Statistics | **Analysis Period:** 1975-2025")
