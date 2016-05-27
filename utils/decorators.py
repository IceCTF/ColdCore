import config
from flask import session, redirect, url_for, flash, g, abort
from functools import wraps

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "team_id" in session and session["team_id"]:
            return f(*args, **kwargs)
        else:
            flash("You need to be logged in to access that page.")
            return redirect(url_for('login'))
    return decorated

def must_be_allowed_to(thing):
    def _must_be_allowed_to(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if getattr(g, 'team_restricts', None) is None:
                return redirect(url_for('login'))
            if g.team_restricts and thing in g.team_restricts:
                return "You are restricted from performing the {} action. Contact an organizer.".format(thing)

            return f(*args, **kwargs)
        return decorated
    return _must_be_allowed_to

def confirmed_email_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "team_id" in session and session["team_id"]:
            if not g.team.email_confirmed:
                flash("Please confirm your email in order to access that page.")
                return redirect(url_for('dashboard'))
            else:
                return f(*args, **kwargs)
        else:
            flash("You need to be logged in to access that page.")
            return redirect(url_for('login'))
    return decorated

def competition_running_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not config.competition_is_running():
            flash("The competition must be running in order for you to access that page.")
            return redirect(url_for('scoreboard'))
        return f(*args, **kwargs)
    return decorated

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "admin" in session and session["admin"]:
            return f(*args, **kwargs)
        flash("You must be an admin to access that page.")
        return redirect(url_for("admin.admin_login"))
    return decorated

def csrf_check(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if kwargs["csrf"] != session["_csrf_token"]:
            abort(403)
            return

        del kwargs["csrf"]

        return f(*args, **kwargs)
    return decorated
