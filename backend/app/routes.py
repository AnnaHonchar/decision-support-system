from flask import Blueprint, jsonify
import pandas as pd

api = Blueprint("api", __name__)

@api.route("/ping", methods=["GET"])
def ping():
    return jsonify({"message": "pong!"})

from flask import request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from app.models import User
from app.db import db
from app.models import Recommendation

@api.route("/register", methods=["POST"])
def register():
    data = request.json
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")

    if not username or not email or not password:
        return jsonify({"error": "Всі поля обов’язкові"}), 400

    if User.query.filter((User.username == username) | (User.email == email)).first():
        return jsonify({"error": "Користувач з таким ім’ям або email вже існує"}), 409

    hashed_password = generate_password_hash(password)
    user = User(username=username, email=email, password=hashed_password)
    db.session.add(user)
    db.session.commit()

    return jsonify({"message": "Користувач успішно зареєстрований"}), 201

@api.route("/login", methods=["POST"])
def login():
    data = request.json
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "Заповніть усі поля"}), 400

    user = User.query.filter_by(email=email).first()

    if not user or not check_password_hash(user.password, password):
        return jsonify({"error": "Невірний email або пароль"}), 401

    return jsonify({
        "message": "Авторизація успішна",
        "username": user.username,
        "user_id": user.id
    }), 200

import os
from datetime import datetime
from flask import current_app
from werkzeug.utils import secure_filename
from app.models import Dataset

@api.route("/upload", methods=["POST"])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "Файл не надіслано"}), 400

    file = request.files['file']
    user_id = request.form.get('user_id')

    if not user_id:
        return jsonify({"error": "Не вказано ID користувача"}), 400

    if file.filename == '':
        return jsonify({"error": "Файл не вибрано"}), 400

    filename = secure_filename(file.filename)
    upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    file.save(upload_path)

    dataset = Dataset(
        user_id=user_id,
        filename=filename,
        upload_date=datetime.utcnow()
    )
    db.session.add(dataset)
    db.session.commit()

    return jsonify({"message": "Файл завантажено", "dataset_id": dataset.id}), 200

from app.ml import train_and_predict
from app.models import Dataset, Prediction, ClassificationResult
import os
from flask import current_app
from datetime import datetime

@api.route("/analyze", methods=["POST"])
def analyze():
    data = request.json
    dataset_id = data.get("dataset_id")

    if not dataset_id:
        return jsonify({"error": "Не вказано dataset_id"}), 400

    dataset = Dataset.query.get(dataset_id)

    if not dataset:
        return jsonify({"error": "Набір даних не знайдено"}), 404

    filepath = os.path.join(current_app.config["UPLOAD_FOLDER"], dataset.filename)

    if not os.path.exists(filepath):
        return jsonify({"error": "Файл не знайдено"}), 404

    try:
        result = train_and_predict(filepath)

        rmse = result["rmse"]
        r2 = result["r2_score"]
        mae = result["mae"]

        # Формування рекомендації на основі RMSE
        if rmse <= 10:
            recommendation_text = "Прогноз досить точний. Можна використовувати для прийняття рішень."
        elif rmse <= 25:
            recommendation_text = "Прогноз помірної точності. Рекомендується перевірити структуру даних."
        else:
            recommendation_text = "Низька точність прогнозу. Спробуйте покращити якість або кількість даних."

        # Збереження результату в predictions
        prediction = Prediction(
            dataset_id=dataset_id,
            created_at=datetime.utcnow(),
            result_summary=f"RMSE: {rmse:.2f}, R²: {r2:.2f}, MAE: {mae:.2f}"
        )
        db.session.add(prediction)
        db.session.commit()

        # Збереження рекомендації
        from app.models import Recommendation
        rec = Recommendation(
            prediction_id=prediction.id,
            text=recommendation_text,
            created_at=datetime.utcnow()
        )
        db.session.add(rec)
        db.session.commit()

        return jsonify({
            "message": "Аналіз завершено",
            "rmse": rmse,
            "mae": mae,
            "r2_score": r2,
            "recommendation": recommendation_text,
            "chart_base64": result["chart_base64"]
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@api.route("/results", methods=["GET"])
def get_results():
    user_id = request.args.get("user_id")

    if not user_id:
        return jsonify({"error": "Не вказано user_id"}), 400

    datasets = Dataset.query.filter_by(user_id=user_id).all()

    if not datasets:
        return jsonify({"message": "Немає результатів для цього користувача"}), 200

    output = []

    for dataset in datasets:
        prediction = Prediction.query.filter_by(dataset_id=dataset.id).order_by(Prediction.created_at.desc()).first()
        if not prediction:
            continue

        recommendation = Recommendation.query.filter_by(prediction_id=prediction.id).first()

        output.append({
            "dataset_id": dataset.id,
            "filename": dataset.filename,
            "uploaded": dataset.upload_date,
            "prediction_accuracy": prediction.result_summary,
            "predicted_at": prediction.created_at,
            "recommendation": recommendation.text if recommendation else "Рекомендації відсутні"
        })

    return jsonify(output), 200

@api.route("/clean/<int:dataset_id>", methods=["POST"])
def clean_data(dataset_id):
    dataset = Dataset.query.get(dataset_id)

    if not dataset:
        return jsonify({"error": "Набір даних не знайдено"}), 404

    filepath = os.path.join(current_app.config["UPLOAD_FOLDER"], dataset.filename)

    try:
        df = pd.read_csv(filepath)

        # Очищення: видалення дублікатів і порожніх значень
        df.drop_duplicates(inplace=True)
        df.dropna(inplace=True)

        # Перезапис очищеного файлу
        df.to_csv(filepath, index=False)

        return jsonify({"message": "Дані очищено"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@api.route("/history", methods=["GET"])
def get_history():
    user_id = request.args.get("user_id")
    query = request.args.get("q", "").lower()

    if not user_id:
        return jsonify({"error": "Не вказано user_id"}), 400

    datasets = Dataset.query.filter_by(user_id=user_id).all()
    history = []

    for dataset in datasets:
        prediction = Prediction.query.filter_by(dataset_id=dataset.id).order_by(Prediction.created_at.desc()).first()
        topsis = TopsisResult.query.filter_by(dataset_id=dataset.id).first()
        classification_entries = ClassificationResult.query.filter_by(dataset_id=dataset.id).all()

        if prediction:
            method = "prophet"
            accuracy = prediction.result_summary
            recommendation = Recommendation.query.filter_by(prediction_id=prediction.id).first()
            recommendation_text = recommendation.text if recommendation else "N/A"
        elif topsis:
            method = "topsis"
            accuracy = "N/A"
            recommendation_text = topsis.result_text
        elif classification_entries:
            method = "classification"
            accuracy = "—"
            recommendation_text = "Класифікація завершена: " + ", ".join([
                f"{c.product_name} → {'Вигідний' if c.predicted_profitable else 'Невигідний'}"
                for c in classification_entries
            ])
        else:
            method = "N/A"
            accuracy = "N/A"
            recommendation_text = "N/A"

        item = {
            "filename": dataset.filename,
            "uploaded_at": dataset.upload_date.strftime("%Y-%m-%d %H:%M:%S"),
            "accuracy": accuracy,
            "recommendation": recommendation_text,
            "dataset_id": dataset.id,
            "method": method
        }


        # Пошук: фільтрація за текстом
        combined_text = f"{item['filename']} {item['accuracy']} {item['recommendation']}".lower()
        if query in combined_text:
            history.append(item)
        elif not query:  # якщо пошуковий рядок порожній — показати всі
            history.append(item)

    return jsonify(history), 200

@api.route("/history/<int:dataset_id>", methods=["DELETE"])
def delete_history_item(dataset_id):
    dataset = Dataset.query.get(dataset_id)
    if not dataset:
        return jsonify({"error": "Набір даних не знайдено"}), 404

    # Видалення рекомендацій
    predictions = Prediction.query.filter_by(dataset_id=dataset_id).all()
    for prediction in predictions:
        Recommendation.query.filter_by(prediction_id=prediction.id).delete()

    # Видалення прогнозів
    Prediction.query.filter_by(dataset_id=dataset_id).delete()

    # Видалення датасету
    db.session.delete(dataset)
    db.session.commit()

    return jsonify({"message": "Прогноз успішно видалено"}), 200

@api.route("/profile/<int:user_id>", methods=["PUT"])
def update_profile(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "Користувача не знайдено"}), 404

    data = request.json
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")

    if username:
        user.username = username
    if email:
        # Перевірка, чи такий email вже використовується іншим користувачем
        existing_user = User.query.filter(User.email == email, User.id != user_id).first()
        if existing_user:
            return jsonify({"error": "Цей email вже використовується іншим користувачем"}), 409
        user.email = email
    if password:
        user.password = generate_password_hash(password)

    db.session.commit()
    return jsonify({"message": "Профіль успішно оновлено"}), 200

@api.route("/profile/<int:user_id>", methods=["GET"])
def get_profile(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "Користувача не знайдено"}), 404

    return jsonify({
        "username": user.username,
        "email": user.email
    }), 200

import pandas as pd

from fpdf import FPDF
import io
from flask import send_file

from flask import request, jsonify, send_file, current_app
from app.models import Dataset, Prediction, Recommendation, TopsisResult, ClassificationResult, SalesPrediction, SalesRecommendation
from fpdf import FPDF
import pandas as pd
import os
import io

@api.route("/export/<int:dataset_id>", methods=["GET"])
def export_prediction(dataset_id):
    export_format = request.args.get("format", "pdf")
    dataset = Dataset.query.get(dataset_id)
    if not dataset:
        return jsonify({"error": "Набір даних не знайдено"}), 404

    prediction = Prediction.query.filter_by(dataset_id=dataset_id).first()
    topsis = TopsisResult.query.filter_by(dataset_id=dataset_id).first()
    classification = ClassificationResult.query.filter_by(dataset_id=dataset_id).all()
    sales_predictions = SalesPrediction.query.filter_by(dataset_id=dataset_id).all()
    recommendations = SalesRecommendation.query.filter_by(dataset_id=dataset_id).all()
    rec_map = {r.category: r.recommendation for r in recommendations}

    filename = dataset.filename
    uploaded_at = dataset.upload_date.strftime("%Y-%m-%d %H:%M:%S")

    if topsis and not classification:
        if export_format == "excel":
            return jsonify({"error": "Формат Excel недоступний для TOPSIS"}), 400

        # TOPSIS — лише PDF з текстом result_text
        pdf = FPDF()
        font_path = os.path.join("fonts", "DejaVuSans.ttf")
        pdf.add_font("DejaVu", "", font_path, uni=True)
        pdf.set_font("DejaVu", size=12)
        pdf.add_page()
        pdf.cell(200, 10, txt="Звіт TOPSIS", ln=True, align='C')
        pdf.ln(10)
        pdf.cell(200, 10, txt=f"Файл: {filename}", ln=True)
        pdf.cell(200, 10, txt=f"Дата завантаження: {uploaded_at}", ln=True)
        pdf.multi_cell(0, 10, txt=f"Рекомендація: {topsis.result_text}")

        buffer = io.BytesIO(pdf.output(dest='S').encode('latin1'))
        buffer.seek(0)
        return send_file(buffer, as_attachment=True, download_name="topsis_result.pdf", mimetype="application/pdf")

    if classification:
        rows = [{
            "Товар": c.product_name,
            "Результат": "Вигідний" if c.predicted_profitable else "Невигідний"
        } for c in classification]

        if export_format == "excel":
            df = pd.DataFrame(rows)
            buffer = io.BytesIO()
            df.to_excel(buffer, index=False, engine='openpyxl')
            buffer.seek(0)
            return send_file(
                buffer,
                as_attachment=True,
                download_name="classification.xlsx",
                mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

        elif export_format == "pdf":
            pdf = FPDF()
            font_path = os.path.join("fonts", "DejaVuSans.ttf")
            pdf.add_font("DejaVu", "", font_path, uni=True)
            pdf.set_font("DejaVu", size=12)
            pdf.add_page()
            pdf.cell(200, 10, txt="Звіт класифікації", ln=True, align='C')
            pdf.ln(10)
            pdf.cell(200, 10, txt=f"Файл: {filename}", ln=True)
            pdf.cell(200, 10, txt=f"Дата: {uploaded_at}", ln=True)
            pdf.ln(5)
            for row in rows:
                pdf.cell(200, 10, txt=f"{row['Товар']}: {row['Результат']}", ln=True)

            buffer = io.BytesIO(pdf.output(dest='S').encode('latin1'))
            buffer.seek(0)
            return send_file(buffer, as_attachment=True, download_name="classification.pdf", mimetype="application/pdf")

    if prediction:
        accuracy = prediction.result_summary
        recommendation = Recommendation.query.filter_by(prediction_id=prediction.id).first()
        recommendation_text = recommendation.text if recommendation else "Рекомендація відсутня"

        # Перший прогноз Prophet з forecast таблицею
        forecast_rows = [
            {
                "Дата": p.predicted_date.strftime("%Y-%m-%d"),
                "Категорія": p.category,
                "Прогнозовані продажі": p.predicted_sales,
                "Рекомендація": rec_map.get(p.category, "—")
            }
            for p in sales_predictions
        ]

        if export_format == "excel":
            df = pd.DataFrame(forecast_rows)
            buffer = io.BytesIO()
            df.to_excel(buffer, index=False, engine='openpyxl')
            buffer.seek(0)
            return send_file(
                buffer,
                as_attachment=True,
                download_name="forecast.xlsx",
                mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

        elif export_format == "pdf":
            pdf = FPDF()
            font_path = os.path.join("fonts", "DejaVuSans.ttf")
            pdf.add_font("DejaVu", "", font_path, uni=True)
            pdf.set_font("DejaVu", size=12)
            pdf.add_page()
            pdf.cell(200, 10, txt="Звіт прогнозування (Prophet)", ln=True, align='C')
            pdf.ln(10)
            pdf.cell(200, 10, txt=f"Файл: {filename}", ln=True)
            pdf.cell(200, 10, txt=f"Дата завантаження: {uploaded_at}", ln=True)
            pdf.cell(200, 10, txt=f"Точність: {accuracy}", ln=True)
            pdf.multi_cell(0, 10, txt=f"Рекомендація: {recommendation_text}")
            pdf.ln(5)
            for row in forecast_rows:
                pdf.cell(200, 10, txt=f"{row['Дата']} — {row['Категорія']}: {row['Прогнозовані продажі']} ({row['Рекомендація']})", ln=True)

            buffer = io.BytesIO(pdf.output(dest='S').encode('latin1'))
            buffer.seek(0)
            return send_file(buffer, as_attachment=True, download_name="forecast.pdf", mimetype="application/pdf")

    return jsonify({"error": "Немає доступних даних для експорту"}), 400
    
from app.sales_forecast import predict_sales
from app.models import SalesPrediction, Dataset

@api.route("/forecast/<int:dataset_id>", methods=["POST"])
def forecast_sales(dataset_id):
    dataset = Dataset.query.get(dataset_id)
    if not dataset:
        return jsonify({"error": "Набір даних не знайдено"}), 404

    filepath = os.path.join(current_app.config["UPLOAD_FOLDER"], dataset.filename)
    try:
        forecast = predict_sales(filepath)

        # Групуємо по категоріях
        category_summary = {}
        for item in forecast:
            cat = item["category"]
            category_summary.setdefault(cat, []).append(item["predicted_sales"])

        for item in forecast:
            entry = SalesPrediction(
                dataset_id=dataset_id,
                predicted_date=item["predicted_date"],
                predicted_sales=item["predicted_sales"],
                category=item["category"]
            )
            db.session.add(entry)
        db.session.commit()

        for category, values in category_summary.items():
            avg = sum(values) / len(values)
            if avg >= 13:
                rec_text = "Варто поповнити склад"
            elif avg < 10:
                rec_text = "Зниження попиту, зменшіть запаси"
            else:
                rec_text = "Стабільний попит"

            rec_entry = SalesRecommendation(
                dataset_id=dataset_id,
                category=category,
                recommendation=rec_text
            )
            db.session.add(rec_entry)

        db.session.commit()
        return jsonify({"message": "Прогноз успішно створено", "forecast": forecast})

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@api.route("/forecast_data/<int:dataset_id>", methods=["GET"])
def get_forecast_data(dataset_id):
    predictions = SalesPrediction.query.filter_by(dataset_id=dataset_id).all()

    result = [
        {
            "date": pred.predicted_date.strftime("%Y-%m-%d"),
            "sales": pred.predicted_sales,
            "category": pred.category
        }
        for pred in predictions
    ]

    return jsonify(result), 200

from app.prophet_forecast import generate_forecast
from app.models import SalesRecommendation
@api.route("/real_forecast/<int:dataset_id>", methods=["POST"])
def real_forecast(dataset_id):
    dataset = Dataset.query.get(dataset_id)
    if not dataset:
        return jsonify({"error": "Набір даних не знайдено"}), 404

    filepath = os.path.join(current_app.config["UPLOAD_FOLDER"], dataset.filename)

    try:
        # 🧹 Очистити старі прогнози
        SalesPrediction.query.filter_by(dataset_id=dataset_id).delete()
        SalesRecommendation.query.filter_by(dataset_id=dataset_id).delete()
        db.session.commit()

        # 📥 Завантажити CSV
        df = pd.read_csv(filepath)

        # ✅ Перевірка на потрібні колонки (всю решту — всередині generate_forecast)
        df.columns = df.columns.str.strip().str.lower()
        required = {"date", "category", "sales"}
        if not required.issubset(df.columns):
            return jsonify({"error": f"Файл повинен містити колонки: {required}"}), 400

        # 🔮 Генерація прогнозу
        forecast_list = generate_forecast(df)

        # 📊 Групування для рекомендацій
        category_summary = {}
        for item in forecast_list:
            cat = item["category"]
            category_summary.setdefault(cat, []).append(item["predicted_sales"])

        # 💾 Зберегти прогноз
        for item in forecast_list:
            db.session.add(SalesPrediction(
                dataset_id=dataset_id,
                predicted_date=item["date"],
                predicted_sales=item["predicted_sales"],
                category=item["category"]
            ))

        # 💬 Зберегти рекомендації
        for category, values in category_summary.items():
            avg = sum(values) / len(values)
            if avg >= 13:
                rec_text = "Варто поповнити склад"
            elif avg < 10:
                rec_text = "Зниження попиту, зменшіть запаси"
            else:
                rec_text = "Стабільний попит"

            db.session.add(SalesRecommendation(
                dataset_id=dataset_id,
                category=category,
                recommendation=rec_text
            ))

        db.session.commit()

        return jsonify({"message": "Прогноз збережено успішно", "forecast": forecast_list}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500



    
@api.route("/forecast_results/<int:dataset_id>", methods=["GET"])
def get_forecast_results(dataset_id):  # <--- інша назва
    predictions = SalesPrediction.query.filter_by(dataset_id=dataset_id).all()
    recs = SalesRecommendation.query.filter_by(dataset_id=dataset_id).all()
    rec_map = {r.category: r.recommendation for r in recs}

    result = []
    for p in predictions:
        result.append({
            "date": p.predicted_date.strftime("%Y-%m-%d"),
            "category": p.category,
            "sales": p.predicted_sales,
            "recommendation": rec_map.get(p.category, "Рекомендація відсутня")
        })

    return jsonify(result), 200
@api.route("/combined_forecast/<int:dataset_id>", methods=["GET"])
def combined_forecast(dataset_id):
    import traceback

    dataset = Dataset.query.get(dataset_id)
    if not dataset:
        return jsonify({"error": "Набір даних не знайдено"}), 404

    filepath = os.path.join(current_app.config["UPLOAD_FOLDER"], dataset.filename)
    try:
        df = pd.read_csv(filepath)

        # Нормалізуємо назви колонок
        df.columns = df.columns.str.strip().str.lower()

        # Перейменовуємо value → sales (після нормалізації!)
        if "value" in df.columns:
            df.rename(columns={"value": "sales"}, inplace=True)

        # Діагностичний вивід:
        print("DF COLUMNS:", df.columns.tolist())

        # Перевірка на наявність потрібних колонок
        required_cols = {"date", "category", "sales"}
        if not required_cols.issubset(df.columns):
            return jsonify({"error": f"CSV має містити колонки: {required_cols}"}), 400

        # Дата
        df["date"] = pd.to_datetime(df["date"])



        # Фактичні дані
        actual_data = {}
        for cat in df["category"].unique():
            cat_data = df[df["category"] == cat][["date", "sales"]]
            actual_data[cat] = [
                {"date": d.strftime("%Y-%m-%d"), "sales": float(s)}
                for d, s in zip(cat_data["date"], cat_data["sales"])
            ]

        # Прогноз
        forecast_data = generate_forecast(df)  # [{date, category, predicted_sales}...]

        forecast_grouped = {}
        for item in forecast_data:
            forecast_grouped.setdefault(item["category"], []).append({
                "date": item["date"],
                "sales": item["predicted_sales"]
            })

        # Обʼєднання
        result = []
        for cat in actual_data:
            result.append({
                "category": cat,
                "actual": actual_data.get(cat, []),
                "forecast": forecast_grouped.get(cat, [])
            })

        return jsonify(result), 200

    except Exception as e:
        print("=== ПОМИЛКА ===")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

from flask import Blueprint, request, jsonify, current_app
import os
import pandas as pd
from werkzeug.utils import secure_filename
from app import db
from app.models import Dataset, TopsisResult
from utils.topsis import run_topsis

topsis_bp = Blueprint("topsis", __name__)

@api.route("/topsis", methods=["POST"])
def topsis_analysis():
    if "file" not in request.files:
        return jsonify({"error": "Файл не надіслано"}), 400

    file = request.files["file"]
    user_id = request.form.get("user_id")

    if not user_id:
        return jsonify({"error": "Не вказано user_id"}), 400
    if file.filename == "":
        return jsonify({"error": "Файл не вибрано"}), 400

    try:
        # Зберігаємо файл
        filename = secure_filename(file.filename)
        upload_path = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
        file.save(upload_path)

        # Додаємо до бази
        dataset = Dataset(
            user_id=user_id,
            filename=filename,
            upload_date=datetime.utcnow()
        )
        db.session.add(dataset)
        db.session.commit()

        # Обробка через TOPSIS
        df = pd.read_csv(upload_path)
        result_text = run_topsis(df)

        topsis_result = TopsisResult(
            dataset_id=dataset.id,
            result_text=result_text
        )
        db.session.add(topsis_result)
        db.session.commit()

        return jsonify({
            "message": "TOPSIS аналіз завершено",
            "result": result_text
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@api.route("/classify", methods=["POST"])
def classify_products():
    from app.models import Dataset, ClassificationResult
    from app.classifier import run_classification

    if "file" not in request.files:
        return jsonify({"error": "Файл не надіслано"}), 400

    file = request.files["file"]
    user_id = request.form.get("user_id")

    if not user_id:
        return jsonify({"error": "Не вказано user_id"}), 400
    if file.filename == "":
        return jsonify({"error": "Файл не вибрано"}), 400

    try:
        filename = secure_filename(file.filename)
        upload_path = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
        file.save(upload_path)

        dataset = Dataset(user_id=user_id, filename=filename, upload_date=datetime.utcnow())
        db.session.add(dataset)
        db.session.commit()

        df = pd.read_csv(upload_path)
        result_table, metrics = run_classification(df)

        for item in result_table:
            db.session.add(ClassificationResult(
                dataset_id=dataset.id,
                product_name=item["product"],
                predicted_profitable=bool(item["predicted"]),
                created_at=datetime.utcnow()
            ))
        db.session.commit()

        return jsonify({
            "message": "Класифікація завершена",
            "results": result_table,
            "metrics": metrics
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
