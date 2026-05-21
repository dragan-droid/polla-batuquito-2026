"""
Partidos eliminatorios Mundial 2026.
Final confirmada: 19 de julio de 2026.
Fechas del resto derivadas del calendario oficial.
"""
from datetime import datetime
from app import app
from models import db, Match

ELIMINATORIOS = [
    # ── Dieciseisavos — 16 partidos (Jun 28 - Jul 5) ──────────────────────────
    ("TBD", "TBD", "2026-06-28 19:00", "Dieciseisavos"),
    ("TBD", "TBD", "2026-06-28 22:00", "Dieciseisavos"),
    ("TBD", "TBD", "2026-06-29 19:00", "Dieciseisavos"),
    ("TBD", "TBD", "2026-06-29 22:00", "Dieciseisavos"),
    ("TBD", "TBD", "2026-06-30 19:00", "Dieciseisavos"),
    ("TBD", "TBD", "2026-06-30 22:00", "Dieciseisavos"),
    ("TBD", "TBD", "2026-07-01 19:00", "Dieciseisavos"),
    ("TBD", "TBD", "2026-07-01 22:00", "Dieciseisavos"),
    ("TBD", "TBD", "2026-07-02 19:00", "Dieciseisavos"),
    ("TBD", "TBD", "2026-07-02 22:00", "Dieciseisavos"),
    ("TBD", "TBD", "2026-07-03 19:00", "Dieciseisavos"),
    ("TBD", "TBD", "2026-07-03 22:00", "Dieciseisavos"),
    ("TBD", "TBD", "2026-07-04 19:00", "Dieciseisavos"),
    ("TBD", "TBD", "2026-07-04 22:00", "Dieciseisavos"),
    ("TBD", "TBD", "2026-07-05 19:00", "Dieciseisavos"),
    ("TBD", "TBD", "2026-07-05 22:00", "Dieciseisavos"),

    # ── Octavos — 8 partidos (Jul 6-9) ────────────────────────────────────────
    ("TBD", "TBD", "2026-07-06 19:00", "Octavos"),
    ("TBD", "TBD", "2026-07-06 22:00", "Octavos"),
    ("TBD", "TBD", "2026-07-07 19:00", "Octavos"),
    ("TBD", "TBD", "2026-07-07 22:00", "Octavos"),
    ("TBD", "TBD", "2026-07-08 19:00", "Octavos"),
    ("TBD", "TBD", "2026-07-08 22:00", "Octavos"),
    ("TBD", "TBD", "2026-07-09 19:00", "Octavos"),
    ("TBD", "TBD", "2026-07-09 22:00", "Octavos"),

    # ── Cuartos de final — 4 partidos (Jul 11-12) ─────────────────────────────
    ("TBD", "TBD", "2026-07-11 19:00", "Cuartos de final"),
    ("TBD", "TBD", "2026-07-11 22:00", "Cuartos de final"),
    ("TBD", "TBD", "2026-07-12 19:00", "Cuartos de final"),
    ("TBD", "TBD", "2026-07-12 22:00", "Cuartos de final"),

    # ── Semifinales — 2 partidos (Jul 15-16) ──────────────────────────────────
    ("TBD", "TBD", "2026-07-15 22:00", "Semifinales"),
    ("TBD", "TBD", "2026-07-16 22:00", "Semifinales"),

    # ── Tercer puesto (Jul 18) ─────────────────────────────────────────────────
    ("TBD", "TBD", "2026-07-18 19:00", "Tercer puesto"),

    # ── Final (Jul 19) — MetLife Stadium, Nueva Jersey ────────────────────────
    ("TBD", "TBD", "2026-07-19 22:00", "Final"),
]


def add_knockout():
    with app.app_context():
        existing = {m.stage for m in Match.query.all()}
        knockout = {"Dieciseisavos", "Octavos", "Cuartos de final", "Semifinales", "Tercer puesto", "Final"}
        if existing & knockout:
            print("Los partidos eliminatorios ya existen. Script cancelado.")
            return
        total = 0
        for team1, team2, dt_str, stage in ELIMINATORIOS:
            dt = datetime.strptime(dt_str, "%Y-%m-%d %H:%M")
            db.session.add(Match(team1=team1, team2=team2, stage=stage, match_datetime=dt))
            total += 1
        db.session.commit()
        print(f"✅ {total} partidos eliminatorios cargados.")


if __name__ == "__main__":
    add_knockout()
