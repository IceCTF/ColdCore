from data.database import TroubleTicket, TicketComment
from datetime import datetime
from exceptions import ValidationError


def get_tickets(team):
    return team.tickets

def get_ticket(team, id):
    try:
        return TroubleTicket.get(TroubleTicket.id == ticket and TroubleTicket.team == team)
    except TroubleTicket.DoesNotExist:
        raise ValidationError("Ticket not found!")

def get_comments(ticket):
    return TicketComment.select().where(TicketComment.ticket == ticket).order_by(TicketComment.time)

def create_ticket(team, summary, description):
    return TroubleTicket.create(team=g.team, summary=summary, description=description, opened_at=datetime.now())

def create_comment(ticket, user, comment):
    TicketComment.create(ticket=ticket, comment_by=user.username, comment=request.form["comment"], time=datetime.now())

def open_ticket(ticket):
    ticket.active = True
    ticket.save()

def close_ticket(ticket):
    ticket.active = False
    ticket.save()
