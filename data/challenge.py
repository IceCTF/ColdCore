from data.database import Challenge, ChallengeSolve, ChallengeFailure, ScoreAdjustment
from datetime import datetime
from exceptions import ValidationError
from flask import g

def get_challenges():
    return Challenge.select().order_by(Challenge.points, Challenge.name)

def get_challenge(id):
    try:
        return Challenge.get(Challenge.id == id)
    except Challenge.DoesNotExist:
        raise ValidationError("Challenge does not exist!")

def get_solved(team):
    return Challenge.select().join(ChallengeSolve).where(ChallengeSolve.team == g.team)

def get_adjustments(team):
    return ScoreAdjustment.select().where(ScoreAdjustment.team == team)

def get_challenge_solves(chall):
    return ChallengeSolve.select(ChallengeSolve, Team).join(Team).order_by(ChallengeSolve.time).where(ChallengeSolve.challenge == chall)

def submit_flag(chall, user, team, flag):
    if team.solved(chall):
        raise ValidationError("Your team has already solved this problem!")
    elif not chall.enabled:
        raise ValidationError("This challenge is disabled.")
    elif flag.strip().lower() != chall.flag.strip.lower():
        ChallengeFailure.create(user=user, team=team, challenge=chall, attempt=flag, time=datetime.now())
        return "Incorrect flag"
    else:
        ChallengeSolve.create(user=user, team=team, challenge=chall, time=datetime.now())
        g.redis.hincrby("solves", challenge.id, 1)
        if config.immediate_scoreboard:
            g.redis.delete("scoreboard")
            g.redis.delete("graph")
        return "Correct!"
