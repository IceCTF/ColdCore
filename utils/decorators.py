import config
from flask import session, redirect, url_for, flash, g
from functools import wraps

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

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "admin" not in session:
            flash("You must be an admin to access that page.")
            return redirect(url_for("admin.admin_login"))
        return f(*args, **kwargs)
    return decorated
