import json
import polars as pl
import requests
import boto3
from datetime import datetime


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


def save_sensors_as_parquet():
    with open("data/sensors.json", "r", encoding="utf-8") as f:
        sensors = json.load(f)

    sensors_data = []

    for row in sensors["data"]:
        sensors_data.append(row)

    sensors_df = pl.DataFrame(sensors_data, schema=sensors["fields"])
    sensors_df.write_parquet(
        "data/sensors.parquet", compression="zstd", compression_level=22
    )


def extract_historical_sensor_data(start: datetime, end: datetime):
    with open("data/sensors.json", "r", encoding="utf-8") as f:
        sensors = json.load(f)

    sensors = sensors["data"]
    fields = "humidity, temperature, pressure, \
        analog_input, \
        pm1.0_atm, pm1.0_cf_1, \
        pm2.5_alt, pm2.5_atm, pm2.5_cf_1, \
        pm10.0_atm, pm10.0_cf_1, \
        scattering_coefficient, deciviews, visual_range, \
        0.3_um_count, 0.5_um_count, 1.0_um_count, 2.5_um_count, 5.0_um_count, 10.0_um_count"

    api_key = "7CD6D264-0A25-11EE-BD21-42010A800008"
    headers = {"X-API-Key": api_key}
    payload = {
        "start_timestamp": start,
        "end_timestamp": end,
        "average": 60,
        "fields": fields,
    }

    agg_sensor_data = []

    count = 0

    for row in sensors:
        sensor_index = row[0]
        url = f"https://api.purpleair.com/v1/sensors/{sensor_index}/history"
        r = requests.get(url, headers=headers, params=payload)
        single_sensor_data = r.json()

        for entry in single_sensor_data["data"]:
            time_slice_sensor_data = entry
            time_slice_sensor_data.insert(0, sensor_index)
            agg_sensor_data.append(time_slice_sensor_data)

        count += 1

        if count == 10:
            break

    columns = single_sensor_data["fields"]
    columns.insert(0, "sensor_index")

    sensors_data_df = pl.DataFrame(agg_sensor_data, columns=columns)
    sensors_data_df.write_parquet(
        "data/sensors_data.parquet", compression="zstd", compression_level=22
    )
    sensors_data_df.write_csv("data/sensors_data.csv")


def load_sensors_to_s3():
    pass


def load_sensors_data_to_s3():
    pass


if __name__ == "__main__":
    start = datetime(2020, 9, 9).timestamp()
    end = datetime(2020, 9, 10).timestamp()
    extract_historical_sensor_data(start, end)
