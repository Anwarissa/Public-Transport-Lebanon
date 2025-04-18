import pandas as pd
import plotly.express as px
import streamlit as st

# Load dataset
transport_df = pd.read_csv('Public Transportation.csv')

# Clean column names
transport_df.columns = transport_df.columns.str.replace(' ', '_').str.replace('-', '_')

# Extract Governorate from refArea column
transport_df["Governorate"] = transport_df["refArea"].apply(
    lambda x: x.split("/")[-1].replace("_", " ") if isinstance(x, str) else x
)

# Filter only the rows with Governorates
gov_df = transport_df[transport_df["Governorate"].str.contains("Governorate", na=False)].copy()
gov_df["Governorate"] = gov_df["Governorate"].str.replace(" Governorate", "", regex=False)

# Define the road types
road_types = ["Main", "Secondary", "Agricultural"]

# Sidebar Filter 
st.sidebar.header("🔍 Filters")
selected_gov = st.sidebar.selectbox("Select a Governorate:", ["All"] + sorted(gov_df["Governorate"].unique()))

# Filter dataset based on selected governorate
filtered_df = gov_df if selected_gov == "All" else gov_df[gov_df["Governorate"] == selected_gov]

# Main Title
st.title("🚖 Public Transport & Road Conditions in Lebanon")
st.caption("Interactive dashboard built with Streamlit and Plotly")

st.markdown("""
Use the **sidebar filter** to explore public transport usage and road conditions across Lebanese governorates.
""")

# KPIs - Transport Mode Summary
st.subheader("📊 Transport Mode Summary")

transport_counts = filtered_df[[
    'The_main_means_of_public_transport___vans',
    'The_main_means_of_public_transport___taxis',
    'The_main_means_of_public_transport___buses'
]].sum()

col1, col2, col3 = st.columns(3)
col1.metric("🚐 Vans", int(transport_counts[0]))
col2.metric("🚖 Taxis", int(transport_counts[1]))
col3.metric("🚌 Buses", int(transport_counts[2]))

# Pie Chart - Public Transport Modes
st.subheader(f"🚍 Primary Public Transport Modes in {'All Governorates' if selected_gov == 'All' else selected_gov}")

fig_pie = px.pie(
    values=transport_counts,
    names=['Vans', 'Taxis', 'Buses'],
    title=None,
    color_discrete_map={'Vans': 'orange', 'Taxis': 'yellow', 'Buses': 'blue'}
)
st.plotly_chart(fig_pie, use_container_width=True)

# Road Type Filter
st.subheader(f"🚧 Road Condition Ratings in {'All Governorates' if selected_gov == 'All' else selected_gov}")
selected_types = st.multiselect(
    "Select Road Types to Display:",
    options=road_types,
    default=road_types,
    key="road_type_filter"
)

# Bar Chart - Road Condition Ratings
road_cols = [
    'State_of_the_main_roads___good', 'State_of_the_main_roads___acceptable', 'State_of_the_main_roads___bad',
    'State_of_the_secondary_roads___good', 'State_of_the_secondary_roads___acceptable', 'State_of_the_secondary_roads___bad',
    'State_of_agricultural_roads___good', 'State_of_agricultural_roads___acceptable', 'State_of_agricultural_roads___bad'
]

road_conditions = filtered_df[road_cols].sum()

labels = [
    'Main - Good', 'Main - Acceptable', 'Main - Bad',
    'Secondary - Good', 'Secondary - Acceptable', 'Secondary - Bad',
    'Agricultural - Good', 'Agricultural - Acceptable', 'Agricultural - Bad'
]

road_conditions_df = pd.DataFrame({'Road Condition': labels, 'Count': road_conditions})
road_conditions_df['Road Type'] = road_conditions_df['Road Condition'].str.split(' - ').str[0]
road_conditions_df['Condition'] = road_conditions_df['Road Condition'].str.split(' - ').str[1]
road_conditions_df = road_conditions_df[road_conditions_df['Road Type'].isin(selected_types)]

condition_colors = {'Good': 'green', 'Acceptable': 'blue', 'Bad': 'red'}

fig_bar = px.bar(
    road_conditions_df,
    x='Road Type',
    y='Count',
    color='Condition',
    barmode='group',
    title=None,
    color_discrete_map=condition_colors
)
st.plotly_chart(fig_bar, use_container_width=True)

# About Section
with st.expander("ℹ️ About this Dashboard"):
    st.markdown("""
This dashboard presents insights on public transportation usage and road conditions across Lebanese governorates.

Features:
- Pie chart of public transport modes
- Bar chart of road condition ratings
- Filter by governorate and road type

Developed by: Anwar Issa  
Source: [Linked Data Source](https://linked.aub.edu.lb/pkgcube/data/85ad3210ab85ae76a878453fad9ce16f_20240905_164730.csv)
""")
