import pandas as pd
import requests
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler
from scipy.stats import zscore


#@st.cache_data(ttl=3600)
def load_earthquake_data():
    url = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_month.geojson"
    data = requests.get(url).json()
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
    df = df[df["magnitude"] > 0]
    return df.drop(columns="coordinates")


def cluster_earthquakes(df, eps=0.3, min_samples=5):
    coords = df[["latitude", "longitude"]].values
    coords = StandardScaler().fit_transform(coords)
    db = DBSCAN(eps=eps, min_samples=min_samples).fit(coords)
    df["cluster"] = db.labels_
    return df


def detect_anomalies(df):
    df["mag_zscore"] = zscore(df["magnitude"].fillna(0))
    df["anomaly"] = df["mag_zscore"] > 2.5
    return df


def assign_severity(df):
    def score(row):
        return (row["magnitude"] ** 2) / (row["depth_km"] + 1)

    def label(sev):
        if sev > 10:
            return "Severe"
        elif sev > 5:
            return "Moderate"
        else:
            return "Light"

    df["severity_score"] = df.apply(score, axis=1)
    df["severity"] = df["severity_score"].apply(label)
    return df


def aggregate_daily(df):
    daily = df.copy()
    daily["date"] = df["time"].dt.date
    return daily.groupby("date").size().reset_index(name="quake_count")
