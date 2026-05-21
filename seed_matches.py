"""
Partidos fase de grupos Mundial 2026.
Grupos: sorteo oficial 5 dic 2024.
Horarios en UTC (Argentina = UTC-3, restar 3 horas).
Horarios con (*) son confirmados por FIFA/ESPN. El resto son aproximados
y se actualizarán cuando FIFA publique el calendario completo.
"""
from datetime import datetime
from app import app
from models import db, Match

GRUPOS = {
    "Grupo A": [
        # (*) Mexico vs Sudáfrica: 1 PM CST = 19:00 UTC confirmado
        ("🇲🇽 México",          "🇿🇦 Sudáfrica",        "2026-06-11 19:00"),
        ("🇰🇷 Corea del Sur",   "🇨🇿 República Checa",  "2026-06-12 22:00"),
        ("🇲🇽 México",          "🇰🇷 Corea del Sur",    "2026-06-17 22:00"),
        ("🇨🇿 República Checa", "🇿🇦 Sudáfrica",        "2026-06-17 19:00"),
        ("🇲🇽 México",          "🇨🇿 República Checa",  "2026-06-22 22:00"),
        ("🇿🇦 Sudáfrica",       "🇰🇷 Corea del Sur",    "2026-06-22 22:00"),
    ],
    "Grupo B": [
        ("🇨🇦 Canadá",          "🇧🇦 Bosnia y Herz.",   "2026-06-12 19:00"),
        ("🇶🇦 Qatar",           "🇨🇭 Suiza",            "2026-06-12 22:00"),
        ("🇨🇦 Canadá",          "🇶🇦 Qatar",            "2026-06-17 19:00"),
        ("🇨🇭 Suiza",           "🇧🇦 Bosnia y Herz.",   "2026-06-18 22:00"),
        ("🇨🇦 Canadá",          "🇨🇭 Suiza",            "2026-06-23 22:00"),
        ("🇧🇦 Bosnia y Herz.",  "🇶🇦 Qatar",            "2026-06-23 22:00"),
    ],
    "Grupo C": [
        # (*) Brasil vs Marruecos: 6 PM ET Jun 13 = 22:00 UTC confirmado
        ("🇧🇷 Brasil",          "🇲🇦 Marruecos",        "2026-06-13 22:00"),
        ("🇭🇹 Haití",           "🏴󠁧󠁢󠁳󠁣󠁴󠁿 Escocia",          "2026-06-13 19:00"),
        ("🇧🇷 Brasil",          "🇭🇹 Haití",            "2026-06-19 22:00"),
        ("🏴󠁧󠁢󠁳󠁣󠁴󠁿 Escocia",         "🇲🇦 Marruecos",        "2026-06-19 19:00"),
        ("🇧🇷 Brasil",          "🏴󠁧󠁢󠁳󠁣󠁴󠁿 Escocia",          "2026-06-24 22:00"),
        ("🇲🇦 Marruecos",       "🇭🇹 Haití",            "2026-06-24 22:00"),
    ],
    "Grupo D": [
        # (*) USA vs Paraguay: 9 PM ET Jun 12 = 01:00 UTC Jun 13 confirmado
        ("🇺🇸 USA",             "🇵🇾 Paraguay",         "2026-06-13 01:00"),
        ("🇦🇺 Australia",       "🇹🇷 Turquía",          "2026-06-13 19:00"),
        ("🇺🇸 USA",             "🇦🇺 Australia",        "2026-06-18 19:00"),
        ("🇹🇷 Turquía",         "🇵🇾 Paraguay",         "2026-06-19 22:00"),
        ("🇺🇸 USA",             "🇹🇷 Turquía",          "2026-06-23 22:00"),
        ("🇵🇾 Paraguay",        "🇦🇺 Australia",        "2026-06-23 22:00"),
    ],
    "Grupo E": [
        ("🇩🇪 Alemania",        "🇨🇼 Curazao",          "2026-06-14 19:00"),
        ("🇨🇮 Costa de Marfil", "🇪🇨 Ecuador",          "2026-06-14 22:00"),
        ("🇩🇪 Alemania",        "🇨🇮 Costa de Marfil",  "2026-06-20 22:00"),
        ("🇪🇨 Ecuador",         "🇨🇼 Curazao",          "2026-06-20 19:00"),
        ("🇩🇪 Alemania",        "🇪🇨 Ecuador",          "2026-06-25 22:00"),
        ("🇨🇼 Curazao",         "🇨🇮 Costa de Marfil",  "2026-06-25 22:00"),
    ],
    "Grupo F": [
        ("🇳🇱 Países Bajos",    "🇯🇵 Japón",            "2026-06-14 22:00"),
        ("🇸🇪 Suecia",          "🇹🇳 Túnez",            "2026-06-15 19:00"),
        ("🇳🇱 Países Bajos",    "🇸🇪 Suecia",           "2026-06-20 19:00"),
        ("🇹🇳 Túnez",           "🇯🇵 Japón",            "2026-06-21 22:00"),
        ("🇳🇱 Países Bajos",    "🇹🇳 Túnez",            "2026-06-26 22:00"),
        ("🇯🇵 Japón",           "🇸🇪 Suecia",           "2026-06-26 22:00"),
    ],
    "Grupo G": [
        ("🇧🇪 Bélgica",         "🇪🇬 Egipto",           "2026-06-15 22:00"),
        ("🇮🇷 Irán",            "🇳🇿 Nueva Zelanda",    "2026-06-15 19:00"),
        ("🇧🇪 Bélgica",         "🇮🇷 Irán",             "2026-06-21 19:00"),
        ("🇳🇿 Nueva Zelanda",   "🇪🇬 Egipto",           "2026-06-21 22:00"),
        ("🇧🇪 Bélgica",         "🇳🇿 Nueva Zelanda",    "2026-06-26 22:00"),
        ("🇪🇬 Egipto",          "🇮🇷 Irán",             "2026-06-26 22:00"),
    ],
    "Grupo H": [
        ("🇪🇸 España",          "🇨🇻 Cabo Verde",       "2026-06-16 19:00"),
        ("🇸🇦 Arabia Saudita",  "🇺🇾 Uruguay",          "2026-06-16 22:00"),
        ("🇪🇸 España",          "🇸🇦 Arabia Saudita",   "2026-06-22 19:00"),
        ("🇺🇾 Uruguay",         "🇨🇻 Cabo Verde",       "2026-06-22 22:00"),
        ("🇪🇸 España",          "🇺🇾 Uruguay",          "2026-06-27 22:00"),
        ("🇨🇻 Cabo Verde",      "🇸🇦 Arabia Saudita",   "2026-06-27 22:00"),
    ],
    "Grupo I": [
        ("🇫🇷 Francia",         "🇸🇳 Senegal",          "2026-06-16 22:00"),
        ("🇮🇶 Iraq",            "🇳🇴 Noruega",          "2026-06-17 19:00"),
        ("🇫🇷 Francia",         "🇮🇶 Iraq",             "2026-06-22 22:00"),
        ("🇳🇴 Noruega",         "🇸🇳 Senegal",          "2026-06-22 19:00"),
        ("🇫🇷 Francia",         "🇳🇴 Noruega",          "2026-06-27 22:00"),
        ("🇸🇳 Senegal",         "🇮🇶 Iraq",             "2026-06-27 22:00"),
    ],
    "Grupo J": [
        # (*) Argentina vs Argelia: 9 PM ET Jun 16 = 01:00 UTC Jun 17 confirmado
        ("🇦🇷 Argentina",       "🇩🇿 Argelia",          "2026-06-17 01:00"),
        ("🇦🇹 Austria",         "🇯🇴 Jordania",         "2026-06-17 22:00"),
        ("🇦🇷 Argentina",       "🇦🇹 Austria",          "2026-06-22 01:00"),
        ("🇯🇴 Jordania",        "🇩🇿 Argelia",          "2026-06-23 19:00"),
        ("🇦🇷 Argentina",       "🇯🇴 Jordania",         "2026-06-27 22:00"),
        ("🇩🇿 Argelia",         "🇦🇹 Austria",          "2026-06-27 22:00"),
    ],
    "Grupo K": [
        ("🇵🇹 Portugal",        "🇨🇩 DR Congo",         "2026-06-17 22:00"),
        ("🇺🇿 Uzbekistán",      "🇨🇴 Colombia",         "2026-06-18 19:00"),
        ("🇵🇹 Portugal",        "🇺🇿 Uzbekistán",       "2026-06-23 22:00"),
        ("🇨🇴 Colombia",        "🇨🇩 DR Congo",         "2026-06-24 19:00"),
        ("🇵🇹 Portugal",        "🇨🇴 Colombia",         "2026-06-28 22:00"),
        ("🇨🇩 DR Congo",        "🇺🇿 Uzbekistán",       "2026-06-28 22:00"),
    ],
    "Grupo L": [
        ("🏴󠁧󠁢󠁥󠁮󠁧󠁿 Inglaterra",       "🇭🇷 Croacia",          "2026-06-18 22:00"),
        ("🇬🇭 Ghana",           "🇵🇦 Panamá",           "2026-06-18 19:00"),
        ("🏴󠁧󠁢󠁥󠁮󠁧󠁿 Inglaterra",       "🇬🇭 Ghana",            "2026-06-24 22:00"),
        ("🇵🇦 Panamá",          "🇭🇷 Croacia",          "2026-06-24 19:00"),
        ("🏴󠁧󠁢󠁥󠁮󠁧󠁿 Inglaterra",       "🇵🇦 Panamá",           "2026-06-29 22:00"),
        ("🇭🇷 Croacia",         "🇬🇭 Ghana",            "2026-06-29 22:00"),
    ],
}


def seed():
    with app.app_context():
        if Match.query.count() > 0:
            print("La base de datos ya tiene partidos. Seed cancelado.")
            return
        total = 0
        for stage, matches in GRUPOS.items():
            for team1, team2, dt_str in matches:
                dt = datetime.strptime(dt_str, "%Y-%m-%d %H:%M")
                db.session.add(Match(team1=team1, team2=team2, stage=stage, match_datetime=dt))
                total += 1
        db.session.commit()
        print(f"✅ {total} partidos de grupos cargados.")


if __name__ == "__main__":
    seed()
