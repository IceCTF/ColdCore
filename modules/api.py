from flask import Blueprint, jsonify, g, request
from database import Challenge
from utils import decorators, flag

api = Blueprint("api", "api", url_prefix="/api")
@api.route("/submit/<int:challenge>.json", methods=["POST"])
@decorators.competition_running_required
@decorators.confirmed_email_required
def submit_api(challenge):
    chal = Challenge.get(Challenge.id == challenge)
    flagval = request.form["flag"]

    code, message = flag.submit_flag(g.team, chal, flagval)
    return jsonify(dict(code=code, message=message))
