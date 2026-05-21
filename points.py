def _real_outcome(s1: int, s2: int) -> str:
    if s1 > s2:
        return "1"
    if s2 > s1:
        return "2"
    return "draw"


def calculate_points(predicted_outcome: str, real_s1: int, real_s2: int) -> int:
    """1 pt si el resultado (ganador o empate) es correcto, 0 si no."""
    return 1 if predicted_outcome == _real_outcome(real_s1, real_s2) else 0


def calculate_special_points(bet, result) -> tuple:
    """Retorna (champion_points, semi_points, top_scorer_points)."""
    champion_pts = 20 if bet.champion and bet.champion == result.champion else 0
    real_semis = result.semis_set
    semi_pts = sum(
        5 for team in [bet.semi1, bet.semi2, bet.semi3, bet.semi4]
        if team and team in real_semis
    )
    top_scorer_pts = 20 if bet.top_scorer and bet.top_scorer == result.top_scorer else 0
    return champion_pts, semi_pts, top_scorer_pts


def calculate_group_qualifier_points(bet_teams_set, real_teams_set) -> int:
    """1 punto por cada equipo clasificado acertado (máx 3 por grupo si hay tercero)."""
    return len(bet_teams_set & real_teams_set)
