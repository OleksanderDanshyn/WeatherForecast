import csv
import os
from datetime import datetime

from flask import Flask, jsonify
import requests
from dotenv import load_dotenv
app = Flask(__name__)

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

@app.route('/weather')
def show_weather():
    data = get_data()
    print("Weather data requested via web:")
    for key, value in data.items():
        print(f"{key}: {value}")
    return jsonify(data)

if __name__ == '__main__':
    configure()
    data = get_data()
    print("Weather data: ")
    for key, value in data.items():
        print(f"{key}: {value}")
    save_to_csv(data)
    app.run()
