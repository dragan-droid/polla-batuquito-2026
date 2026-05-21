"""Script que crea las tablas y carga los partidos si la DB está vacía."""
from app import app
from models import db, Match
from seed_matches import seed
from add_knockout import add_knockout

with app.app_context():
    db.create_all()
    if Match.query.count() == 0:
        seed()
        add_knockout()
        print("✅ Base de datos inicializada con 104 partidos.")
    else:
        print(f"ℹ️  Ya hay {Match.query.count()} partidos en la base de datos.")
