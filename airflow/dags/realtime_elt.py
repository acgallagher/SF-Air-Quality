from airflow.decorators import dag, task
import json
import polars as pl
import requests
import boto3
from datetime import datetime
import logging
from botocore.exceptions import ClientError
import os


@dag(start_date=datetime.today(), schedule="@daily", catchup=False)
def realtime_elt():
    @task()
    def extract_realtime_sf_sensors_data():
        url = "https://api.purpleair.com/v1/sensors"

        api_key = "7CD6D264-0A25-11EE-BD21-42010A800008"
        headers = {"X-API-Key": api_key}
        fields = "humidity, temperature, pressure, \
            voc, analog_input, \
            pm1.0_atm, pm1.0_cf_1, \
            pm2.5_alt, pm2.5_atm, pm2.5_cf_1, \
            pm10.0_atm, pm10.0_cf_1, \
            scattering_coefficient, deciviews, visual_range, \
            0.3_um_count, 0.5_um_count, 1.0_um_count, 2.5_um_count, 5.0_um_count, 10.0_um_count"
        payload = {
            "fields": fields,
            "nwlng": -122.53142306021361,
            "nwlat": 37.811659965839596,
            "selng": -122.34937561032184,
            "selat": 37.70831681790109,
        }

        r = requests.get(url, headers=headers, params=payload)
        data = r.json()
        print(data)

        with open(
            "/opt/airflow/data/sensors_realtime.json", "w", encoding="utf-8"
        ) as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

        return "/opt/airflow/data/sensors_realtime.json"

    @task()
    def save_sensor_data_as_parquet(json_path):
        with open(json_path, "r", encoding="utf-8") as f:
            sensors = json.load(f)

        sensors_data = []

        for row in sensors["data"]:
            sensors_data.append(row)

        sensors_df = pl.DataFrame(sensors_data, schema=sensors["fields"])
        sensors_df.write_parquet(
            "/opt/airflow/data/sensors_realtime.parquet",
            compression="zstd",
            compression_level=22,
        )

        return "/opt/airflow/data/sensors_realtime.parquet"

    @task()
    def upload_file_to_s3(file_name, bucket, object_name=None):
        """Upload a file to an S3 bucket

        :param file_name: File to upload
        :param bucket: Bucket to upload to
        :param object_name: S3 object name. If not specified then file_name is used
        :return: True if file was uploaded, else False
        """

        # If S3 object_name was not specified, use file_name
        if object_name is None:
            object_name = os.path.basename(file_name)

        # Load AWS Credentials
        credentials = {}
        with open("/opt/airflow/config/aws_credentials.csv") as f:
            for line in f.readlines():
                values = line.strip("\n").split(",")
                credentials[values[0]] = values[1]

        s3_client = boto3.client(
            "s3",
            aws_access_key_id=credentials["access_key"],
            aws_secret_access_key=credentials["secret_access_key"],
        )

        # Upload the file
        try:
            response = s3_client.upload_file(file_name, bucket, object_name)
        except ClientError as e:
            logging.error(e)
            return False
        return True

    json_path = extract_realtime_sf_sensors_data()
    parquet_path = save_sensor_data_as_parquet(json_path)
    upload_file_to_s3(parquet_path, "sf-air-quality-bucket")


realtime_elt()