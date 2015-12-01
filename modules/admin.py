from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from database import AdminUser, Team, Challenge, ChallengeSolve, ChallengeFailure, ScoreAdjustment, TroubleTicket, TicketComment, Notification
import utils
import utils.admin
import utils.scoreboard
from utils.decorators import admin_required, csrf_check
from utils.notification import make_link
from datetime import datetime
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
@admin_required
def admin_dashboard():
    teams = Team.select()
    solves = ChallengeSolve.select(ChallengeSolve, Challenge).join(Challenge)
    adjustments = ScoreAdjustment.select()
    scoredata = utils.scoreboard.get_all_scores(teams, solves, adjustments)
    lastsolvedata = utils.scoreboard.get_last_solves(teams, solves)
    tickets = list(TroubleTicket.select().where(TroubleTicket.active == True))
    return render_template("admin/dashboard.html", teams=teams, scoredata=scoredata, lastsolvedata=lastsolvedata, tickets=tickets)

@admin.route("/tickets/")
@admin_required
def admin_tickets():
    tickets = list(TroubleTicket.select(TroubleTicket, Team).join(Team))
    return render_template("admin/tickets.html", tickets=tickets)

@admin.route("/tickets/<int:ticket>/")
@admin_required
def admin_ticket_detail(ticket):
    ticket = TroubleTicket.get(TroubleTicket.id == ticket)
    comments = list(TicketComment.select().where(TicketComment.ticket == ticket))
    return render_template("admin/ticket_detail.html", ticket=ticket, comments=comments)

@admin.route("/tickets/<int:ticket>/comment/", methods=["POST"])
@admin_required
def admin_ticket_comment(ticket):
    ticket = TroubleTicket.get(TroubleTicket.id == ticket)
    if request.form["comment"]:
        TicketComment.create(ticket=ticket, comment_by=session["admin"], comment=request.form["comment"], time=datetime.now())
        Notification.create(team=ticket.team, notification="A response has been added for {}.".format(make_link("ticket #{}".format(ticket.id), url_for("team_ticket_detail", ticket=ticket.id))))
        flash("Comment added.")

    if ticket.active and "resolved" in request.form:
        ticket.active = False
        ticket.save()
        Notification.create(team=ticket.team, notification="{} has been marked resolved.".format(make_link("Ticket #{}".format(ticket.id), url_for("team_ticket_detail", ticket=ticket.id))))
        flash("Ticket closed.")

    elif not ticket.active and "resolved" not in request.form:
        ticket.active = True
        ticket.save()
        Notification.create(team=ticket.team, notification="{} has been reopened.".format(make_link("Ticket #{}".format(ticket.id), url_for("team_ticket_detail", ticket=ticket.id))))
        flash("Ticket reopened.")

    return redirect(url_for(".admin_ticket_detail", ticket=ticket.id))

@admin.route("/team/<int:tid>/")
@admin_required
def admin_show_team(tid):
    team = Team.get(Team.id == tid)
    return render_template("admin/team.html", team=team)

@admin.route("/team/<int:tid>/<csrf>/impersonate/")
@csrf_check
@admin_required
def admin_impersonate_team(tid):
    session["team_id"] = tid
    return redirect(url_for("scoreboard"))

@admin.route("/team/<int:tid>/<csrf>/toggle_eligibility_lock/")
@csrf_check
@admin_required
def admin_toggle_eligibility_lock(tid):
    team = Team.get(Team.id == tid)
    team.eligibility_locked = not team.eligibility_locked
    team.save()
    flash("Eligibility lock set to {}".format(team.eligibility_locked))
    return redirect(url_for(".admin_show_team", tid=tid))

@admin.route("/logout/")
def admin_logout():
    del session["admin"]
    return redirect(url_for('.admin_login'))
