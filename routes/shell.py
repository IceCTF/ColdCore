from flask import Blueprint, g, render_template

from data import ssh


shell = Blueprint("shell", __name__, template_folder="../templates/shell")


@shell.route('/shell/')
def index():
    account = ssh.get_team_account(g.team)
    return render_template("shell.html", account=account)
