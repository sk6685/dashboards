import streamlit as st
import pandas as pd
import requests
import plotly.express as px

@st.cache_data(ttl=3600)
def load_earthquake_data():
    url = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_month.geojson"
    response = requests.get(url)
    data = response.json()
    print(data)
    features = data["features"]
    df = pd.json_normalize(features)
    df = df[[
        "id", "properties.place", "properties.mag", "properties.time", "geometry.coordinates"
    ]]
    df.columns = ["id", "place", "magnitude", "time", "coordinates"]
    df["longitude"] = df["coordinates"].apply(lambda x: x[0])
    df["latitude"] = df["coordinates"].apply(lambda x: x[1])
    df["depth_km"] = df["coordinates"].apply(lambda x: x[2])
    df["time"] = pd.to_datetime(df["time"], unit="ms")
    return df

st.title("🌍 USGS Earthquake Dashboard")

df = load_earthquake_data()
df = df[df["magnitude"] > 0]

# Sidebar filters
min_mag = float(df["magnitude"].min())
max_mag = float(df["magnitude"].max())
magnitude_range = st.sidebar.slider(
    "Magnitude Range",
    min_value=min_mag,
    max_value=max_mag,
    value=(min_mag, max_mag),
    step=0.1,
)

start_time = df["time"].min()
end_time = df["time"].max()
time_range = st.sidebar.date_input(
    "Date Range",
    value=(start_time.date(), end_time.date()),
    min_value=start_time.date(),
    max_value=end_time.date(),
)

# Filter dataframe
filtered_df = df[
    (df["magnitude"] >= magnitude_range[0]) &
    (df["magnitude"] <= magnitude_range[1]) &
    (df["time"].dt.date >= time_range[0]) &
    (df["time"].dt.date <= time_range[1])
]

st.subheader(f"Filtered {len(filtered_df)} earthquakes")

fig = px.scatter_map(
    filtered_df,
    lat="latitude",
    lon="longitude",
    size="magnitude",
    color="depth_km",
    color_continuous_scale="Viridis",
    hover_name="place",
    hover_data={"magnitude": True, "time": True, "depth_km": True},
    zoom=3,
    height=500,
)
fig.update_layout(mapbox_style="open-street-map", margin={"r":0,"t":0,"l":0,"b":0})

st.plotly_chart(fig, use_container_width=True)
