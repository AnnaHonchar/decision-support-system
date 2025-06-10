from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score
import pandas as pd

def run_classification(df):
    df.columns = df.columns.str.strip().str.lower()

    required = {"product_name", "cost_price", "sale_price", "units_sold", "storage_cost"}
    if not required.issubset(df.columns):
        raise ValueError(f"Файл має містити колонки: {required}")

    if "margin" not in df.columns:
        df["margin"] = ((df["sale_price"] - df["cost_price"]) / df["cost_price"]) * 100

    features = ["cost_price", "sale_price", "units_sold", "storage_cost", "margin"]
    X = df[features]

    result_table = []
    metrics = {}

    if "profitable" in df.columns:
        y = df["profitable"]
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        model = LogisticRegression()
        model.fit(X_train, y_train)

        y_pred = model.predict(X_test)

        metrics = {
            "accuracy": round(accuracy_score(y_test, y_pred), 3),
            "precision": round(precision_score(y_test, y_pred), 3),
            "recall": round(recall_score(y_test, y_pred), 3)
        }

        predictions = model.predict(X)
        df["predicted_profitable"] = predictions
    else:
        raise ValueError("Колонка 'profitable' відсутня. Навчання неможливе.")

    for _, row in df.iterrows():
        result_table.append({
            "product": row["product_name"],
            "predicted": int(row["predicted_profitable"])
        })

    return result_table, metrics