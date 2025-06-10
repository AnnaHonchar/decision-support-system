from app import create_app
from app.db import db
from app.models import User, Dataset, Prediction, Recommendation, Log  # важливо!

app = create_app()

if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # Ініціалізація БД
    app.run(debug=True)