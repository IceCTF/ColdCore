from flask import Flask, render_template, session, redirect, url_for, request, g, flash, jsonify
app = Flask(__name__)

from database import User, Team, UserAccess, Challenge, ChallengeSolve, ChallengeFailure, ScoreAdjustment, TroubleTicket, TicketComment, Notification, db
from datetime import datetime, timedelta
from peewee import fn

from utils import decorators, flag, cache, misc, captcha, email, select
import utils.scoreboard

import config
import utils
import redis
import requests
import socket

app.secret_key = config.secret.key

import logging
logging.basicConfig(level=logging.DEBUG)

@app.before_request
def make_info_available():
    if "user_id" in session:
        try:
            g.user = User.get(User.id == session["user_id"])
            g.user_restricts = g.user.restricts.split(",")
            g.team = g.user.team
            g.team_restricts = g.team.restricts.split(",")
        except User.DoesNotExist:
            session.pop("user_id")
            return render_template("login.html")

@app.context_processor
def scoreboard_variables():
    var = dict(config=config, select=select)
    if "user_id" in session:
        var["logged_in"] = True
        var["user"] = g.user
        var["team"] = g.team
        # TODO should this apply to users or teams?
        # var["notifications"] = Notification.select().where(Notification.user == g.user)
        var["notifications"] = []
    else:
        var["logged_in"] = False
        var["notifications"] = []

    return var

# Blueprints
from modules import api, admin
app.register_blueprint(api.api)
app.register_blueprint(admin.admin)

# Publically accessible things

@app.route('/')
def root():
    return redirect(url_for('register'))

@app.route('/chat/')
def chat():
    return render_template("chat.html")

@app.route('/scoreboard/')
def scoreboard():
    data = cache.get_complex("scoreboard")
    graphdata = cache.get_complex("graph")
    if data is None or graphdata is None:
        if config.immediate_scoreboard:
            data = utils.scoreboard.calculate_scores()
            graphdata = utils.scoreboard.calculate_graph(data)
            utils.scoreboard.set_complex("scoreboard", data, 120)
            utils.scoreboard.set_complex("graph", graphdata, 120)
        else:
            return "No scoreboard data available. Please contact an organizer."

    return render_template("scoreboard.html", data=data, graphdata=graphdata)

@app.route('/login/', methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    elif request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        try:
            user = User.get(User.username == username)
            if(user.checkPassword(password)):
                UserAccess.create(user=user, ip=misc.get_ip(), time=datetime.now())
                session["user_id"] = user.id
                flash("Login successful.")
                return redirect(url_for('team_dashboard'))
            else:
                flash("Incorrect username or password", "error")
                return render_template("login.html")
        except User.DoesNotExist:
            flash("Incorrect username or password", "error")
            return render_template("login.html")

@app.route('/register/', methods=["GET", "POST"])
def register():
    if not config.registration:
        if "admin" in session and session["admin"]:
            pass
        else:
            return "Registration is currently disabled. Email icectf@icec.tf to create an account."

    if request.method == "GET":
        return render_template("register.html")
    elif request.method == "POST":
        error, message = captcha.verify_captcha()
        if error:
            flash(message)
            return render_template("register.html")

        username = request.form["username"].strip()
        user_email = request.form["email"].strip()
        password = request.form["password"].strip()
        confirm_password = request.form["confirm_password"].strip()
        background = request.form["background"].strip()
        country = request.form["country"].strip()

        tshirt_size = ""
        gender = ""
        if "tshirt_size" in request.form.keys():
            tshirt_size = request.form["tshirt_size"].strip()
        if "gender" in request.form.keys():
            gender = request.form["gender"].strip()

        join_team = bool(int(request.form["join_team"].strip()))
        if join_team:
            team_key = request.form["team_key"].strip()
        else:
            team_name = request.form["team_name"].strip()
            team_affiliation = request.form["team_affiliation"].strip()

        if len(username) > 50 or not username:
            flash("You must have a username!")
            return render_template("register.html")

        try:
            user = User.get(User.username == username)
            flash("This username is already in use!")
            return render_template("register.html")
        except User.DoesNotExist:
            pass

        if password != confirm_password:
            flash("Password does not match confirmation")
            return render_template("register.html")

        if not (user_email and "." in user_email and "@" in user_email):
            flash("You must have a valid email!")
            return render_template("register.html")

        if not email.is_valid_email(user_email):
            flash("You're lying")
            return render_template("register.html")

        if (not tshirt_size == "") and (not tshirt_size in select.TShirts):
            flash("Invalid T-shirt size")
            return render_template("register.html")

        if not background in select.BackgroundKeys:
            flash("Invalid Background")
            return render_template("register.html")

        if not country in select.CountryKeys:
            flash("Invalid Background")
            return render_template("register.html")

        if (not gender == "") and (not gender in ["M", "F"]):
            flash("Invalid gender")
            return render_template("register.html")

        confirmation_key = misc.generate_confirmation_key()

        team=None
        if join_team:
            try:
                team = Team.get(Team.key == team_key)
            except Team.DoesNotExist:
                flash("Couldn't find this team, check your team key.")
                return render_template("register.html")
        else:
            if not team_name or len(team_name) > 50:
                flash("Missing team name")
                return render_template("register.html")
            if not team_affiliation or len(team_affiliation) > 100:
                team_affiliation = "No affiliation"
            try:
                team = Team.get(Team.name == team_name)
                flash("This team name is already in use!")
                return render_template("register.html")
            except Team.DoesNotExist:
                pass
            team_key = misc.generate_team_key()
            team = Team.create(name=team_name, affiliation=team_affiliation, key=team_key)


        user = User.create(username=username, email=user_email,
                background=background, country=country,
                tshirt_size=tshirt_size, gender=gender,
                email_confirmation_key=confirmation_key,
                team=team)
        user.setPassword(password)
        user.save()

        UserAccess.create(user=user, ip=misc.get_ip(), time=datetime.now())
        # print(confirmation_key)

        email.send_confirmation_email(user_email, confirmation_key)

        session["user_id"] = user.id
        flash("Registration finished")
        return redirect(url_for('user_dashboard'))

@app.route('/logout/')
def logout():
    session.pop("user_id")
    flash("You've successfully logged out.")
    return redirect(url_for('login'))

# Things that require a team

@app.route('/confirm_email/<confirmation_key>', methods=["GET"])
@decorators.login_required
def confirm_email(confirmation_key):
    if confirmation_key == g.user.email_confirmation_key:
        flash("Email confirmed!")
        g.user.email_confirmed = True
        g.user.save()
    else:
        flash("Incorrect confirmation key.")
    return redirect(url_for('user_dashboard'))

@app.route('/forgot_password/', methods=["GET", "POST"])
def forgot_password():
    if request.method == "GET":
        return render_template("forgot_password.html")
    elif request.method == "POST":
        username = request.form["username"].strip()
        if len(username) > 50 or not username:
            flash("You must have a username!")
            return redirect(url_for('forgot_password'))

        try:
            user = User.get(User.username == username)
            user.password_reset_token = misc.generate_confirmation_key()
            user.password_reset_expired = datetime.now() + timedelta(days=1)
            user.save()
            email.send_password_reset_email(user.email, user.password_reset_token)
            flash("Forgot password email sent! Check your email.")
            return render_template("forgot_password.html")
        except User.DoesNotExist:
            flash("Username is not registered", "error")
            return render_template("forgot_password.html")

@app.route('/reset_password/<password_reset_token>', methods=["GET", "POST"])
def reset_password(password_reset_token):
    if request.method == "GET":
        return render_template("reset_password.html")
    elif request.method == "POST":
        password = request.form["password"].strip()
        confirm_password = request.form["confirm_password"].strip()

        if not password == confirm_password:
            flash("Password does not match")
            return render_template("reset_password.html", password_reset_token=password_reset_token)

        if not password_reset_token:
            flash("Reset Token is invalid", "error")
            return redirect(url_for("forgot_password"))

        try:
            user = User.get(User.password_reset_token == password_reset_token)
            if user.password_reset_expired < datetime.now():
                flash("Token expired")
                return redirect(url_for("forgot_password"))

            user.setPassword(password)
            user.password_reset_token = None
            user.save()
            flash("Password successfully reset")
            return redirect(url_for("login"))
        except User.DoesNotExist:
            flash("Reset Token is invalid", "error")
            return redirect(url_for("forgot_password"))

@app.route('/user/', methods=["GET", "POST"])
@decorators.login_required
def user_dashboard():
    if request.method == "GET":
        first_login = False
        if g.user.first_login:
            first_login = True
            g.user.first_login = False
            g.user.save()
        return render_template("user.html", first_login=first_login)
    elif request.method == "POST":
        if g.redis.get("ul{}".format(session["user_id"])):
            flash("You're changing your information too fast!")
            return redirect(url_for('user_dashboard'))

        username = request.form["username"].strip()
        user_email = request.form["email"].strip()
        password = request.form["password"].strip()
        confirm_password = request.form["confirm_password"].strip()
        background = request.form["background"].strip()
        country = request.form["country"].strip()

        tshirt_size = ""
        gender = ""
        if "tshirt_size" in request.form.keys():
            tshirt_size = request.form["tshirt_size"].strip()
        if "gender" in request.form.keys():
            gender = request.form["gender"].strip()

        if len(username) > 50 or not username:
            flash("You must have a username!")
            return redirect(url_for('user_dashboard'))
        if g.user.username != username:
            try:
                user = User.get(User.username == username)
                flash("This username is already in use!")
                return redirect(url_for('user_dashboard'))
            except User.DoesNotExist:
                pass

        if not (user_email and "." in user_email and "@" in user_email):
            flash("You must have a valid email!")
            return redirect(url_for('user_dashboard'))

        if not email.is_valid_email(user_email):
            flash("You're lying")
            return redirect(url_for('user_dashboard'))

        if (not tshirt_size == "") and (not tshirt_size in select.TShirts):
            flash("Invalid T-shirt size")
            return redirect(url_for('user_dashboard'))

        if not background in select.BackgroundKeys:
            flash("Invalid Background")
            return redirect(url_for('user_dashboard'))

        if not country in select.CountryKeys:
            flash("Invalid Background")
            return redirect(url_for('user_dashboard'))

        if (not gender == "") and (not gender in ["M", "F"]):
            flash("Invalid gender")
            return redirect(url_for('user_dashboard'))

        email_changed = (user_email != g.user.email)

        g.user.username = username
        g.user.email = user_email
        g.user.background = background
        g.user.country = country
        g.user.gender = gender
        g.user.tshirt_size = tshirt_size

        g.redis.set("ul{}".format(session["user_id"]), str(datetime.now()), 120)

        if password != "":
            if password != confirm_password:
                flash("Password does not match confirmation")
                return redirect(url_for('user_dashboard'))
            g.user.setPassword(password)

        if email_changed:
            g.user.email_confirmation_key = misc.generate_confirmation_key()
            g.user.email_confirmed = False

            email.send_confirmation_email(user_email, g.user.email_confirmation_key)
            flash("Changes saved. Please check your email for a new confirmation key.")
        else:
            flash("Changes saved.")
        g.user.save()


        return redirect(url_for('user_dashboard'))
@app.route('/team/', methods=["GET", "POST"])
@decorators.login_required
def team_dashboard():
    if request.method == "GET":
        team_solves = ChallengeSolve.select(ChallengeSolve, Challenge).join(Challenge).where(ChallengeSolve.team == g.team)
        team_adjustments = ScoreAdjustment.select().where(ScoreAdjustment.team == g.team)
        team_score = sum([i.challenge.points for i in team_solves] + [i.value for i in team_adjustments])
        return render_template("team.html", team_solves=team_solves, team_adjustments=team_adjustments, team_score=team_score)
    elif request.method == "POST":
        if g.redis.get("ul{}".format(session["user_id"])):
            flash("You're changing your information too fast!")
            return redirect(url_for('team_dashboard'))

        team_name = request.form["team_name"].strip()
        affiliation = request.form["team_affiliation"].strip()

        if len(team_name) > 50 or not team_name:
            flash("You must have a team name!")
            return redirect(url_for('team_dashboard'))

        if not affiliation or len(affiliation) > 100:
            affiliation = "No affiliation"

        if g.team.name != team_name:
            try:
                team = Team.get(Team.name == team_name)
                flash("This team name is already in use!")
                return redirect(url_for('team_dashboard'))
            except Team.DoesNotExist:
                pass

        g.team.name = team_name
        g.team.affiliation = affiliation

        g.redis.set("ul{}".format(session["user_id"]), str(datetime.now()), 120)

        flash("Changes saved.")
        g.team.save()


        return redirect(url_for('team_dashboard'))

@app.route('/teamconfirm/', methods=["POST"])
def teamconfirm():
    if utils.misc.get_ip() in config.confirm_ip:
        team_name = request.form["team_name"].strip()
        team_key = request.form["team_key"].strip()
        try:
            team = Team.get(Team.name == team_name)
        except Team.DoesNotExist:
            return "invalid", 403
        if team.key == team_key:
            return "ok", 200
        else:
            return "invalid", 403
    else:
        return "unauthorized", 401

@app.route('/challenges/')
@decorators.must_be_allowed_to("view challenges")
@decorators.competition_running_required
@decorators.confirmed_email_required
def challenges():
    chals = Challenge.select().order_by(Challenge.points, Challenge.name)
    solved = Challenge.select().join(ChallengeSolve).where(ChallengeSolve.team == g.team)
    solves = {i: int(g.redis.hget("solves", i).decode()) for i in [k.id for k in chals]}
    categories = sorted(list({chal.category for chal in chals}))
    return render_template("challenges.html", challenges=chals, solved=solved, categories=categories, solves=solves)

@app.route('/challenges/<int:challenge>/solves/')
@decorators.must_be_allowed_to("view challenge solves")
@decorators.must_be_allowed_to("view challenges")
@decorators.competition_running_required
@decorators.confirmed_email_required
def challenge_show_solves(challenge):
    chal = Challenge.get(Challenge.id == challenge)
    solves = ChallengeSolve.select(ChallengeSolve, Team).join(Team).order_by(ChallengeSolve.time).where(ChallengeSolve.challenge == chal)
    return render_template("challenge_solves.html", challenge=chal, solves=solves)

@app.route('/submit/<int:challenge>/', methods=["POST"])
@decorators.must_be_allowed_to("solve challenges")
@decorators.must_be_allowed_to("view challenges")
@decorators.competition_running_required
@decorators.confirmed_email_required
def submit(challenge):
    chal = Challenge.get(Challenge.id == challenge)
    flagval = request.form["flag"]

    code, message = flag.submit_flag(g.team, chal, flagval)
    flash(message)
    return redirect(url_for('challenges'))

# Trouble tickets

@app.route('/tickets/')
@decorators.must_be_allowed_to("view tickets")
@decorators.login_required
def team_tickets():
    return render_template("tickets.html", tickets=list(g.team.tickets))

@app.route('/tickets/new/', methods=["GET", "POST"])
@decorators.must_be_allowed_to("submit tickets")
@decorators.must_be_allowed_to("view tickets")
@decorators.login_required
def open_ticket():
    if request.method == "GET":
        return render_template("open_ticket.html")
    elif request.method == "POST":
        if g.redis.get("ticketl{}".format(session["user_id"])):
            return "You're doing that too fast."
        g.redis.set("ticketl{}".format(g.team.id), "1", 30)
        summary = request.form["summary"]
        description = request.form["description"]
        opened_at = datetime.now()
        ticket = TroubleTicket.create(team=g.team, summary=summary, description=description, opened_at=opened_at)
        flash("Ticket #{} opened.".format(ticket.id))
        return redirect(url_for("team_ticket_detail", ticket=ticket.id))

@app.route('/tickets/<int:ticket>/')
@decorators.must_be_allowed_to("view tickets")
@decorators.login_required
def team_ticket_detail(ticket):
    try:
        ticket = TroubleTicket.get(TroubleTicket.id == ticket)
    except TroubleTicket.DoesNotExist:
        flash("Couldn't find ticket #{}.".format(ticket))
        return redirect(url_for("team_tickets"))

    if ticket.team != g.team:
        flash("That's not your ticket.")
        return redirect(url_for("team_tickets"))

    comments = TicketComment.select().where(TicketComment.ticket == ticket).order_by(TicketComment.time)
    return render_template("ticket_detail.html", ticket=ticket, comments=comments)

@app.route('/tickets/<int:ticket>/comment/', methods=["POST"])
@decorators.must_be_allowed_to("comment on tickets")
@decorators.must_be_allowed_to("view tickets")
def team_ticket_comment(ticket):
    if g.redis.get("ticketl{}".format(session["user_id"])):
        return "You're doing that too fast."
    g.redis.set("ticketl{}".format(g.team.id), "1", 30)
    try:
        ticket = TroubleTicket.get(TroubleTicket.id == ticket)
    except TroubleTicket.DoesNotExist:
        flash("Couldn't find ticket #{}.".format(ticket))
        return redirect(url_for("team_tickets"))

    if ticket.team != g.team:
        flash("That's not your ticket.")
        return redirect(url_for("team_tickets"))

    if request.form["comment"]:
        TicketComment.create(ticket=ticket, comment_by=g.team.name, comment=request.form["comment"], time=datetime.now())
        flash("Comment added.")

    if ticket.active and "resolved" in request.form:
        ticket.active = False
        ticket.save()
        flash("Ticket closed.")

    elif not ticket.active and "resolved" not in request.form:
        ticket.active = True
        ticket.save()
        flash("Ticket re-opened.")

    return redirect(url_for("team_ticket_detail", ticket=ticket.id))

# Debug
@app.route('/debug/')
def debug_app():
    return jsonify(hostname=socket.gethostname())

# Manage Peewee database sessions and Redis

@app.before_request
def before_request():
    g.connected = True
    db.connect()
    g.redis = redis.StrictRedis()

@app.teardown_request
def teardown_request(exc):
    if getattr(g, 'connected', False):
        db.close()
        g.redis.connection_pool.disconnect()

# CSRF things

@app.before_request
def csrf_protect():
    csrf_exempt = ['/teamconfirm/']

    if request.method == "POST":
        token = session.get('_csrf_token', None)
        if (not token or token != request.form["_csrf_token"]) and not request.path in csrf_exempt:
            return "Invalid CSRF token!"

def generate_csrf_token():
    if '_csrf_token' not in session:
        session['_csrf_token'] = misc.generate_random_string(64)
    return session['_csrf_token']

app.jinja_env.globals['csrf_token'] = generate_csrf_token

if __name__ == '__main__':
    app.run(debug=True, port=8001)
