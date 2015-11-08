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

class ChallengeFailure(BaseModel):
    team = ForeignKeyField(Team, related_name='failures')
    challenge = ForeignKeyField(Challenge, related_name='failures')
    attempt = CharField()
    time = DateTimeField()

class ScoreAdjustment(BaseModel):
    team = ForeignKeyField(Team, related_name='adjustments')
    value = IntegerField()
    reason = TextField()
