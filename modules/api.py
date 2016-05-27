from flask import Blueprint, jsonify, g, request
from database import Challenge, Notification, Team, Challenge, ChallengeSolve
from utils import decorators, flag, scoreboard
from ctferror import *
from datetime import datetime
import config

api = Blueprint("api", "api", url_prefix="/api")
@api.route("/submit/<int:challenge>.json", methods=["POST"])
@decorators.must_be_allowed_to("solve challenges")
@decorators.must_be_allowed_to("view challenges")
@decorators.competition_running_required
@decorators.confirmed_email_required
def submit_api(challenge):
    chal = Challenge.get(Challenge.id == challenge)
    flagval = request.form["flag"]

    code, message = flag.submit_flag(g.team, chal, flagval)
    return jsonify(dict(code=code, message=message))

@api.route("/dismiss/<int:nid>.json", methods=["POST"])
@decorators.login_required
def dismiss_notification(nid):
    n = Notification.get(Notification.id == nid)
    if g.team != n.team:
        code, message = NOTIFICATION_NOT_YOURS
    else:
        Notification.delete().where(Notification.id == nid).execute()
        code, message = SUCCESS
    return jsonify(dict(code=code, message=message))

@api.route("/_ctftime/")
def ctftime_scoreboard_json():
    if not config.immediate_scoreboard and datetime.now() < config.competition_end:
        return "unavailable", 503

    scores = scoreboard.calculate_scores()
    standings = [dict(team=i[2], score=i[4], outward=not i[0]) for i in scores]
    for index, standing in enumerate(standings):
        standing["pos"] = index + 1

    return jsonify(standings=standings)
