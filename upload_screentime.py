import requests
import json
import os
from datetime import datetime, timedelta

# 1. Fetch all buckets
buckets_url = "http://localhost:5600/api/0/buckets/"
response = requests.get(buckets_url)
buckets = response.json()  # Returns a dict {bucket_id: bucket_details}

# 2. Find AFK and App buckets
afk_bucket_id = next(
    (bid for bid in buckets if "aw-watcher-afk" in bid),
    None
)
app_bucket_id = next(
    (bid for bid in buckets if "aw-watcher-window" in bid),
    None
)

if not afk_bucket_id or not app_bucket_id:
    print("Error: AFK or App bucket not found!")
    exit(1)

# 3. Get events from buckets for the last 24 hours
now = datetime.now().astimezone()
start_time = (now - timedelta(hours=24)).isoformat()
end_time = now.isoformat()

def get_events(bucket_id):
    events_url = f"http://localhost:5600/api/0/buckets/{bucket_id}/events"
    params = {
        "start": start_time,
        "end": end_time,
        "limit": -1  # Get all events
    }
    response = requests.get(events_url, params=params)
    return response.json()

afk_events = get_events(afk_bucket_id)
app_events = get_events(app_bucket_id)

# 4. Calculate total active time (non-AFK)
total_duration = sum(
    event["duration"] for event in afk_events 
    if event["data"]["status"] == "not-afk"
) / 3600  # Convert to hours

# 5. Get top 5 apps
app_usage = {}
for event in app_events:
    app_name = event["data"].get("app", "Unknown")
    app_usage[app_name] = app_usage.get(app_name, 0) + event["duration"]

top_apps = sorted(app_usage.items(), key=lambda x: x[1], reverse=True)[:5]

# 6. Save to JSON
output = {
    "total_time": round(total_duration, 2),
    "top_apps": [{"app": app[0], "duration": app[1]} for app in top_apps]
}

with open("screentime.json", "w") as f:
    json.dump(output, f, indent=2)

print("✅ Data saved to screentime.json!")

# 7. Push to GitHub (your existing code)
os.chdir(r"C:\Users\Shrey\OneDrive\Desktop\FINAL PROJECT\screen-time-data")
os.system('git add screentime.json')
os.system('git commit -m "Update screen time data"')
os.system('git push https://ShreyasSondur:ghp_yourPAT@github.com/ShreyasSondur/screen-time-data.git main')