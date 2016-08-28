from flask import Blueprint, g, render_template

from data import ssh
from utils import decorators


shell = Blueprint("shell", __name__, template_folder="../templates/shell")


@shell.route('/shell/')
@decorators.must_be_allowed_to("access shell")
@decorators.competition_started_required
@decorators.confirmed_email_required
def index():
    account = ssh.get_team_account(g.team)
    return render_template("shell.html", account=account)
