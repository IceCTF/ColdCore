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
    first_login = BooleanField(default=True)
    email_confirmed = BooleanField(default=False)
    email_confirmation_key = CharField()
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
    time = DateField()

class Challenge(BaseModel):
    name = CharField()
    category = CharField()
    description = TextField()
    points = IntegerField()
    flag = CharField()

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

class ChallengeWriteup(BaseModel):
    team = ForeignKeyField(Team, related_name='writeups')
    challenge = ForeignKeyField(Challenge, related_name='writeups')
    text = TextField()

class WriteupRating(BaseModel):
    writeup = ForeignKeyField(ChallengeWriteup, related_name='ratings')
    team = ForeignKeyField(Team, related_name='writeupratings')
    rating = IntegerField()

class ScoreAdjustment(BaseModel):
    team = ForeignKeyField(Team, related_name='adjustments')
    value = IntegerField()
    reason = TextField()

class AdminUser(BaseModel):
    username = CharField()
    password = CharField()
