from flask import Flask, render_template, session, redirect, url_for, request, g, flash, jsonify

import redis
import socket
import logging

import config

from utils import misc, select

from data.database import db
import data

# Blueprints
from routes import api, admin, teams, users, challenges, tickets, scoreboard, shell

if config.production:
    logging.basicConfig(level=logging.INFO)
else:
    logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
app.secret_key = config.secret.key


app.register_blueprint(api.api)
app.register_blueprint(admin.admin)
app.register_blueprint(teams.teams)
app.register_blueprint(users.users)
app.register_blueprint(challenges.challenges)
app.register_blueprint(tickets.tickets)
app.register_blueprint(scoreboard.scoreboard)
app.register_blueprint(shell.shell)


@app.before_request
def make_info_available():
    if "user_id" in session:
        g.logged_in = True
        current_user = data.user.get_user(id=session["user_id"])
        if current_user is not None:
            g.user = current_user
            g.user_restricts = g.user.restricts.split(",")
            g.team = g.user.team
            g.team_restricts = g.team.restricts.split(",")
        else:
            g.logged_in = False
            session.pop("user_id")
            return render_template("login.html")
    else:
        g.logged_in = False


@app.context_processor
def scoreboard_variables():
    var = dict(config=config, select=select)
    if "user_id" in session:
        var["logged_in"] = True
        var["user"] = g.user
        var["team"] = g.team
        var["notifications"] = data.notification.get_notifications(team=g.team)
    else:
        var["logged_in"] = False
        var["notifications"] = []

    return var


@app.route('/')
def root():
    if g.logged_in:
        return redirect(url_for('teams.dashboard'))
    return redirect(url_for('users.register'))


@app.route('/chat/')
def chat():
    return render_template("chat.html")


# Debug
@app.route('/debug/')
def debug_app():
    return jsonify(hostname=socket.gethostname())


# Manage Peewee database sessions and Redis
@app.before_request
def before_request():
    db.connect()
    g.redis = redis.StrictRedis(host=config.redis.host, port=config.redis.port, db=config.redis.db)
    g.connected = True


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
        if (not token or token != request.form["_csrf_token"]) and request.path not in csrf_exempt:
            return "Invalid CSRF token!"


def generate_csrf_token():
    if '_csrf_token' not in session:
        session['_csrf_token'] = misc.generate_random_string(64)
    return session['_csrf_token']


app.jinja_env.globals['csrf_token'] = generate_csrf_token

if __name__ == '__main__':
    app.run(debug=True, port=8001)
