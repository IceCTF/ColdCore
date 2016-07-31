from flask import Blueprint, jsonify, g, request
from data import challenge, notification, scoreboard
from utils import decorators, ratelimit
import exceptions
from datetime import datetime
import config

api = Blueprint("api", __name__, url_prefix="/api")


@api.route("/submit/<int:challenge>.json", methods=["POST"])
@decorators.must_be_allowed_to("solve challenges")
@decorators.must_be_allowed_to("view challenges")
@decorators.competition_running_required
@decorators.confirmed_email_required
@ratelimit.ratelimit(limit=10, per=120, over_limit=ratelimit.on_over_api_limit)
def submit_api(challenge_id):
    try:
        chall = challenge.get_challenge(challenge_id)
    except exceptions.ValidationError as e:
        return jsonify(dict(code=1001, message=str(e)))
    flag = request.form["flag"]

    try:
        challenge.submit_flag(chall, g.user, g.team, flag)
        return jsonify(dict(code=0, message="Success!"))
    except exceptions.ValidationError as e:
        return jsonify(dict(code=1001, message=str(e)))


@api.route("/dismiss/<int:nid>.json", methods=["POST"])
@decorators.login_required
def dismiss_notification(nid):
    try:
        n = notification.get_notification(g.team, nid)
        notification.delete_notification(n)
        return jsonify(dict(code=0, message="Success!"))
    except exceptions.ValidationError as e:
        return jsonify(dict(code=1001, message=str(e)))


@api.route("/_ctftime/")
def ctftime_scoreboard_json():
    if not config.immediate_scoreboard and datetime.now() < config.competition_end:
        return "unavailable", 503

    scores = scoreboard.calculate_scores()
    standings = [dict(team=i[2], score=i[4], outward=not i[0]) for i in scores]
    for index, standing in enumerate(standings):
        standing["pos"] = index + 1

    return jsonify(standings=standings)
