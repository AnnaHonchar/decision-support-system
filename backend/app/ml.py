import pandas as pd
import os
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from xgboost import XGBRegressor
import matplotlib
matplotlib.use('Agg')  # <-- не дозволяє відкривати вікна
import matplotlib.pyplot as plt
import io
import base64
from sklearn.metrics import classification_report, accuracy_score
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
import numpy as np

def preprocess_data(filepath):
    df = pd.read_csv(filepath)

    # Видаляємо порожні колонки
    df.dropna(axis=1, how='all', inplace=True)

    # Видаляємо рядки з відсутніми значеннями
    df.dropna(inplace=True)

    # Перетворюємо всі об'єктні (текстові) стовпці в числа
    for col in df.select_dtypes(include='object').columns:
        le = LabelEncoder()
        df[col] = le.fit_transform(df[col])

    return df

def train_and_predict(filepath):
    df = preprocess_data(filepath)

    X = df.iloc[:, :-1]
    y = df.iloc[:, -1]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = XGBRegressor()
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)

    # Метрики регресії
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    r2 = r2_score(y_test, y_pred)
    mae = mean_absolute_error(y_test, y_pred)

    # Побудова графіка порівняння
    plt.figure(figsize=(8, 4))
    plt.plot(y_test.values, label='Actual', marker='o')
    plt.plot(y_pred, label='Predicted', marker='x')
    plt.legend()
    plt.title("Actual vs Predicted Sales")

    # Збереження в base64
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    image_base64 = base64.b64encode(buf.read()).decode('utf-8')
    buf.close()
    plt.close()

    result = {
        "rmse": round(rmse, 2),
        "mae": round(mae, 2),
        "r2_score": round(r2, 2),
        "chart_base64": image_base64,
        "predictions": y_pred.tolist()
    }

    return result