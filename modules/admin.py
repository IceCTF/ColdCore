from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from database import AdminUser, Team, Challenge, ChallengeSolve, ChallengeFailure, ScoreAdjustment
import utils
import utils.admin
import utils.scoreboard
admin = Blueprint("admin", "admin", url_prefix="/admin")

@admin.route("/")
def admin_root():
    if "admin" in session:
        return redirect(url_for(".admin_dashboard"))
    else:
        return redirect(url_for(".admin_login"))

@admin.route("/login/", methods=["GET", "POST"])
def admin_login():
    if request.method == "GET":
        return render_template("admin/login.html")

    elif request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        try:
            user = AdminUser.get(AdminUser.username == username)
            result = utils.admin.verify_password(user, password)
            if result:
                session["admin"] = user.username
                return redirect(url_for(".admin_dashboard"))
        except AdminUser.DoesNotExist:
            pass
        flash("Invalid username or password.")
        return render_template("admin/login.html")

@admin.route("/dashboard/")
def admin_dashboard():
    teams = Team.select()
    solves = ChallengeSolve.select(ChallengeSolve, Challenge).join(Challenge)
    adjustments = ScoreAdjustment.select()
    scoredata = utils.scoreboard.get_all_scores(teams, solves, adjustments)
    lastsolvedata = utils.scoreboard.get_last_solves(teams, solves)
    return render_template("admin/dashboard.html", teams=teams, scoredata=scoredata, lastsolvedata=lastsolvedata)

@admin.route("/team/<int:tid>/")
def admin_show_team(tid):
    team = Team.get(Team.id == tid)
    return render_template("admin/team.html", team=team)

@admin.route("/logout/")
def admin_logout():
    del session["admin"]
    return redirect(url_for('.admin_login'))
