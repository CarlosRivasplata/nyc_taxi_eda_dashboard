import os

import numpy as np
import pandas as pd
from flask import Flask, render_template
import plotly.express as px
from plotly.io import to_html

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "data", "nyc_taxi.csv")

df = pd.read_csv(
    DATA_PATH,
    parse_dates=["tpep_pickup_datetime", "tpep_dropoff_datetime"]
)

df["trip_duration_min"] = (
    df["tpep_dropoff_datetime"] - df["tpep_pickup_datetime"]
).dt.total_seconds() / 60.0

df["pickup_date"] = df["tpep_pickup_datetime"].dt.date
df["pickup_hour"] = df["tpep_pickup_datetime"].dt.hour
df["pickup_dow"] = df["tpep_pickup_datetime"].dt.day_name()

df = df[(df["trip_distance"] > 0) & (df["trip_distance"] < 100)]
df = df[(df["trip_duration_min"] > 0) & (df["trip_duration_min"] < 300)]
df = df[(df["total_amount"] > 0) & (df["total_amount"] < 500)]

def get_sample(df, n=5000, random_state=42):
    if len(df) > n:
        return df.sample(n=n, random_state=random_state)
    return df

def create_trip_distance_histogram(df_sample):
    fig = px.histogram(
        df_sample,
        x="trip_distance",
        nbins=50,
        title="Distribución de la distancia del viaje (millas)",
    )
    return to_html(fig, full_html=False, include_plotlyjs="cdn")

def create_total_amount_histogram(df_sample):
    fig = px.histogram(
        df_sample,
        x="total_amount",
        nbins=50,
        title="Distribución del importe total ($)",
    )
    return to_html(fig, full_html=False, include_plotlyjs=False)

def create_trips_by_hour_bar(df_sample):
    trips_by_hour = (
        df_sample.groupby("pickup_hour")
        .size()
        .reset_index(name="num_trips")
        .sort_values("pickup_hour")
    )
    fig = px.bar(
        trips_by_hour,
        x="pickup_hour",
        y="num_trips",
        title="Número de viajes por hora del día",
    )
    return to_html(fig, full_html=False, include_plotlyjs=False)

def create_duration_by_dow_box(df_sample):
    fig = px.box(
        df_sample,
        x="pickup_dow",
        y="trip_duration_min",
        title="Duración del viaje por día de la semana (min)",
    )
    return to_html(fig, full_html=False, include_plotlyjs=False)

def create_fare_vs_distance_scatter(df_sample):
    fig = px.scatter(
        df_sample,
        x="trip_distance",
        y="total_amount",
        opacity=0.5,
        title="Relación entre distancia e importe total",
    )
    return to_html(fig, full_html=False, include_plotlyjs=False)

@app.route("/")
def dashboard():
    df_sample = get_sample(df)

    total_trips = len(df)
    avg_distance = round(df["trip_distance"].mean(), 2)
    avg_total_amount = round(df["total_amount"].mean(), 2)
    avg_duration = round(df["trip_duration_min"].mean(), 2)

    graph_trip_distance = create_trip_distance_histogram(df_sample)
    graph_total_amount = create_total_amount_histogram(df_sample)
    graph_trips_by_hour = create_trips_by_hour_bar(df_sample)
    graph_duration_by_dow = create_duration_by_dow_box(df_sample)
    graph_fare_vs_distance = create_fare_vs_distance_scatter(df_sample)

    return render_template(
        "dashboard.html",
        total_trips=total_trips,
        avg_distance=avg_distance,
        avg_total_amount=avg_total_amount,
        avg_duration=avg_duration,
        graph_trip_distance=graph_trip_distance,
        graph_total_amount=graph_total_amount,
        graph_trips_by_hour=graph_trips_by_hour,
        graph_duration_by_dow=graph_duration_by_dow,
        graph_fare_vs_distance=graph_fare_vs_distance,
    )

if __name__ == "__main__":
    app.run(debug=True)
