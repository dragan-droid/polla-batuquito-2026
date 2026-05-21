def _winner(s1: int, s2: int) -> str:
    if s1 > s2:
        return "1"
    if s2 > s1:
        return "2"
    return "draw"


def calculate_points(pred_s1: int, pred_s2: int, real_s1: int, real_s2: int) -> int:
    # Marcador exacto: 3 pts (1 resultado + 2 bonus)
    if pred_s1 == real_s1 and pred_s2 == real_s2:
        return 3

    correct_outcome = _winner(pred_s1, pred_s2) == _winner(real_s1, real_s2)
    one_number = (pred_s1 == real_s1) or (pred_s2 == real_s2)

    # Resultado correcto O un número acertado: 1 pt
    if correct_outcome or one_number:
        return 1

    return 0


def calculate_special_points(bet, result) -> tuple:
    """Retorna (champion_points, semi_points)."""
    champion_pts = 20 if bet.champion and bet.champion == result.champion else 0
    real_semis = result.semis_set
    semi_pts = sum(
        5 for team in [bet.semi1, bet.semi2, bet.semi3, bet.semi4]
        if team and team in real_semis
    )
    return champion_pts, semi_pts


def calculate_group_qualifier_points(bet_teams_set, real_teams_set) -> int:
    """1 punto por cada equipo clasificado acertado (máx 3 por grupo si hay tercero)."""
    return len(bet_teams_set & real_teams_set)
