"""
Crea tablas y carga los 104 partidos si la DB está vacía.
Si RESET_DB=true, ELIMINA todas las tablas y las recrea desde cero.
"""
import os
from datetime import datetime
from app import app
from models import db, Match
from seed_matches import GRUPOS
from add_knockout import ELIMINATORIOS

RESET = os.environ.get("RESET_DB", "false").lower() == "true"

with app.app_context():

    if RESET:
        print("⚠️  RESET_DB=true — eliminando y recreando todas las tablas...")
        db.drop_all()
        print("✅ Tablas eliminadas.")

    db.create_all()
    print("✅ Tablas creadas/verificadas.")

    count = Match.query.count()
    print(f"Partidos en DB: {count}")

    if count == 0:
        print("Cargando grupos...")
        total = 0
        for stage, matches in GRUPOS.items():
            for team1, team2, dt_str in matches:
                dt = datetime.strptime(dt_str, "%Y-%m-%d %H:%M")
                db.session.add(Match(team1=team1, team2=team2, stage=stage, match_datetime=dt))
                total += 1
        db.session.commit()
        print(f"✅ {total} partidos de grupos cargados.")

        print("Cargando eliminatorios...")
        total2 = 0
        for team1, team2, dt_str, stage in ELIMINATORIOS:
            dt = datetime.strptime(dt_str, "%Y-%m-%d %H:%M")
            db.session.add(Match(team1=team1, team2=team2, stage=stage, match_datetime=dt))
            total2 += 1
        db.session.commit()
        print(f"✅ {total2} partidos eliminatorios cargados.")
        print(f"✅ Total: {total + total2} partidos.")
    else:
        print(f"ℹ️  DB ya tiene {count} partidos, no se recarga.")
