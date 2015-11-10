import random
import config
import json
import requests
from datetime import datetime
from functools import wraps
from flask import request, session, redirect, url_for, flash, g
from database import Team, Challenge, ChallengeSolve, ScoreAdjustment

allowed_chars = "abcdefghijklmnopqrstuvwxyz0123456789"

def generate_random_string(length=32, chars=allowed_chars):
    return "".join([random.choice(chars) for i in range(length)])

def generate_team_key():
    return config.ctf_name.lower() + "_" + generate_random_string(32, allowed_chars)

def generate_confirmation_key():
    return generate_random_string(48)

def get_ip():
    return request.headers.get(config.proxied_ip_header, request.remote_addr)

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "team_id" not in session:
            flash("You need to be logged in to access that page.")
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

def confirmed_email_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "team_id" not in session:
            flash("You need to be logged in to access that page.")
            return redirect(url_for('login'))
        if not g.team.email_confirmed:
            flash("You need to confirm your email in order to access that page.")
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated

def competition_running_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not config.competition_is_running:
            flash("The competition must be running in order for you to access that page.")
            return redirect(url_for('scoreboard'))
        return f(*args, **kwargs)
    return decorated

def calculate_scores():
    solves = ChallengeSolve.select(ChallengeSolve, Challenge).join(Challenge)
    adjustments = ScoreAdjustment.select()
    teams = Team.select()

    team_solves = {team.id: [] for team in teams}
    team_mapping = {team.id: team for team in teams}
    scores = {team.id: 0 for team in teams}
    for solve in solves:
        scores[solve.team_id] += solve.challenge.points
        team_solves[solve.team_id].append(solve)
    for adjustment in adjustments:
        scores[adjustment.team_id] += adjustment.value

    most_recent_solve = {tid: max([i.time for i in team_solves[tid]]) for tid in team_solves if team_solves[tid]}
    scores = {i: j for i, j in scores.items() if i in most_recent_solve}
    return [(team_mapping[i[0]].eligible, i[0], team_mapping[i[0]].name, team_mapping[i[0]].affiliation, i[1]) for idx, i in enumerate(sorted(scores.items(), key=lambda k: (-k[1], most_recent_solve[k[0]])))]

def calculate_graph(scoredata):
    solves = list(ChallengeSolve.select(ChallengeSolve, Challenge).join(Challenge).order_by(ChallengeSolve.time))
    adjustments = list(ScoreAdjustment.select())
    scoredata = [i for i in scoredata if i[0]] # Only eligible teams are on the score graph
    graph_data = []
    for eligible, tid, name, affiliation, score in scoredata[:config.teams_on_graph]:
        our_solves = [i for i in solves if i.team_id == tid]
        team_data = []
        s = sum([i.value for i in adjustments if i.team_id == tid])
        for i in sorted(our_solves, key=lambda k: k.time):
            team_data.append((str(i.time), s))
            s += i.challenge.points
            team_data.append((str(i.time), s))
        team_data.append((str(datetime.now()), score))
        graph_data.append((name, team_data))
    return graph_data

def get_complex(key):
    i = g.redis.get(key)
    if i is None:
        return None
    return json.loads(i.decode())

def set_complex(key, val, ex):
    g.redis.set(key, json.dumps(val), ex)

def send_email(to, subject, text):
    return requests.post("{}/messages".format(config.secret.mailgun_url), {"from": config.mail_from, "to": to, "subject": subject, "text": text}, auth=("api", config.secret.mailgun_key))

def send_confirmation_email(team_email, confirmation_key, team_key):
    send_email(team_email, "Welcome to {}!".format(config.ctf_name),
"""Hello, and thanks for registering for {}! Before you can start solving problems,
you must confirm your email by entering this code into the team dashboard:

{}

Once you've done that, your account will be enabled, and you will be able to access
the challenges. If you have any trouble, feel free to contact an organizer!

If you didn't register an account, then you can disregard this email.

In case you lose it, your team key is: {}""".format(config.ctf_name, confirmation_key, team_key))
