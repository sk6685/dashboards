import requests
import pandas as pd

url = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_month.geojson"
response = requests.get(url)

print("Status code:", response.status_code)
if response.status_code != 200:
    print("Error fetching data:", response.text)
else:
    data = response.json()
    print("Top-level keys:", data.keys())


df=pd.json_normalize(data['features'])

df = df[[
    "id", "properties.place", "properties.mag", "properties.time", "geometry.coordinates"
]]
df.columns = ["id", "place", "magnitude", "time", "coordinates"]

print(df.head())