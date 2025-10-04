from models import db, WiFiNetwork
from app import app

with app.app_context():
    networks = WiFiNetwork.query.all()
    for network in networks:
        print(f"SSID: {network.ssid}, Brand: {network.brand}, Interval: {network.interval}")