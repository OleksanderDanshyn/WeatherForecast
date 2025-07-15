import csv
import os
from datetime import datetime
import requests
from airflow.providers.standard.operators.python import PythonOperator
from dotenv import load_dotenv
from airflow import DAG


def configure():
    load_dotenv(".env")

def get_data():
    api_key = os.getenv('API_KEY')
    url = 'http://api.openweathermap.org/data/2.5/weather'
    params = {
        "lat": 52.22,
        "lon": 21.01,
        "appid": api_key,
        "units": "metric"
    }

    data = requests.get(url, params=params)
    data.raise_for_status()

    result = data.json()
    return {
        "City": result.get('name'),
        "Temperature": result.get('main', {}).get('temp'),
        "Feels_like": result.get('main', {}).get('feels_like'),
        "Humidity": result.get('main', {}).get('humidity'),
        "Wind": result.get('wind', {}).get('speed'),
        "Cloudiness": result.get('clouds', {}).get('all'),
        "Time": datetime.fromtimestamp(result.get('dt'))
    }

def save_to_csv(data):
    filename = 'weather.csv'
    file_exists = os.path.isfile(filename)
    with open(filename, mode='a', newline='', encoding='utf') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=data.keys())
        if not file_exists:
            writer.writeheader()
        writer.writerow(data)


def fetch_and_save_weather():
    save_to_csv(get_data())

if __name__ == '__main__':
    configure()
    data = get_data()
    print("Weather data: ")
    for key, value in data.items():
        print(f"{key}: {value}")

with DAG(
        dag_id="weather",
        start_date=datetime(2025, 7, 15),
        schedule="@hourly",
):
    fetch_and_save_csv = PythonOperator(
        task_id="fetch_and_save_csv",
        python_callable=fetch_and_save_weather
    )
    fetch_and_save_csv.set_upstream()
