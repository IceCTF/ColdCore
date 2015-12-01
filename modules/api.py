from flask import Blueprint, jsonify, g, request
from database import Challenge, Notification
from utils import decorators, flag
from ctferror import *

api = Blueprint("api", "api", url_prefix="/api")
@api.route("/submit/<int:challenge>.json", methods=["POST"])
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

    Notification.delete().where(Notification.id == nid).execute()
    code, message = SUCCESS
    return jsonify(dict(code=code, message=message))
