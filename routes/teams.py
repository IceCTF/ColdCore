from flask import Blueprint, g, request, render_template, flash, url_for, redirect

from data import team, challenge

from utils import decorators, ratelimit
import utils
import config

import exceptions

teams = Blueprint("teams", __name__, template_folder="../templates/teams")
# Things that require a team


@teams.route('/team/', methods=["GET", "POST"])
@decorators.login_required
@ratelimit.ratelimit(limit=6, per=120)
def dashboard():
    if request.method == "GET":
        team_solves = challenge.get_solved(g.team)
        team_adjustments = challenge.get_adjustments(g.team)
        team_score = sum([i.challenge.points for i in team_solves] + [i.value for i in team_adjustments])
        return render_template("team.html", team_solves=team_solves, team_adjustments=team_adjustments, team_score=team_score)
    elif request.method == "POST":

        team_name = request.form["team_name"].strip()
        affiliation = request.form["team_affiliation"].strip()

        try:
            team.update_team(g.team, team_name, affiliation)
            flash("Changes saved.")
        except exceptions.ValidationError as e:
            flash(str(e))

        return redirect(url_for('.dashboard'))


@teams.route('/teamconfirm/', methods=["POST"])
def teamconfirm():
    if utils.misc.get_ip() in config.confirm_ip:
        team_name = request.form["team_name"].strip()
        team_key = request.form["team_key"].strip()
        t = team.get_team(name=team_name)
        if t is None:
            return "invalid", 403
        if t.key == team_key:
            return "ok", 200
        else:
            return "invalid", 403
    else:
        return "unauthorized", 401
