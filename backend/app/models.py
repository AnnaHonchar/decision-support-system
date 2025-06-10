from .db import db
from datetime import datetime

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), nullable=False, unique=True)
    email = db.Column(db.String(255), nullable=False, unique=True)
    password = db.Column(db.String(2048), nullable=False)

    def __repr__(self):
        return f"<User {self.username}>"
    
class Dataset(db.Model):
    __tablename__ = 'datasets'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    upload_date = db.Column(db.DateTime, nullable=False)

    user = db.relationship('User', backref=db.backref('datasets', lazy=True))


class Prediction(db.Model):
    __tablename__ = 'predictions'

    id = db.Column(db.Integer, primary_key=True)
    dataset_id = db.Column(db.Integer, db.ForeignKey('datasets.id'), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)
    result_summary = db.Column(db.Text)

    dataset = db.relationship('Dataset', backref=db.backref('predictions', lazy=True))


class Recommendation(db.Model):
    __tablename__ = 'recommendations'

    id = db.Column(db.Integer, primary_key=True)
    prediction_id = db.Column(db.Integer, db.ForeignKey('predictions.id'), nullable=False)
    text = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)

    prediction = db.relationship('Prediction', backref=db.backref('recommendations', lazy=True))


class Log(db.Model):
    __tablename__ = 'logs'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    action = db.Column(db.String(255), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False)

    user = db.relationship('User', backref=db.backref('logs', lazy=True))

class SalesPrediction(db.Model):
    __tablename__ = 'sales_predictions'

    id = db.Column(db.Integer, primary_key=True)
    dataset_id = db.Column(db.Integer, db.ForeignKey('datasets.id'), nullable=False)
    predicted_date = db.Column(db.Date, nullable=False)
    predicted_sales = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class SalesRecommendation(db.Model):
    __tablename__ = 'sales_recommendation'

    id = db.Column(db.Integer, primary_key=True)
    dataset_id = db.Column(db.Integer, db.ForeignKey('datasets.id'), nullable=False)
    category = db.Column(db.String(100), nullable=False)
    recommendation = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    dataset = db.relationship('Dataset', backref=db.backref('sales_recommendations', lazy=True))

class TopsisResult(db.Model):
    __tablename__ = 'topsis_result'

    id = db.Column(db.Integer, primary_key=True)
    dataset_id = db.Column(db.Integer, db.ForeignKey('datasets.id'), nullable=False)
    result_text = db.Column(db.Text, nullable=False)
    dataset = db.relationship("Dataset", backref=db.backref("topsis_result", uselist=False))

class ClassificationResult(db.Model):
    __tablename__ = 'classification_result'

    id = db.Column(db.Integer, primary_key=True)
    dataset_id = db.Column(db.Integer, db.ForeignKey("datasets.id"), nullable=False)
    product_name = db.Column(db.String(120))
    predicted_profitable = db.Column(db.Boolean)  # True / False
    created_at = db.Column(db.DateTime)