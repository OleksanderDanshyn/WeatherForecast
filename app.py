import os
from flask import Flask, jsonify
import requests
from dotenv import load_dotenv
app = Flask(__name__)

def configure():
    load_dotenv(".env")

@app.route('/')
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
    return jsonify({
        "City": result.get('name'),
        "Temperature": result.get('main', {}).get('temp')
    })


if __name__ == '__main__':
    app.run()
