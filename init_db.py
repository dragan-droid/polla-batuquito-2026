"""
Crea tablas y carga los 104 partidos si la DB está vacía.
Si RESET_DB=true, borra todo y recarga desde cero.
"""
import os
from datetime import datetime
from app import app
from models import db, Match, Prediction, SpecialBet, SpecialResult, GroupQualifierBet, GroupQualifierResult
from seed_matches import GRUPOS
from add_knockout import ELIMINATORIOS

RESET = os.environ.get("RESET_DB", "false").lower() == "true"

with app.app_context():
    db.create_all()

    if RESET:
        print("⚠️  RESET_DB=true — borrando todos los datos...")
        GroupQualifierBet.query.delete()
        GroupQualifierResult.query.delete()
        SpecialBet.query.delete()
        SpecialResult.query.delete()
        Prediction.query.delete()
        Match.query.delete()
        db.session.commit()
        print("✅ Datos eliminados.")

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
        print(f"ℹ️  DB ya tiene {count} partidos.")
