from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class WiFiNetwork(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ssid = db.Column(db.String(100), nullable=False)
    brand = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100), nullable=False)
    interval = db.Column(db.String(50), nullable=False)
    security = db.Column(db.String(50),nullable=False)
    registered_at = db.Column(db.DateTime, default=datetime.utcnow)