import pandas as pd
import numpy as np

def run_topsis(df):
    data = df.copy()
    product_names = data["product"].values
    data = data.drop("product", axis=1)

    # Нормалізація
    norm = np.sqrt((data ** 2).sum())
    norm_data = data / norm

    # Ваги критеріїв (можеш змінити під задачу)
    weights = np.array([0.4, 0.2, 0.3, 0.1])  # Наприклад: прибуток, попит, вартість, площа

    weighted_data = norm_data * weights

    # Ідеальні (кращі та гірші) рішення
    ideal_best = weighted_data.max()
    ideal_worst = weighted_data.min()

    # Відстані до ідеального та анти-ідеального
    dist_best = np.sqrt(((weighted_data - ideal_best) ** 2).sum(axis=1))
    dist_worst = np.sqrt(((weighted_data - ideal_worst) ** 2).sum(axis=1))

    # TOPSIS score
    scores = dist_worst / (dist_best + dist_worst)

    # Ранжування (від кращого до гіршого)
    ranking_indices = np.argsort(scores)[::-1]
    ranked_products = product_names[ranking_indices]

    # Формування текстового висновку
    result_text = "З отриманих результатів можемо зробити висновок, що найкращим товаром для включення в асортимент є "
    for i, prod in enumerate(ranked_products):
        if i == 0:
            result_text += f"{prod}"
        elif i == len(ranked_products) - 1:
            result_text += f", потім – {prod}."
        else:
            result_text += f", далі – {prod}"
    
    return result_text
