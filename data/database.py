from peewee import PostgresqlDatabase, SqliteDatabase
from peewee import Model, CharField, TextField, IntegerField, BooleanField, DateTimeField, ForeignKeyField, CompositeKey

import bcrypt
import config

if config.production:
    db = PostgresqlDatabase(config.database.database, user=config.database.user, password=config.database.password)
else:
    db = SqliteDatabase("dev.db")


class BaseModel(Model):
    class Meta:
        database = db


class Team(BaseModel):
    name = CharField(unique=True)
    affiliation = CharField(null=True)
    restricts = TextField(default="")
    key = CharField(unique=True, index=True)
    eligibility = BooleanField(null=True)

    def solved(self, challenge):
        return ChallengeSolve.select().where(ChallengeSolve.team == self, ChallengeSolve.challenge == challenge).count()

    def eligible(self):
        if self.eligibility is not None:
            return self.eligibility
        return all([member.eligible() for member in self.members]) and self.members.count() <= 3

    @property
    def score(self):
        challenge_points = sum([i.challenge.points for i in self.solves])
        adjust_points = sum([i.value for i in self.adjustments])
        return challenge_points + adjust_points


class User(BaseModel):
    username = CharField(unique=True, index=True)
    email = CharField(index=True)
    email_confirmed = BooleanField(default=False)
    email_confirmation_key = CharField()
    password = CharField(null=True)
    background = CharField()
    country = CharField()
    tshirt_size = CharField(null=True)
    gender = CharField(null=True)
    first_login = BooleanField(default=True)
    restricts = TextField(default="")
    team = ForeignKeyField(Team, related_name="members")
    banned = BooleanField(default=False)
    password_reset_token = CharField(null=True)
    password_reset_expired = DateTimeField(null=True)

    def set_password(self, pw):
        self.password = bcrypt.hashpw(pw.encode("utf-8"), bcrypt.gensalt())
        return

    def check_password(self, pw):
        return bcrypt.checkpw(pw.encode("utf-8"), self.password.encode("utf-8"))

    def eligible(self):
        return self.country == "ISL" and not self.banned


class UserAccess(BaseModel):
    user = ForeignKeyField(User, related_name='accesses')
    ip = CharField()
    time = DateTimeField()


class Stage(BaseModel):
    name = CharField()
    alias = CharField(unique=True, index=True)
    description = CharField(null=True)


class Challenge(BaseModel):
    name = CharField()
    alias = CharField(unique=True, index=True)
    category = CharField()
    author = CharField()
    description = TextField()
    points = IntegerField()
    breakthrough_bonus = IntegerField(default=0)
    enabled = BooleanField(default=True)
    flag = TextField()
    stage = ForeignKeyField(Stage, related_name='challenges')


class ChallengeSolve(BaseModel):
    user = ForeignKeyField(User, related_name='solves')
    team = ForeignKeyField(Team, related_name='solves')
    challenge = ForeignKeyField(Challenge, related_name='solves')
    time = DateTimeField()

    class Meta:
        primary_key = CompositeKey('team', 'challenge')


class ChallengeFailure(BaseModel):
    user = ForeignKeyField(User, related_name='failures')
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


class SshAccount(BaseModel):
    team = ForeignKeyField(Team, null=True, related_name='ssh_account')
    username = CharField()
    password = CharField()
    hostname = CharField()
    port = IntegerField()
