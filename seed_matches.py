"""
Carga los partidos del Polla batuquito 2026 (fase de grupos) en la base de datos.
Ejecutar UNA SOLA VEZ: python seed_matches.py

IMPORTANTE: Los horarios están en UTC. Argentina = UTC-3.
Ejemplo: 22:00 UTC = 19:00 Argentina.

Los datos de grupos son aproximados basados en el sorteo de diciembre 2024.
Verificar el calendario oficial en: https://www.fifa.com/en/tournaments/mens/worldcup/canada-mexico-usa-2026
El admin puede editar cualquier partido desde /admin.
"""
from datetime import datetime
from app import app
from models import db, Match


GRUPOS = {
    "Grupo A": [
        ("🇺🇸 USA",        "🇺🇾 Uruguay",     "2026-06-11 22:00"),
        ("🇸🇳 Senegal",    "🇰🇷 Corea del Sur","2026-06-12 19:00"),
        ("🇺🇸 USA",        "🇸🇳 Senegal",     "2026-06-17 22:00"),
        ("🇺🇾 Uruguay",    "🇰🇷 Corea del Sur","2026-06-17 19:00"),
        ("🇺🇸 USA",        "🇰🇷 Corea del Sur","2026-06-22 22:00"),
        ("🇺🇾 Uruguay",    "🇸🇳 Senegal",     "2026-06-22 22:00"),
    ],
    "Grupo B": [
        ("🇲🇽 México",     "🇪🇨 Ecuador",     "2026-06-12 01:00"),
        ("🇿🇦 Sudáfrica",  "🇭🇷 Croacia",     "2026-06-12 22:00"),
        ("🇲🇽 México",     "🇿🇦 Sudáfrica",   "2026-06-18 22:00"),
        ("🇪🇨 Ecuador",    "🇭🇷 Croacia",     "2026-06-18 19:00"),
        ("🇲🇽 México",     "🇭🇷 Croacia",     "2026-06-23 22:00"),
        ("🇪🇨 Ecuador",    "🇿🇦 Sudáfrica",   "2026-06-23 22:00"),
    ],
    "Grupo C": [
        ("🇨🇦 Canadá",     "🇨🇴 Colombia",    "2026-06-13 22:00"),
        ("🇨🇮 Costa de Marfil","🇯🇵 Japón",   "2026-06-13 19:00"),
        ("🇨🇦 Canadá",     "🇨🇮 Costa de Marfil","2026-06-19 22:00"),
        ("🇨🇴 Colombia",   "🇯🇵 Japón",       "2026-06-19 19:00"),
        ("🇨🇦 Canadá",     "🇯🇵 Japón",       "2026-06-24 22:00"),
        ("🇨🇴 Colombia",   "🇨🇮 Costa de Marfil","2026-06-24 22:00"),
    ],
    "Grupo D": [
        ("🇦🇷 Argentina",  "🇵🇦 Panamá",      "2026-06-14 01:00"),
        ("🇩🇿 Argelia",    "🇹🇷 Turquía",     "2026-06-14 19:00"),
        ("🇦🇷 Argentina",  "🇩🇿 Argelia",     "2026-06-20 01:00"),
        ("🇵🇦 Panamá",     "🇹🇷 Turquía",     "2026-06-19 22:00"),
        ("🇦🇷 Argentina",  "🇹🇷 Turquía",     "2026-06-25 22:00"),
        ("🇵🇦 Panamá",     "🇩🇿 Argelia",     "2026-06-25 22:00"),
    ],
    "Grupo E": [
        ("🇧🇷 Brasil",     "🇯🇲 Jamaica",     "2026-06-14 22:00"),
        ("🇯🇴 Jordania",   "🇨🇭 Suiza",       "2026-06-15 19:00"),
        ("🇧🇷 Brasil",     "🇯🇴 Jordania",    "2026-06-21 01:00"),
        ("🇯🇲 Jamaica",    "🇨🇭 Suiza",       "2026-06-20 22:00"),
        ("🇧🇷 Brasil",     "🇨🇭 Suiza",       "2026-06-26 22:00"),
        ("🇯🇲 Jamaica",    "🇯🇴 Jordania",    "2026-06-26 22:00"),
    ],
    "Grupo F": [
        ("🇫🇷 Francia",    "🇭🇳 Honduras",    "2026-06-15 22:00"),
        ("🇲🇱 Mali",       "🇦🇺 Australia",   "2026-06-15 01:00"),
        ("🇫🇷 Francia",    "🇲🇱 Mali",        "2026-06-21 22:00"),
        ("🇭🇳 Honduras",   "🇦🇺 Australia",   "2026-06-21 19:00"),
        ("🇫🇷 Francia",    "🇦🇺 Australia",   "2026-06-27 22:00"),
        ("🇭🇳 Honduras",   "🇲🇱 Mali",        "2026-06-27 22:00"),
    ],
    "Grupo G": [
        ("🏴󠁧󠁢󠁥󠁮󠁧󠁿 Inglaterra", "🇳🇬 Nigeria",   "2026-06-16 22:00"),
        ("🇸🇦 Arabia Saudita","🇩🇰 Dinamarca","2026-06-16 19:00"),
        ("🏴󠁧󠁢󠁥󠁮󠁧󠁿 Inglaterra", "🇸🇦 Arabia Saudita","2026-06-22 01:00"),
        ("🇳🇬 Nigeria",    "🇩🇰 Dinamarca",   "2026-06-21 22:00"),
        ("🏴󠁧󠁢󠁥󠁮󠁧󠁿 Inglaterra", "🇩🇰 Dinamarca", "2026-06-28 22:00"),
        ("🇳🇬 Nigeria",    "🇸🇦 Arabia Saudita","2026-06-28 22:00"),
    ],
    "Grupo H": [
        ("🇩🇪 Alemania",   "🇨🇲 Camerún",    "2026-06-17 01:00"),
        ("🇵🇾 Paraguay",   "🇷🇸 Serbia",      "2026-06-16 01:00"),
        ("🇩🇪 Alemania",   "🇵🇾 Paraguay",    "2026-06-23 01:00"),
        ("🇨🇲 Camerún",    "🇷🇸 Serbia",      "2026-06-22 19:00"),
        ("🇩🇪 Alemania",   "🇷🇸 Serbia",      "2026-06-29 22:00"),
        ("🇵🇾 Paraguay",   "🇨🇲 Camerún",    "2026-06-29 22:00"),
    ],
    "Grupo I": [
        ("🇪🇸 España",     "🇪🇬 Egipto",      "2026-06-18 01:00"),
        ("🇺🇿 Uzbekistán", "🇦🇹 Austria",     "2026-06-17 19:00"),
        ("🇪🇸 España",     "🇺🇿 Uzbekistán",  "2026-06-24 01:00"),
        ("🇪🇬 Egipto",     "🇦🇹 Austria",     "2026-06-23 19:00"),
        ("🇪🇸 España",     "🇦🇹 Austria",     "2026-06-30 22:00"),
        ("🇪🇬 Egipto",     "🇺🇿 Uzbekistán",  "2026-06-30 22:00"),
    ],
    "Grupo J": [
        ("🇵🇹 Portugal",   "🇲🇦 Marruecos",   "2026-06-18 22:00"),
        ("🇮🇷 Irán",       "🇧🇪 Bélgica",     "2026-06-18 19:00"),
        ("🇵🇹 Portugal",   "🇮🇷 Irán",        "2026-06-25 01:00"),
        ("🇲🇦 Marruecos",  "🇧🇪 Bélgica",     "2026-06-24 19:00"),
        ("🇵🇹 Portugal",   "🇧🇪 Bélgica",     "2026-07-01 22:00"),
        ("🇲🇦 Marruecos",  "🇮🇷 Irán",        "2026-07-01 22:00"),
    ],
    "Grupo K": [
        ("🇳🇱 Países Bajos","🇹🇳 Túnez",      "2026-06-19 01:00"),
        ("🇳🇿 Nueva Zelanda","🏴󠁧󠁢󠁳󠁣󠁴󠁿 Escocia", "2026-06-19 22:00"),
        ("🇳🇱 Países Bajos","🇳🇿 Nueva Zelanda","2026-06-26 01:00"),
        ("🇹🇳 Túnez",      "🏴󠁧󠁢󠁳󠁣󠁴󠁿 Escocia", "2026-06-25 19:00"),
        ("🇳🇱 Países Bajos","🏴󠁧󠁢󠁳󠁣󠁴󠁿 Escocia", "2026-07-02 22:00"),
        ("🇳🇿 Nueva Zelanda","🇹🇳 Túnez",      "2026-07-02 22:00"),
    ],
    "Grupo L": [
        ("🇮🇹 Italia",     "🇶🇦 Qatar",       "2026-06-20 22:00"),
        ("🇻🇪 Venezuela",  "🇵🇱 Polonia",     "2026-06-20 19:00"),
        ("🇮🇹 Italia",     "🇻🇪 Venezuela",   "2026-06-27 01:00"),
        ("🇶🇦 Qatar",      "🇵🇱 Polonia",     "2026-06-26 19:00"),
        ("🇮🇹 Italia",     "🇵🇱 Polonia",     "2026-07-03 22:00"),
        ("🇻🇪 Venezuela",  "🇶🇦 Qatar",       "2026-07-03 22:00"),
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
                m = Match(team1=team1, team2=team2, stage=stage, match_datetime=dt)
                db.session.add(m)
                total += 1

        db.session.commit()
        print(f"✅ {total} partidos cargados correctamente.")
        print("Nota: los horarios son en UTC. Argentina = UTC-3 (restar 3 horas).")


if __name__ == "__main__":
    seed()
