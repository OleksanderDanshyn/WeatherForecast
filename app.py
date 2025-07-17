import csv
import os
from datetime import datetime

import requests
from dotenv import load_dotenv

#from airflow.providers.standard.operators.python import PythonOperator
#from airflow import DAG

from sklearn.naive_bayes import GaussianNB
import pandas as pd
from sklearn.preprocessing import LabelEncoder

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
        "Weather": result.get('weather', [{}])[0].get('main'),
        "Time": datetime.fromtimestamp(result.get('dt'))
    }

def save_to_csv(data, clothing=None):
    filename = 'weather.csv'
    file_exists = os.path.isfile(filename)
    data['Clothing'] = clothing
    with open(filename, mode='a', newline='', encoding='utf') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=data.keys())
        if not file_exists:
            writer.writeheader()
        writer.writerow(data)


def fetch_and_save_weather():
    save_to_csv(get_data())

def train_model():
    df = pd.read_csv('weather.csv')
    df = df.dropna(subset=['Clothing'])
    features = ['Temperature', 'Feels_like', 'Humidity', 'Wind', 'Cloudiness']
    x = df[features]
    y = df['Clothing']

    label_encoder = LabelEncoder()
    y_encoded = label_encoder.fit_transform(y)

    model = GaussianNB()
    model.fit(x, y_encoded)
    return model, label_encoder


def predict_clothing(new_data, model, label_encoder):
    features = pd.DataFrame([{
        'Temperature': new_data['Temperature'],
        'Feels_like': new_data['Feels_like'],
        'Humidity': new_data['Humidity'],
        'Wind': new_data['Wind'],
        'Cloudiness': new_data['Cloudiness']
    }])

    prediction = model.predict(features)
    clothing = label_encoder.inverse_transform(prediction)
    return clothing[0]

if __name__ == '__main__':
    configure()
    data = get_data()

    model, label_encoder = train_model()
    clothing = predict_clothing(data, model, label_encoder)

    print("\nPredicted clothing recommendation:")
    print(f">>> You should wear: {clothing}")

    save_to_csv(data, clothing)

#with DAG(
#        dag_id="weather",
#        start_date=datetime(2025, 7, 15),
#        schedule="@hourly",
#        catchup=False
#) as dag:
#    fetch_and_save_csv = PythonOperator(
#        task_id="fetch_and_save_csv",
#        python_callable=fetch_and_save_weather
#    )
