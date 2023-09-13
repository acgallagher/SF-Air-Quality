from airflow.decorators import dag, task
import json
import polars as pl
import requests
import boto3
from datetime import datetime


@dag(start_date=datetime.today(), schedule="@daily", catchup=False)
def orange_day_elt():
    @task()
    def extract_sf_sensors():
        url = "https://api.purpleair.com/v1/sensors"
        api_key = "7CD6D264-0A25-11EE-BD21-42010A800008"
        headers = {"X-API-Key": api_key}
        fields = "name, icon, model, hardware, location_type, private, latitude, longitude, altitude, position_rating, led_brightness, firmware_version, firmware_upgrade, rssi, uptime, pa_latency, memory, last_seen, last_modified, date_created, channel_state, channel_flags, channel_flags_manual, channel_flags_auto, confidence, confidence_manual, confidence_auto"

        payload = {
            "fields": fields,
            "nwlng": -122.53142306021361,
            "nwlat": 37.811659965839596,
            "selng": -122.34937561032184,
            "selat": 37.70831681790109,
        }

        r = requests.get(url, headers=headers, params=payload)
        data = r.json()

        with open("data/sensors.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    extract_sf_sensors()


orange_day_elt()
