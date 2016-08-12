import config
from flask import session, redirect, url_for, flash, g, abort
from functools import wraps

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" in session and session["user_id"]:
            return f(*args, **kwargs)
        else:
            flash("You need to be logged in")
            return redirect(url_for('users.login'))
    return decorated

def must_be_allowed_to(thing):
    def _must_be_allowed_to(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if getattr(g, 'user_restricts', None) is None:
                return redirect(url_for('users.login'))
            if g.user_restricts and thing in g.user_restricts:
                return "You are restricted from performing the {} action. Contact an organizer.".format(thing)

            return f(*args, **kwargs)
        return decorated
    return _must_be_allowed_to

def confirmed_email_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" in session and session["user_id"]:
            if not g.user.email_confirmed:
                flash("Please confirm your email")
                return redirect(url_for('users.dashboard'))
            else:
                return f(*args, **kwargs)
        else:
            flash("You need to be logged in to access that page.")
            return redirect(url_for('users.login'))
    return decorated

def competition_running_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not config.competition_is_running() and not ("admin" in session and session["admin"]):
            flash("The competition hasn't started")
            return redirect(url_for('scoreboard.index'))
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
