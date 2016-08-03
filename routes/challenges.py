from flask import Blueprint, g, request, render_template, flash, redirect, url_for

from utils import decorators, ratelimit
from data import challenge

import exceptions

challenges = Blueprint("challenges", __name__, template_folder="../templates/challenges")


@challenges.route('/challenges/')
@decorators.must_be_allowed_to("view challenges")
@decorators.competition_running_required
@decorators.confirmed_email_required
def index():
    chals = challenge.get_challenges()
    solved = challenge.get_solved(g.team)
    solves = {i: int(g.redis.hget("solves", i).decode()) for i in [k.id for k in chals]}
    categories = sorted(list({chal.category for chal in chals}))
    return render_template("challenges.html", challenges=chals, solved=solved, categories=categories, solves=solves)


@challenges.route('/challenges/<int:challenge_id>/solves/')
@decorators.must_be_allowed_to("view challenge solves")
@decorators.must_be_allowed_to("view challenges")
@decorators.competition_running_required
@decorators.confirmed_email_required
def show_solves(challenge_id):
    try:
        chall = challenge.get_challenge(challenge_id)
    except exceptions.ValidationError as e:
        flash(str(e))
        return redirect(url_for(".index"))
    solves = challenge.get_challenge_solves(chall)
    return render_template("challenge_solves.html", challenge=chall, solves=solves)


@challenges.route('/submit/<int:challenge_id>/', methods=["POST"])
@decorators.must_be_allowed_to("solve challenges")
@decorators.must_be_allowed_to("view challenges")
@decorators.competition_running_required
@decorators.confirmed_email_required
@ratelimit.ratelimit(limit=10, per=120)
def submit(challenge_id):
    try:
        chall = challenge.get_challenge(challenge_id)
    except exceptions.ValidationError as e:
        flash(str(e))
        return redirect(url_for(".index"))
    flag = request.form["flag"]

    try:
        challenge.submit_flag(chall, g.user, g.team, flag)
        flash("Success!")
    except exceptions.ValidationError as e:
        flash(str(e))
    return redirect(url_for('.index'))
