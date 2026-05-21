"""
Carga los 72 partidos de la fase de grupos del Mundial 2026.
Grupos verificados con el sorteo oficial del 5 de diciembre de 2024.
Horarios en UTC. Argentina = UTC-3.
"""
from datetime import datetime
from app import app
from models import db, Match

GRUPOS = {
    # Sede principal: Estadio Azteca (Ciudad de México) — partido inaugural
    "Grupo A": [
        ("🇲🇽 México",          "🇿🇦 Sudáfrica",        "2026-06-11 21:00"),
        ("🇰🇷 Corea del Sur",   "🇨🇿 República Checa",  "2026-06-12 18:00"),
        ("🇲🇽 México",          "🇰🇷 Corea del Sur",    "2026-06-17 21:00"),
        ("🇨🇿 República Checa", "🇿🇦 Sudáfrica",        "2026-06-17 18:00"),
        ("🇲🇽 México",          "🇨🇿 República Checa",  "2026-06-22 22:00"),
        ("🇿🇦 Sudáfrica",       "🇰🇷 Corea del Sur",    "2026-06-22 22:00"),
    ],
    "Grupo B": [
        ("🇨🇦 Canadá",          "🇧🇦 Bosnia y Herz.",   "2026-06-11 18:00"),
        ("🇶🇦 Qatar",           "🇨🇭 Suiza",            "2026-06-12 21:00"),
        ("🇨🇦 Canadá",          "🇶🇦 Qatar",            "2026-06-17 18:00"),
        ("🇨🇭 Suiza",           "🇧🇦 Bosnia y Herz.",   "2026-06-18 21:00"),
        ("🇨🇦 Canadá",          "🇨🇭 Suiza",            "2026-06-23 22:00"),
        ("🇧🇦 Bosnia y Herz.",  "🇶🇦 Qatar",            "2026-06-23 22:00"),
    ],
    "Grupo C": [
        ("🇧🇷 Brasil",          "🇲🇦 Marruecos",        "2026-06-12 21:00"),
        ("🇭🇹 Haití",           "🏴󠁧󠁢󠁳󠁣󠁴󠁿 Escocia",          "2026-06-13 18:00"),
        ("🇧🇷 Brasil",          "🇭🇹 Haití",            "2026-06-18 21:00"),
        ("🏴󠁧󠁢󠁳󠁣󠁴󠁿 Escocia",         "🇲🇦 Marruecos",        "2026-06-19 18:00"),
        ("🇧🇷 Brasil",          "🏴󠁧󠁢󠁳󠁣󠁴󠁿 Escocia",          "2026-06-24 22:00"),
        ("🇲🇦 Marruecos",       "🇭🇹 Haití",            "2026-06-24 22:00"),
    ],
    "Grupo D": [
        ("🇺🇸 USA",             "🇵🇾 Paraguay",         "2026-06-12 18:00"),
        ("🇦🇺 Australia",       "🇹🇷 Turquía",          "2026-06-13 21:00"),
        ("🇺🇸 USA",             "🇦🇺 Australia",        "2026-06-18 18:00"),
        ("🇹🇷 Turquía",         "🇵🇾 Paraguay",         "2026-06-19 21:00"),
        ("🇺🇸 USA",             "🇹🇷 Turquía",          "2026-06-23 22:00"),
        ("🇵🇾 Paraguay",        "🇦🇺 Australia",        "2026-06-23 22:00"),
    ],
    "Grupo E": [
        ("🇩🇪 Alemania",        "🇨🇼 Curazao",          "2026-06-13 21:00"),
        ("🇨🇮 Costa de Marfil", "🇪🇨 Ecuador",          "2026-06-14 18:00"),
        ("🇩🇪 Alemania",        "🇨🇮 Costa de Marfil",  "2026-06-19 21:00"),
        ("🇪🇨 Ecuador",         "🇨🇼 Curazao",          "2026-06-20 18:00"),
        ("🇩🇪 Alemania",        "🇪🇨 Ecuador",          "2026-06-24 22:00"),
        ("🇨🇼 Curazao",         "🇨🇮 Costa de Marfil",  "2026-06-24 22:00"),
    ],
    "Grupo F": [
        ("🇳🇱 Países Bajos",    "🇯🇵 Japón",            "2026-06-14 21:00"),
        ("🇸🇪 Suecia",          "🇹🇳 Túnez",            "2026-06-15 18:00"),
        ("🇳🇱 Países Bajos",    "🇸🇪 Suecia",           "2026-06-20 21:00"),
        ("🇹🇳 Túnez",           "🇯🇵 Japón",            "2026-06-21 18:00"),
        ("🇳🇱 Países Bajos",    "🇹🇳 Túnez",            "2026-06-25 22:00"),
        ("🇯🇵 Japón",           "🇸🇪 Suecia",           "2026-06-25 22:00"),
    ],
    "Grupo G": [
        ("🇧🇪 Bélgica",         "🇪🇬 Egipto",           "2026-06-14 18:00"),
        ("🇮🇷 Irán",            "🇳🇿 Nueva Zelanda",    "2026-06-15 21:00"),
        ("🇧🇪 Bélgica",         "🇮🇷 Irán",             "2026-06-20 18:00"),
        ("🇳🇿 Nueva Zelanda",   "🇪🇬 Egipto",           "2026-06-21 21:00"),
        ("🇧🇪 Bélgica",         "🇳🇿 Nueva Zelanda",    "2026-06-25 22:00"),
        ("🇪🇬 Egipto",          "🇮🇷 Irán",             "2026-06-25 22:00"),
    ],
    "Grupo H": [
        ("🇪🇸 España",          "🇨🇻 Cabo Verde",       "2026-06-15 21:00"),
        ("🇸🇦 Arabia Saudita",  "🇺🇾 Uruguay",          "2026-06-16 18:00"),
        ("🇪🇸 España",          "🇸🇦 Arabia Saudita",   "2026-06-21 21:00"),
        ("🇺🇾 Uruguay",         "🇨🇻 Cabo Verde",       "2026-06-22 18:00"),
        ("🇪🇸 España",          "🇺🇾 Uruguay",          "2026-06-26 22:00"),
        ("🇨🇻 Cabo Verde",      "🇸🇦 Arabia Saudita",   "2026-06-26 22:00"),
    ],
    "Grupo I": [
        ("🇫🇷 Francia",         "🇸🇳 Senegal",          "2026-06-15 18:00"),
        ("🇮🇶 Iraq",            "🇳🇴 Noruega",          "2026-06-16 21:00"),
        ("🇫🇷 Francia",         "🇮🇶 Iraq",             "2026-06-21 18:00"),
        ("🇳🇴 Noruega",         "🇸🇳 Senegal",          "2026-06-22 21:00"),
        ("🇫🇷 Francia",         "🇳🇴 Noruega",          "2026-06-26 22:00"),
        ("🇸🇳 Senegal",         "🇮🇶 Iraq",             "2026-06-26 22:00"),
    ],
    "Grupo J": [
        ("🇦🇷 Argentina",       "🇩🇿 Argelia",          "2026-06-16 21:00"),
        ("🇦🇹 Austria",         "🇯🇴 Jordania",         "2026-06-17 18:00"),
        ("🇦🇷 Argentina",       "🇦🇹 Austria",          "2026-06-22 21:00"),
        ("🇯🇴 Jordania",        "🇩🇿 Argelia",          "2026-06-23 18:00"),
        ("🇦🇷 Argentina",       "🇯🇴 Jordania",         "2026-06-27 22:00"),
        ("🇩🇿 Argelia",         "🇦🇹 Austria",          "2026-06-27 22:00"),
    ],
    "Grupo K": [
        ("🇵🇹 Portugal",        "🇨🇩 DR Congo",         "2026-06-16 18:00"),
        ("🇺🇿 Uzbekistán",      "🇨🇴 Colombia",         "2026-06-17 21:00"),
        ("🇵🇹 Portugal",        "🇺🇿 Uzbekistán",       "2026-06-22 18:00"),
        ("🇨🇴 Colombia",        "🇨🇩 DR Congo",         "2026-06-23 21:00"),
        ("🇵🇹 Portugal",        "🇨🇴 Colombia",         "2026-06-27 22:00"),
        ("🇨🇩 DR Congo",        "🇺🇿 Uzbekistán",       "2026-06-27 22:00"),
    ],
    "Grupo L": [
        ("🏴󠁧󠁢󠁥󠁮󠁧󠁿 Inglaterra",       "🇭🇷 Croacia",          "2026-06-17 21:00"),
        ("🇬🇭 Ghana",           "🇵🇦 Panamá",           "2026-06-18 18:00"),
        ("🏴󠁧󠁢󠁥󠁮󠁧󠁿 Inglaterra",       "🇬🇭 Ghana",            "2026-06-23 21:00"),
        ("🇵🇦 Panamá",          "🇭🇷 Croacia",          "2026-06-24 18:00"),
        ("🏴󠁧󠁢󠁥󠁮󠁧󠁿 Inglaterra",       "🇵🇦 Panamá",           "2026-06-28 22:00"),
        ("🇭🇷 Croacia",         "🇬🇭 Ghana",            "2026-06-28 22:00"),
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
