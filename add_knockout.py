"""
Partidos eliminatorios Mundial 2026.
Final confirmada: 19 de julio de 2026.
Fechas del resto derivadas del calendario oficial.
"""
from datetime import datetime
from app import app
from models import db, Match

ELIMINATORIOS = [
    # ── Dieciseisavos — 16 partidos (Jun 28 - Jul 2) ──────────────────────────
    ("1° Grupo A",       "2° Grupo C",       "2026-06-28 19:00", "Dieciseisavos"),
    ("1° Grupo C",       "2° Grupo A",       "2026-06-28 22:00", "Dieciseisavos"),
    ("1° Grupo B",       "2° Grupo D",       "2026-06-29 19:00", "Dieciseisavos"),
    ("1° Grupo D",       "2° Grupo B",       "2026-06-29 22:00", "Dieciseisavos"),
    ("1° Grupo E",       "2° Grupo G",       "2026-06-30 19:00", "Dieciseisavos"),
    ("1° Grupo G",       "2° Grupo E",       "2026-06-30 22:00", "Dieciseisavos"),
    ("1° Grupo F",       "2° Grupo H",       "2026-07-01 19:00", "Dieciseisavos"),
    ("1° Grupo H",       "2° Grupo F",       "2026-07-01 22:00", "Dieciseisavos"),
    ("1° Grupo I",       "2° Grupo K",       "2026-07-02 19:00", "Dieciseisavos"),
    ("1° Grupo K",       "2° Grupo I",       "2026-07-02 22:00", "Dieciseisavos"),
    ("1° Grupo J",       "2° Grupo L",       "2026-07-03 19:00", "Dieciseisavos"),
    ("1° Grupo L",       "2° Grupo J",       "2026-07-03 22:00", "Dieciseisavos"),
    ("Mejor 3° (1)",     "Mejor 3° (2)",     "2026-07-04 19:00", "Dieciseisavos"),
    ("Mejor 3° (3)",     "Mejor 3° (4)",     "2026-07-04 22:00", "Dieciseisavos"),
    ("Mejor 3° (5)",     "Mejor 3° (6)",     "2026-07-05 19:00", "Dieciseisavos"),
    ("Mejor 3° (7)",     "Mejor 3° (8)",     "2026-07-05 22:00", "Dieciseisavos"),

    # ── Octavos — 8 partidos (Jul 6-9) ────────────────────────────────────────
    ("Gan. R32 (1)",     "Gan. R32 (2)",     "2026-07-06 22:00", "Octavos"),
    ("Gan. R32 (3)",     "Gan. R32 (4)",     "2026-07-07 22:00", "Octavos"),
    ("Gan. R32 (5)",     "Gan. R32 (6)",     "2026-07-08 22:00", "Octavos"),
    ("Gan. R32 (7)",     "Gan. R32 (8)",     "2026-07-08 19:00", "Octavos"),
    ("Gan. R32 (9)",     "Gan. R32 (10)",    "2026-07-09 22:00", "Octavos"),
    ("Gan. R32 (11)",    "Gan. R32 (12)",    "2026-07-09 19:00", "Octavos"),
    ("Gan. R32 (13)",    "Gan. R32 (14)",    "2026-07-06 19:00", "Octavos"),
    ("Gan. R32 (15)",    "Gan. R32 (16)",    "2026-07-07 19:00", "Octavos"),

    # ── Cuartos de final — 4 partidos (Jul 11-12) ─────────────────────────────
    ("Gan. Octavos (1)", "Gan. Octavos (2)", "2026-07-11 22:00", "Cuartos de final"),
    ("Gan. Octavos (3)", "Gan. Octavos (4)", "2026-07-11 19:00", "Cuartos de final"),
    ("Gan. Octavos (5)", "Gan. Octavos (6)", "2026-07-12 22:00", "Cuartos de final"),
    ("Gan. Octavos (7)", "Gan. Octavos (8)", "2026-07-12 19:00", "Cuartos de final"),

    # ── Semifinales — 2 partidos (Jul 15-16) ──────────────────────────────────
    ("Gan. Cuartos (1)", "Gan. Cuartos (2)", "2026-07-15 22:00", "Semifinales"),
    ("Gan. Cuartos (3)", "Gan. Cuartos (4)", "2026-07-16 22:00", "Semifinales"),

    # ── Tercer puesto (Jul 18) ─────────────────────────────────────────────────
    ("Perdedor Semi (1)", "Perdedor Semi (2)", "2026-07-18 19:00", "Tercer puesto"),

    # ── Final (Jul 19) — MetLife Stadium, Nueva Jersey ────────────────────────
    ("Finalista (1)",    "Finalista (2)",    "2026-07-19 22:00", "Final"),
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
