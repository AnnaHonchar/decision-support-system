import pandas as pd
from datetime import datetime, timedelta
import random

def predict_sales(filepath):
    df = pd.read_csv(filepath)
    df['date'] = pd.to_datetime(df['date'])

    # Групуємо за категоріями та обчислюємо середні денні продажі
    summary = df.groupby('category')['sales'].mean().reset_index()

    forecast = []
    today = datetime.today().date()

    for i in range(7):  # прогноз на 7 днів вперед
        target_date = today + timedelta(days=i)
        for _, row in summary.iterrows():
            base = row['sales']
            noise = random.uniform(-0.1, 0.1) * base
            forecast.append({
                "predicted_date": target_date,
                "predicted_sales": round(base + noise, 2),
                "category": row['category']
            })

    return forecast