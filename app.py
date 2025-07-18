import streamlit as st
import plotly.express as px
from utils import load_earthquake_data, cluster_earthquakes, detect_anomalies, assign_severity, aggregate_daily

st.set_page_config(layout="wide", page_title="🌍 Rhombus Earthquake Dashboard")

st.title("🌍 Rhombus Earthquake Dashboard")
st.markdown("A snapshot of global seismic activity. Built for the Rhombus Hackathon challenge.")

# Load and process data
df = load_earthquake_data()

# Sidebar filters
st.sidebar.header("🔍 Filters")
mag_range = st.sidebar.slider(
    "Magnitude Range",
    float(df["magnitude"].min()),
    float(df["magnitude"].max()),
    (2.5, 6.0),
    0.1,
)

date_range = st.sidebar.date_input(
    "Date Range",
    value=(df["time"].min().date(), df["time"].max().date()),
    min_value=df["time"].min().date(),
    max_value=df["time"].max().date(),
)

depth_range = st.sidebar.slider(
    "Depth Range (km)",
    float(df["depth_km"].min()),
    float(df["depth_km"].max()),
    (0.0, 300.0),
    5.0,
)

# Filter data
filtered = df[
    (df["magnitude"].between(*mag_range)) &
    (df["time"].dt.date.between(*date_range)) &
    (df["depth_km"].between(*depth_range))
]

# Apply logic
filtered = cluster_earthquakes(filtered)
filtered = assign_severity(filtered)
filtered = detect_anomalies(filtered)
filtered["cluster_label"] = filtered["cluster"].astype(str).replace({'-1': 'Noise'})

# Show metrics
col1, col2, col3 = st.columns(3)
col1.metric("Total Earthquakes", len(filtered))
col2.metric("Clusters Detected", filtered["cluster"].nunique() - (1 if -1 in filtered["cluster"].unique() else 0))
col3.metric("Anomalies Detected", filtered["anomaly"].sum())

# Earthquake map
st.subheader("🗺️ Earthquake Map (Clustered)")
fig = px.scatter_mapbox(
    filtered,
    lat="latitude",
    lon="longitude",
    color="cluster_label",
    size="magnitude",
    #animation_frame=filtered["time"].dt.date.astype(str),

    hover_name="place",
    hover_data=["magnitude", "depth_km", "severity"],
    zoom=1,
    height=600,
)

fig.update_layout(mapbox_style="open-street-map", margin={"r":0,"t":0,"l":0,"b":0})
st.plotly_chart(fig, use_container_width=True)

# Daily trend chart
st.subheader("📈 Earthquake Trend Over Time")
daily = aggregate_daily(filtered)
fig2 = px.line(daily, x="date", y="quake_count", markers=True)
st.plotly_chart(fig2, use_container_width=True)

# Top regions
st.subheader("🏙️ Top 5 Locations by Event Count")
top_places = filtered["place"].value_counts().head(5).reset_index()
top_places.columns = ["Location", "Count"]
st.dataframe(top_places)

# Download button
st.download_button(
    "📥 Download Filtered Data as CSV",
    data=filtered.to_csv(index=False),
    file_name="filtered_earthquakes.csv",
    mime="text/csv",
)

# Footer
st.caption("Built by sushama Jadhav for the Rhombus Hackathon.")
