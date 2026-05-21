from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    predictions = db.relationship("Prediction", backref="user", lazy=True)
    special_bet = db.relationship("SpecialBet", backref="user", uselist=False, lazy=True)

    @property
    def total_points(self):
        pts = sum(p.points_earned for p in self.predictions if p.points_earned is not None)
        if self.special_bet:
            sb = self.special_bet
            if sb.champion_points is not None:
                pts += sb.champion_points
            if sb.semi_points is not None:
                pts += sb.semi_points
            for gqb in sb.group_qualifier_bets:
                if gqb.points is not None:
                    pts += gqb.points
        return pts

    @property
    def special_total(self):
        if not self.special_bet:
            return 0
        sb = self.special_bet
        pts = 0
        if sb.champion_points is not None:
            pts += sb.champion_points
        if sb.semi_points is not None:
            pts += sb.semi_points
        for gqb in sb.group_qualifier_bets:
            if gqb.points is not None:
                pts += gqb.points
        return pts


class Match(db.Model):
    __tablename__ = "matches"
    id = db.Column(db.Integer, primary_key=True)
    team1 = db.Column(db.String(50), nullable=False)
    team2 = db.Column(db.String(50), nullable=False)
    stage = db.Column(db.String(30), nullable=False)
    match_datetime = db.Column(db.DateTime, nullable=False)
    score1_real = db.Column(db.Integer, nullable=True)
    score2_real = db.Column(db.Integer, nullable=True)
    is_finished = db.Column(db.Boolean, default=False)
    predictions = db.relationship("Prediction", backref="match", lazy=True)

    @property
    def is_open(self):
        return datetime.utcnow() < self.match_datetime and not self.is_finished

    @property
    def result_label(self):
        if self.score1_real is None:
            return None
        if self.score1_real > self.score2_real:
            return self.team1
        if self.score2_real > self.score1_real:
            return self.team2
        return "Empate"


class Prediction(db.Model):
    __tablename__ = "predictions"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    match_id = db.Column(db.Integer, db.ForeignKey("matches.id"), nullable=False)
    predicted_score1 = db.Column(db.Integer, nullable=False)
    predicted_score2 = db.Column(db.Integer, nullable=False)
    points_earned = db.Column(db.Integer, nullable=True)

    __table_args__ = (db.UniqueConstraint("user_id", "match_id"),)

    @property
    def predicted_winner(self):
        if self.predicted_score1 > self.predicted_score2:
            return self.match.team1
        if self.predicted_score2 > self.predicted_score1:
            return self.match.team2
        return "Empate"


class SpecialBet(db.Model):
    __tablename__ = "special_bets"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), unique=True, nullable=False)
    champion = db.Column(db.String(50), nullable=True)
    semi1 = db.Column(db.String(50), nullable=True)
    semi2 = db.Column(db.String(50), nullable=True)
    semi3 = db.Column(db.String(50), nullable=True)
    semi4 = db.Column(db.String(50), nullable=True)
    champion_points = db.Column(db.Integer, nullable=True)
    semi_points = db.Column(db.Integer, nullable=True)
    group_qualifier_bets = db.relationship("GroupQualifierBet", backref="special_bet",
                                           lazy=True, cascade="all, delete-orphan")

    @property
    def semis_list(self):
        return [t for t in [self.semi1, self.semi2, self.semi3, self.semi4] if t]


class SpecialResult(db.Model):
    __tablename__ = "special_results"
    id = db.Column(db.Integer, primary_key=True, default=1)
    champion = db.Column(db.String(50), nullable=True)
    semi1 = db.Column(db.String(50), nullable=True)
    semi2 = db.Column(db.String(50), nullable=True)
    semi3 = db.Column(db.String(50), nullable=True)
    semi4 = db.Column(db.String(50), nullable=True)

    @property
    def semis_set(self):
        return {t for t in [self.semi1, self.semi2, self.semi3, self.semi4] if t}


class GroupQualifierBet(db.Model):
    """Equipos que el usuario predice que clasifican de cada grupo (2 obligatorios + 1 tercero opcional)."""
    __tablename__ = "group_qualifier_bets"
    id = db.Column(db.Integer, primary_key=True)
    special_bet_id = db.Column(db.Integer, db.ForeignKey("special_bets.id"), nullable=False)
    group_name = db.Column(db.String(15), nullable=False)
    team1 = db.Column(db.String(50), nullable=True)
    team2 = db.Column(db.String(50), nullable=True)
    team3 = db.Column(db.String(50), nullable=True)  # tercero opcional
    points = db.Column(db.Integer, nullable=True)  # 0-3

    __table_args__ = (db.UniqueConstraint("special_bet_id", "group_name"),)

    @property
    def teams_set(self):
        return {t for t in [self.team1, self.team2, self.team3] if t}

    @property
    def teams_list(self):
        return [t for t in [self.team1, self.team2, self.team3] if t]


class GroupQualifierResult(db.Model):
    """Los equipos reales que clasificaron de cada grupo (2 directos + 1 tercero si aplica)."""
    __tablename__ = "group_qualifier_results"
    id = db.Column(db.Integer, primary_key=True)
    group_name = db.Column(db.String(15), unique=True, nullable=False)
    team1 = db.Column(db.String(50), nullable=True)
    team2 = db.Column(db.String(50), nullable=True)
    team3 = db.Column(db.String(50), nullable=True)  # tercero clasificado (si aplica)

    @property
    def teams_set(self):
        return {t for t in [self.team1, self.team2, self.team3] if t}
