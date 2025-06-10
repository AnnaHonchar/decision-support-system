from prophet import Prophet
import pandas as pd
from datetime import timedelta

def generate_forecast(df):
    result = []

    # ✅ Нормалізація колонок
    df.columns = df.columns.str.strip().str.lower()

    # ✅ Гарантуємо, що колонка "date" — це datetime
    df["date"] = pd.to_datetime(df["date"], errors="coerce")

    # 🧹 Очищення NaT, порожніх та дублікатів
    df = df.dropna(subset=["date", "sales", "category"])
    df = df.drop_duplicates(subset=["date", "category"], keep="last")
    df = df.sort_values("date")

    # 🧾 Перевірка останньої дати з CSV
    last_actual_date = df["date"].max()

    # 🔁 Прогноз для кожної категорії окремо
    for category in df["category"].unique():

        cat_df = df[df["category"] == category].copy()
        cat_df.rename(columns={"date": "ds", "sales": "y"}, inplace=True)

        # 🔐 Захист від порожнього DataFrame після фільтрації
        if cat_df.empty:
            print("⚠️ Warning: Empty dataframe for category:", category)
            continue

        model = Prophet()
        model.fit(cat_df)

        future_dates = pd.date_range(start=last_actual_date + timedelta(days=1), periods=7)
        future = pd.DataFrame({"ds": future_dates})

        forecast = model.predict(future)

        for _, row in forecast.iterrows():
            result.append({
                "date": row["ds"].strftime("%Y-%m-%d"),
                "category": category,
                "predicted_sales": row["yhat"]
            })

    return result
