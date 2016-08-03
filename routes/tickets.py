from flask import Blueprint, g, request, render_template, redirect, url_for, flash

from utils import decorators, ratelimit

from data import ticket

import exceptions

tickets = Blueprint("tickets", __name__, template_folder="../templates/tickets")
# Trouble tickets


@tickets.route('/tickets/')
@decorators.must_be_allowed_to("view tickets")
@decorators.login_required
def index():
    return render_template("tickets.html", tickets=list(ticket.get_tickets(g.team)))


@tickets.route('/tickets/new/', methods=["GET", "POST"])
@decorators.must_be_allowed_to("submit tickets")
@decorators.must_be_allowed_to("view tickets")
@decorators.login_required
@ratelimit.ratelimit(limit=1, per=120)
def open_ticket():
    if request.method == "GET":
        return render_template("open_ticket.html")
    elif request.method == "POST":
        summary = request.form["summary"]
        description = request.form["description"]
        t = ticket.create_ticket(g.team, summary, description)
        flash("Ticket #{} opened.".format(t.id))
        return redirect(url_for(".detail", ticket=t.id))


@tickets.route('/tickets/<int:ticket>/')
@decorators.must_be_allowed_to("view tickets")
@decorators.login_required
def detail(ticket):
    try:
        ticket = ticket.get_ticket(g.team, ticket)
    except exceptions.ValidationError as e:
        flash(str(e))
        return redirect(url_for(".index"))

    comments = ticket.get_comments(ticket)
    return render_template("ticket_detail.html", ticket=ticket, comments=comments)


@tickets.route('/tickets/<int:ticket>/comment/', methods=["POST"])
@decorators.must_be_allowed_to("comment on tickets")
@decorators.must_be_allowed_to("view tickets")
@ratelimit.ratelimit(limit=1, per=120)
def comment(ticket):
    try:
        ticket = ticket.get_ticket(g.team, ticket)
    except exceptions.ValidationError as e:
        flash(str(e))
        return redirect(url_for(".index"))

    if request.form["comment"]:
        ticket.create_comment(ticket, g.user, request.form["comment"])
        flash("Comment added.")

    if ticket.active and "resolved" in request.form:
        ticket.close_ticket(ticket)
        flash("Ticket closed.")

    elif not ticket.active and "resolved" not in request.form:
        ticket.open_ticket(ticket)
        flash("Ticket re-opened.")

    return redirect(url_for(".detail", ticket=ticket.id))
