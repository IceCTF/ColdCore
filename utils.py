import random
import config
import json
from functools import wraps
from flask import request, session, redirect, url_for, flash, g
from database import Team, Challenge, ChallengeSolve, ScoreAdjustment

allowed_chars = "abcdefghijklmnopqrstuvwxyz0123456789"

def generate_random_string(length=32, chars=allowed_chars):
    return "".join([random.choice(chars) for i in range(length)])

def generate_team_key():
    return config.ctf_name.lower() + "_" + generate_random_string(32, allowed_chars)

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
    teams = Team.select(Team.id, Team, ChallengeSolve).join(ChallengeSolve)

    team_mapping = {team.id: team for team in teams}
    scores = {team.id: 0 for team in teams}
    most_recent_solve = {team.id: max([i.time for i in team.solves]) for team in teams}
    for solve in solves:
        scores[solve.team_id] += solve.challenge.points
    for adjustment in adjustments:
        scores[adjustment.team_id] += adjustment.value
    return [(team_mapping[i[0]].eligible, team_mapping[i[0]].name, team_mapping[i[0]].affiliation, i[1]) for idx, i in enumerate(sorted(scores.items(), key=lambda k: (-k[1], most_recent_solve[k[0]])))]

def get_complex(key):
    i = g.redis.get(key)
    if i is None:
        return None
    return json.loads(i.decode())

def set_complex(key, val, ex):
    g.redis.set(key, json.dumps(val), ex)
