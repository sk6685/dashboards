import pandas as pd
import random
from datetime import datetime, timedelta
import uuid

# --- Configuration for Data Generation ---
NUM_RECORDS = 750
START_DATE = datetime(2025, 1, 1) # Start date for events
END_DATE = datetime(2025, 7, 15)   # End date for events

EVENT_TYPES = [
    "Cyber Attack", "Infrastructure Incident", "Natural Disaster",
    "Humanitarian Crisis", "Security Anomaly", "Intelligence Leak"
]
SEVERITY_SCORES = list(range(1, 11))
STATUSES = ["Active", "Mitigated", "Ongoing Investigation", "Resolved"]
REPORTED_SOURCES = ["OSINT-Feed", "Gov-Agency-A", "Private-Sensor-Net", "Local-Watch"]
IMPACTED_REGIONS_OPTIONS = [
    "USA", "Europe", "Asia", "Africa", "South America", "Oceania",
    "Global", "Middle East", "North America", "Arctic"
]

# --- Create Hotspot Coordinates (examples) ---
# Near San Francisco
HOTSPOT_1 = (37.7749, -122.4194)
# Near Ukraine/Eastern Europe
HOTSPOT_2 = (48.3794, 31.1656)
# Near South China Sea
HOTSPOT_3 = (15.0, 115.0)

HOTSPOT_PROBABILITY = 0.25 # Probability that an event falls into a hotspot

# --- Data Generation Logic ---
data = []

for i in range(NUM_RECORDS):
    event_id = f"evt_{uuid.uuid4().hex[:8]}"

    # Random timestamp within the defined range
    time_delta = END_DATE - START_DATE
    random_days = random.randint(0, time_delta.days)
    random_seconds = random.randint(0, 24*3600 - 1)
    timestamp_utc = (START_DATE + timedelta(days=random_days, seconds=random_seconds)).isoformat() + 'Z'

    # Generate latitude/longitude, sometimes skewed towards hotspots
    if random.random() < HOTSPOT_PROBABILITY:
        hotspot_coords = random.choice([HOTSPOT_1, HOTSPOT_2, HOTSPOT_3])
        latitude = random.uniform(hotspot_coords[0] - 1.5, hotspot_coords[0] + 1.5)
        longitude = random.uniform(hotspot_coords[1] - 2.5, hotspot_coords[1] + 2.5)
    else:
        latitude = random.uniform(-90.0, 90.0)
        longitude = random.uniform(-180.0, 180.0)

    # Introduce some bad lat/lon values
    if random.random() < 0.01: # 1% chance of bad coord
        latitude = 999.0 if random.random() < 0.5 else -999.0
    if random.random() < 0.01: # 1% chance of bad coord
        longitude = 999.0 if random.random() < 0.5 else -999.0

    event_type = random.choice(EVENT_TYPES)
    # Introduce inconsistent casing for event_type
    if random.random() < 0.1:
        event_type = event_type.lower()
    elif random.random() < 0.05:
        event_type = event_type.upper()

    severity_score = random.choice(SEVERITY_SCORES)
    # Introduce missing severity_score
    if random.random() < 0.03: # 3% chance of missing score
        severity_score = None

    status = random.choice(STATUSES)
    reported_source = random.choice(REPORTED_SOURCES)

    impacted_regions = []
    num_regions = random.randint(0, 3) # 0 to 3 impacted regions
    for _ in range(num_regions):
        region = random.choice(IMPACTED_REGIONS_OPTIONS)
        if region not in impacted_regions:
            impacted_regions.append(region)
    impacted_regions_str = ",".join(impacted_regions) if impacted_regions else ""

    # Introduce missing impacted_regions
    if random.random() < 0.05: # 5% chance of missing impacted regions
        impacted_regions_str = ""


    data.append({
        'event_id': event_id,
        'timestamp_utc': timestamp_utc,
        'latitude': latitude,
        'longitude': longitude,
        'event_type': event_type,
        'severity_score': severity_score,
        'status': status,
        'reported_source': reported_source,
        'impacted_regions': impacted_regions_str
    })

# Create DataFrame
df = pd.DataFrame(data)

# Save to CSV
file_name = "global_event_data.csv"
df.to_csv(file_name, index=False)

print(f"Generated '{file_name}' with {NUM_RECORDS} records.")
print("\nFirst 5 rows:")
print(df.head())
print("\nSample of intentional data issues:")
print(df[df['severity_score'].isna()].head())
print(df[df['event_type'].apply(lambda x: x.islower() or x.isupper())].head())
print(df[(df['latitude'] > 90) | (df['latitude'] < -90) | (df['longitude'] > 180) | (df['longitude'] < -180)].head())