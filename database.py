from peewee import *
db = SqliteDatabase("dev.db")

class BaseModel(Model):
    class Meta:
        database = db

class Team(BaseModel):
    name = CharField()
    email = CharField()
    affiliation = CharField()
    eligible = BooleanField()
    eligibility_locked = BooleanField(default=False)
    first_login = BooleanField(default=True)
    email_confirmed = BooleanField(default=False)
    email_confirmation_key = CharField()
    restricts = TextField(default="")
    key = CharField()

    def solved(self, challenge):
        return ChallengeSolve.select().where(ChallengeSolve.team == self, ChallengeSolve.challenge == challenge).count()

    @property
    def score(self):
        challenge_points = sum([i.challenge.points for i in self.solves])
        adjust_points = sum([i.value for i in self.adjustments])
        return challenge_points + adjust_points

class TeamAccess(BaseModel):
    team = ForeignKeyField(Team, related_name='accesses')
    ip = CharField()
    time = DateTimeField()

class Challenge(BaseModel):
    name = CharField()
    category = CharField()
    author = CharField()
    description = TextField()
    points = IntegerField()
    breakthrough_bonus = IntegerField(default=0)
    enabled = BooleanField(default=True)
    flag = TextField()

class ChallengeSolve(BaseModel):
    team = ForeignKeyField(Team, related_name='solves')
    challenge = ForeignKeyField(Challenge, related_name='solves')
    time = DateTimeField()

    class Meta:
        primary_key = CompositeKey('team', 'challenge')

class ChallengeFailure(BaseModel):
    team = ForeignKeyField(Team, related_name='failures')
    challenge = ForeignKeyField(Challenge, related_name='failures')
    attempt = CharField()
    time = DateTimeField()

class NewsItem(BaseModel):
    summary = CharField()
    description = TextField()

class TroubleTicket(BaseModel):
    team = ForeignKeyField(Team, related_name='tickets')
    summary = CharField()
    description = TextField()
    active = BooleanField(default=True)
    opened_at = DateTimeField()

class TicketComment(BaseModel):
    ticket = ForeignKeyField(TroubleTicket, related_name='comments')
    comment_by = CharField()
    comment = TextField()
    time = DateTimeField()

class Notification(BaseModel):
    team = ForeignKeyField(Team, related_name='notifications')
    notification = TextField()

class ScoreAdjustment(BaseModel):
    team = ForeignKeyField(Team, related_name='adjustments')
    value = IntegerField()
    reason = TextField()

class AdminUser(BaseModel):
    username = CharField()
    password = CharField()
    secret = CharField()
