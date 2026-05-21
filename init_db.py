"""Crea tablas y carga los 104 partidos si la DB está vacía."""
import os
from datetime import datetime
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv

load_dotenv()

# Importar app ya configurada
from app import app
from models import db, Match

with app.app_context():
    db.create_all()
    count = Match.query.count()
    print(f"Partidos en DB: {count}")

    if count == 0:
        print("Cargando partidos de fase de grupos...")
        from seed_matches import GRUPOS
        total = 0
        for stage, matches in GRUPOS.items():
            for team1, team2, dt_str in matches:
                dt = datetime.strptime(dt_str, "%Y-%m-%d %H:%M")
                db.session.add(Match(team1=team1, team2=team2, stage=stage, match_datetime=dt))
                total += 1
        db.session.commit()
        print(f"✅ {total} partidos de grupos cargados.")

        print("Cargando partidos eliminatorios...")
        from add_knockout import ELIMINATORIOS
        total2 = 0
        for team1, team2, dt_str, stage in ELIMINATORIOS:
            dt = datetime.strptime(dt_str, "%Y-%m-%d %H:%M")
            db.session.add(Match(team1=team1, team2=team2, stage=stage, match_datetime=dt))
            total2 += 1
        db.session.commit()
        print(f"✅ {total2} partidos eliminatorios cargados.")
        print(f"✅ Total: {total + total2} partidos en la base de datos.")
    else:
        print(f"ℹ️  DB ya tiene {count} partidos, no se carga nada.")
