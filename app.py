import os
from datetime import datetime
from collections import defaultdict
from flask import Flask, render_template, request, redirect, url_for, session, flash
from dotenv import load_dotenv
from models import db, User, Match, Prediction, SpecialBet, SpecialResult, GroupQualifierBet, GroupQualifierResult
from points import calculate_points, calculate_special_points, calculate_group_qualifier_points

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret")

# Railway provee DATABASE_URL con PostgreSQL; localmente usamos SQLite
_db_url = os.environ.get("DATABASE_URL", "sqlite:///mundial.db")
if _db_url.startswith("postgres://"):          # Railway usa postgres://, SQLAlchemy necesita postgresql://
    _db_url = _db_url.replace("postgres://", "postgresql://", 1)
app.config["SQLALCHEMY_DATABASE_URI"] = _db_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

with app.app_context():
    db.create_all()


def current_user():
    uid = session.get("user_id")
    if uid:
        return db.session.get(User, uid)
    return None


# ─── Rutas públicas ───────────────────────────────────────────────────────────

STAGE_ORDER = [
    "Grupo A", "Grupo B", "Grupo C", "Grupo D", "Grupo E", "Grupo F",
    "Grupo G", "Grupo H", "Grupo I", "Grupo J", "Grupo K", "Grupo L",
    "Dieciseisavos", "Octavos", "Cuartos de final", "Semifinales", "Tercer puesto", "Final",
]


@app.route("/")
def index():
    user = current_user()
    now = datetime.utcnow()

    all_matches = Match.query.order_by(Match.match_datetime, Match.id).all()

    # Group by date (Argentina = UTC-3, show local date)
    by_date = defaultdict(list)
    for m in all_matches:
        day = m.match_datetime.date()
        by_date[day].append(m)
    date_groups = sorted(by_date.items())

    # Unique stages preserving canonical order
    present_stages = {m.stage for m in all_matches}
    stages = [s for s in STAGE_ORDER if s in present_stages]

    users = User.query.all()
    users.sort(key=lambda u: u.total_points, reverse=True)

    user_predictions = {}
    if user:
        for p in Prediction.query.filter_by(user_id=user.id).all():
            user_predictions[p.match_id] = p

    total = len(all_matches)
    finished_count = sum(1 for m in all_matches if m.is_finished)
    open_count = sum(1 for m in all_matches if m.is_open)

    return render_template(
        "index.html",
        user=user,
        date_groups=date_groups,
        stages=stages,
        leaderboard=users[:5],
        user_predictions=user_predictions,
        now=now,
        total_matches=total,
        finished_count=finished_count,
        open_count=open_count,
    )


@app.route("/join", methods=["GET", "POST"])
def join():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        if not name:
            flash("El nombre no puede estar vacío.", "danger")
            return redirect(url_for("join"))
        if len(name) > 50:
            flash("El nombre es demasiado largo (máximo 50 caracteres).", "danger")
            return redirect(url_for("join"))
        existing = User.query.filter_by(name=name).first()
        if existing:
            session["user_id"] = existing.id
            flash(f"¡Bienvenido de vuelta, {name}!", "success")
        else:
            user = User(name=name)
            db.session.add(user)
            db.session.commit()
            session["user_id"] = user.id
            flash(f"¡Listo, {name}! Ya podés hacer tus predicciones.", "success")
        return redirect(url_for("index"))
    return render_template("join.html", user=current_user())


@app.route("/logout")
def logout():
    session.pop("user_id", None)
    return redirect(url_for("index"))


@app.route("/predict/<int:match_id>", methods=["GET", "POST"])
def predict(match_id):
    user = current_user()
    if not user:
        flash("Primero ingresá tu nombre para participar.", "warning")
        return redirect(url_for("join"))

    match = db.session.get(Match, match_id)
    if not match:
        flash("Partido no encontrado.", "danger")
        return redirect(url_for("index"))

    if not match.is_open:
        flash("Las predicciones para este partido ya están cerradas.", "warning")
        return redirect(url_for("index"))

    existing = Prediction.query.filter_by(user_id=user.id, match_id=match_id).first()

    if request.method == "POST":
        try:
            s1 = int(request.form["score1"])
            s2 = int(request.form["score2"])
            if s1 < 0 or s2 < 0:
                raise ValueError
        except (ValueError, KeyError):
            flash("Marcador inválido. Ingresá números mayores o iguales a 0.", "danger")
            return redirect(url_for("predict", match_id=match_id))

        if existing:
            existing.predicted_score1 = s1
            existing.predicted_score2 = s2
            existing.points_earned = None
        else:
            db.session.add(Prediction(
                user_id=user.id,
                match_id=match_id,
                predicted_score1=s1,
                predicted_score2=s2,
            ))
        db.session.commit()
        flash(f"✅ Predicción guardada: {match.team1} {s1} – {s2} {match.team2}", "success")
        return redirect(url_for("index"))

    return render_template("predict.html", user=user, match=match, existing=existing)


@app.route("/results")
def results():
    user = current_user()
    finished = (
        Match.query
        .filter_by(is_finished=True)
        .order_by(Match.match_datetime.desc())
        .all()
    )
    user_predictions = {}
    if user:
        for p in Prediction.query.filter_by(user_id=user.id).all():
            user_predictions[p.match_id] = p

    return render_template("results.html", user=user, finished=finished, user_predictions=user_predictions)


@app.route("/leaderboard")
def leaderboard():
    user = current_user()
    users = User.query.all()
    users.sort(key=lambda u: u.total_points, reverse=True)
    return render_template("leaderboard.html", user=user, users=users)


@app.route("/predictions/<int:target_id>")
def user_predictions(target_id):
    user = current_user()
    target = db.session.get(User, target_id)
    if not target:
        flash("Usuario no encontrado.", "danger")
        return redirect(url_for("leaderboard"))

    all_matches = Match.query.order_by(Match.match_datetime).all()
    preds_map = {p.match_id: p for p in Prediction.query.filter_by(user_id=target_id).all()}

    # Agrupar por fase en orden canónico
    by_stage = defaultdict(list)
    for m in all_matches:
        by_stage[m.stage].append(m)
    stage_groups = [(s, by_stage[s]) for s in STAGE_ORDER if s in by_stage]

    # Stats
    made = len(preds_map)
    total_pts = target.total_points
    exact = sum(1 for p in preds_map.values() if p.points_earned == 3)
    winner_only = sum(1 for p in preds_map.values() if p.points_earned == 1)

    all_users = User.query.all()
    all_users.sort(key=lambda u: u.total_points, reverse=True)

    return render_template("user_predictions.html",
        user=user,
        target=target,
        stage_groups=stage_groups,
        preds_map=preds_map,
        is_own=user and user.id == target_id,
        stats={"made": made, "total": len(all_matches), "pts": total_pts,
               "exact": exact, "winner": winner_only},
        leaderboard_users=all_users,
    )


def _get_group_teams():
    """Devuelve lista ordenada de los 48 equipos de la fase de grupos."""
    matches = Match.query.filter(Match.stage.like("Grupo%")).all()
    teams = set()
    for m in matches:
        teams.add(m.team1)
        teams.add(m.team2)
    return sorted(teams)


def _get_groups_with_teams():
    """Devuelve dict ordenado {grupo: [equipo1, equipo2, equipo3, equipo4]}."""
    groups = {}
    for m in Match.query.filter(Match.stage.like("Grupo%")).all():
        groups.setdefault(m.stage, set()).update([m.team1, m.team2])
    return {g: sorted(teams) for g, teams in sorted(groups.items())}


def _special_deadline():
    """Cierre: cuando empieza el primer partido."""
    first = Match.query.order_by(Match.match_datetime).first()
    return first.match_datetime if first else datetime(2026, 6, 11, 21, 0)


@app.route("/special", methods=["GET", "POST"])
def special():
    user = current_user()
    if not user:
        flash("Primero ingresá tu nombre para participar.", "warning")
        return redirect(url_for("join"))

    deadline = _special_deadline()
    is_open = datetime.utcnow() < deadline

    result = SpecialResult.query.get(1)
    teams = _get_group_teams()
    existing = SpecialBet.query.filter_by(user_id=user.id).first()

    if request.method == "POST":
        if not is_open:
            flash("Las apuestas especiales ya están cerradas.", "warning")
            return redirect(url_for("special"))

        champion = request.form.get("champion", "").strip()
        semis = [
            request.form.get("semi1", "").strip(),
            request.form.get("semi2", "").strip(),
            request.form.get("semi3", "").strip(),
            request.form.get("semi4", "").strip(),
        ]
        semis_clean = [s for s in semis if s]

        if not champion:
            flash("Seleccioná un campeón.", "danger")
            return redirect(url_for("special"))
        if len(semis_clean) < 4:
            flash("Seleccioná los 4 semifinalistas.", "danger")
            return redirect(url_for("special"))
        if len(set(semis_clean)) < 4:
            flash("Los 4 semifinalistas deben ser equipos distintos.", "danger")
            return redirect(url_for("special"))
        if champion not in semis_clean:
            flash("El campeón debe ser uno de los 4 semifinalistas.", "danger")
            return redirect(url_for("special"))

        if existing:
            existing.champion = champion
            existing.semi1, existing.semi2, existing.semi3, existing.semi4 = semis_clean
            existing.champion_points = None
            existing.semi_points = None
        else:
            db.session.add(SpecialBet(
                user_id=user.id,
                champion=champion,
                semi1=semis_clean[0], semi2=semis_clean[1],
                semi3=semis_clean[2], semi4=semis_clean[3],
            ))
        db.session.commit()

        # Recalcular si ya hay resultado
        if result and result.champion:
            bet = existing or SpecialBet.query.filter_by(user_id=user.id).first()
            c_pts, s_pts = calculate_special_points(bet, result)
            bet.champion_points = c_pts
            bet.semi_points = s_pts
            db.session.commit()

        flash("✅ Apuesta especial guardada.", "success")
        return redirect(url_for("special"))

    # Mostrar apuestas de todos solo cuando ya cerró (evitar trampa)
    all_bets = []
    if not is_open:
        all_bets = (
            db.session.query(SpecialBet, User)
            .join(User, SpecialBet.user_id == User.id)
            .all()
        )

    groups_with_teams = _get_groups_with_teams()

    # Apuestas de clasificados por grupo del usuario actual
    existing_gq = {}
    if existing:
        for gqb in existing.group_qualifier_bets:
            existing_gq[gqb.group_name] = [gqb.team1, gqb.team2]

    # Resultados de clasificados por grupo
    gq_results = {r.group_name: r for r in GroupQualifierResult.query.all()}

    return render_template("special.html",
        user=user, teams=teams, existing=existing,
        result=result, is_open=is_open, deadline=deadline,
        all_bets=all_bets,
        groups_with_teams=groups_with_teams,
        existing_gq=existing_gq,
        gq_results=gq_results)


@app.route("/special/groups", methods=["POST"])
def special_groups():
    user = current_user()
    if not user:
        return redirect(url_for("join"))

    deadline = _special_deadline()
    if datetime.utcnow() >= deadline:
        flash("Las apuestas especiales ya están cerradas.", "warning")
        return redirect(url_for("special"))

    # Asegurar que existe el SpecialBet del usuario
    bet = SpecialBet.query.filter_by(user_id=user.id).first()
    if not bet:
        bet = SpecialBet(user_id=user.id)
        db.session.add(bet)
        db.session.commit()

    groups_with_teams = _get_groups_with_teams()
    errors = []

    for group_name in groups_with_teams:
        selected = request.form.getlist(f"gq_{group_name}")
        if len(selected) != 2:
            errors.append(f"{group_name}: seleccioná exactamente 2 equipos (seleccionaste {len(selected)}).")

    if errors:
        for e in errors:
            flash(e, "danger")
        return redirect(url_for("special"))

    # Guardar o actualizar las apuestas de cada grupo
    existing_map = {gqb.group_name: gqb for gqb in bet.group_qualifier_bets}
    gq_results = {r.group_name: r for r in GroupQualifierResult.query.all()}

    for group_name, _ in groups_with_teams.items():
        selected = request.form.getlist(f"gq_{group_name}")
        if group_name in existing_map:
            gqb = existing_map[group_name]
            gqb.team1, gqb.team2 = selected[0], selected[1]
            gqb.points = None
        else:
            gqb = GroupQualifierBet(
                special_bet_id=bet.id,
                group_name=group_name,
                team1=selected[0], team2=selected[1],
            )
            db.session.add(gqb)
            db.session.flush()

        # Recalcular si ya hay resultado para este grupo
        if group_name in gq_results:
            r = gq_results[group_name]
            gqb.points = calculate_group_qualifier_points(gqb.team1, gqb.team2, r.team1, r.team2)

    db.session.commit()
    flash("✅ Clasificados por grupo guardados.", "success")
    return redirect(url_for("special"))


# ─── Rutas admin ──────────────────────────────────────────────────────────────

@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        password = request.form.get("password", "")
        if password == os.environ.get("ADMIN_PASSWORD", "admin123"):
            session["is_admin"] = True
            return redirect(url_for("admin_dashboard"))
        flash("Contraseña incorrecta.", "danger")
    return render_template("admin/login.html")


@app.route("/admin/logout")
def admin_logout():
    session.pop("is_admin", None)
    return redirect(url_for("index"))


@app.route("/admin")
def admin_dashboard():
    if not session.get("is_admin"):
        return redirect(url_for("admin_login"))
    matches = Match.query.order_by(Match.match_datetime).all()
    return render_template("admin/dashboard.html", matches=matches)


@app.route("/admin/users")
def admin_users():
    if not session.get("is_admin"):
        return redirect(url_for("admin_login"))
    users = User.query.order_by(User.name).all()
    return render_template("admin/users.html", users=users)


@app.route("/admin/users/<int:user_id>/delete", methods=["POST"])
def admin_delete_user(user_id):
    if not session.get("is_admin"):
        return redirect(url_for("admin_login"))
    user = db.session.get(User, user_id)
    if not user:
        flash("Usuario no encontrado.", "danger")
        return redirect(url_for("admin_users"))

    # Eliminar predicciones de partidos
    Prediction.query.filter_by(user_id=user_id).delete()

    # Eliminar apuesta especial y sus clasificados
    bet = SpecialBet.query.filter_by(user_id=user_id).first()
    if bet:
        GroupQualifierBet.query.filter_by(special_bet_id=bet.id).delete()
        db.session.delete(bet)

    name = user.name
    db.session.delete(user)
    db.session.commit()
    flash(f"Usuario «{name}» eliminado junto con todas sus predicciones.", "success")
    return redirect(url_for("admin_users"))


@app.route("/admin/match/new", methods=["GET", "POST"])
def admin_new_match():
    if not session.get("is_admin"):
        return redirect(url_for("admin_login"))
    if request.method == "POST":
        try:
            dt = datetime.strptime(request.form["datetime"], "%Y-%m-%dT%H:%M")
        except ValueError:
            flash("Fecha inválida.", "danger")
            return redirect(url_for("admin_new_match"))
        db.session.add(Match(
            team1=request.form["team1"].strip(),
            team2=request.form["team2"].strip(),
            stage=request.form["stage"].strip(),
            match_datetime=dt,
        ))
        db.session.commit()
        flash("Partido creado.", "success")
        return redirect(url_for("admin_dashboard"))
    return render_template("admin/match.html", match=None)


@app.route("/admin/match/<int:match_id>", methods=["GET", "POST"])
def admin_match(match_id):
    if not session.get("is_admin"):
        return redirect(url_for("admin_login"))
    match = db.session.get(Match, match_id)
    if not match:
        flash("Partido no encontrado.", "danger")
        return redirect(url_for("admin_dashboard"))

    if request.method == "POST":
        action = request.form.get("action")

        if action == "edit":
            try:
                dt = datetime.strptime(request.form["datetime"], "%Y-%m-%dT%H:%M")
            except ValueError:
                flash("Fecha inválida.", "danger")
                return redirect(url_for("admin_match", match_id=match_id))
            match.team1 = request.form["team1"].strip()
            match.team2 = request.form["team2"].strip()
            match.stage = request.form["stage"].strip()
            match.match_datetime = dt
            db.session.commit()
            flash("Partido actualizado.", "success")

        elif action == "result":
            try:
                s1 = int(request.form["score1"])
                s2 = int(request.form["score2"])
                if s1 < 0 or s2 < 0:
                    raise ValueError
            except (ValueError, KeyError):
                flash("Marcador inválido.", "danger")
                return redirect(url_for("admin_match", match_id=match_id))
            match.score1_real = s1
            match.score2_real = s2
            match.is_finished = True
            for pred in match.predictions:
                pred.points_earned = calculate_points(
                    pred.predicted_score1, pred.predicted_score2, s1, s2
                )
            db.session.commit()
            flash(
                f"✅ Resultado cargado: {match.team1} {s1} – {s2} {match.team2}. "
                f"Puntos calculados para {len(match.predictions)} predicciones.",
                "success",
            )

        elif action == "reopen":
            match.is_finished = False
            match.score1_real = None
            match.score2_real = None
            for pred in match.predictions:
                pred.points_earned = None
            db.session.commit()
            flash("Partido reabierto. Puntos revertidos.", "warning")

        return redirect(url_for("admin_dashboard"))

    return render_template("admin/match.html", match=match)


@app.route("/admin/special", methods=["GET", "POST"])
def admin_special():
    if not session.get("is_admin"):
        return redirect(url_for("admin_login"))

    result = SpecialResult.query.get(1)
    teams = _get_group_teams()
    bets = SpecialBet.query.all()

    if request.method == "POST":
        champion = request.form.get("champion", "").strip()
        semis = [
            request.form.get("semi1", "").strip(),
            request.form.get("semi2", "").strip(),
            request.form.get("semi3", "").strip(),
            request.form.get("semi4", "").strip(),
        ]

        if not result:
            result = SpecialResult(id=1)
            db.session.add(result)

        result.champion = champion or None
        result.semi1 = semis[0] or None
        result.semi2 = semis[1] or None
        result.semi3 = semis[2] or None
        result.semi4 = semis[3] or None
        db.session.commit()

        # Recalcular puntos para todas las apuestas
        if result.champion:
            for bet in bets:
                c_pts, s_pts = calculate_special_points(bet, result)
                bet.champion_points = c_pts
                bet.semi_points = s_pts
            db.session.commit()
            flash(f"✅ Resultados guardados. Puntos calculados para {len(bets)} apuestas.", "success")
        else:
            flash("Resultados guardados (sin calcular puntos hasta tener campeón).", "info")

        return redirect(url_for("admin_special"))

    groups_with_teams = _get_groups_with_teams()
    gq_results = {r.group_name: r for r in GroupQualifierResult.query.all()}

    return render_template("admin/special.html",
        result=result, teams=teams, bets=bets,
        groups_with_teams=groups_with_teams, gq_results=gq_results)


@app.route("/admin/special/groups", methods=["POST"])
def admin_special_groups():
    if not session.get("is_admin"):
        return redirect(url_for("admin_login"))

    groups_with_teams = _get_groups_with_teams()
    existing_map = {r.group_name: r for r in GroupQualifierResult.query.all()}

    for group_name in groups_with_teams:
        t1 = request.form.get(f"real_{group_name}_1", "").strip() or None
        t2 = request.form.get(f"real_{group_name}_2", "").strip() or None

        if group_name in existing_map:
            existing_map[group_name].team1 = t1
            existing_map[group_name].team2 = t2
        else:
            db.session.add(GroupQualifierResult(group_name=group_name, team1=t1, team2=t2))

    db.session.commit()

    # Recalcular puntos de todas las apuestas de clasificados
    gq_results = {r.group_name: r for r in GroupQualifierResult.query.all()}
    count = 0
    for gqb in GroupQualifierBet.query.all():
        r = gq_results.get(gqb.group_name)
        if r and r.team1:
            gqb.points = calculate_group_qualifier_points(gqb.team1, gqb.team2, r.team1, r.team2)
            count += 1
        else:
            gqb.points = None
    db.session.commit()

    flash(f"✅ Clasificados guardados. Puntos recalculados para {count} apuestas.", "success")
    return redirect(url_for("admin_special"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
