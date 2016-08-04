from data.database import Stage, Challenge, ChallengeSolve, ChallengeFailure, ScoreAdjustment, Team
from datetime import datetime
from exceptions import ValidationError
from flask import g
import config


def get_stages():
    return list(Stage.select().order_by(Stage.name))


def get_stage_challenges(stage_id):
    print(stage_id)
    return list(Challenge.select(Challenge.alias).where(Challenge.stage == stage_id))


def get_categories():
    return [q.category for q in Challenge.select(Challenge.category).distinct().order_by(Challenge.category)]


def get_challenges():
    challenges = Challenge.select().order_by(Challenge.stage, Challenge.points, Challenge.name)
    d = dict()
    for chall in challenges:
        if chall.stage_id in d:
            d[chall.stage_id].append(chall)
        else:
            d[chall.stage_id] = [chall]
    return d


def get_solve_counts():
    # TODO: optimize
    d = dict()
    for k in Challenge.select(Challenge.id):
        d[k.id] = get_solve_count(k.id)
    return d

def get_solve_count(chall_id):
    s = g.redis.hget("solves", chall_id)
    if s is not None:
        return int(s.decode())
    else:
        return -1


def get_challenge(id=None, alias=None):
    try:
        if id is not None:
            return Challenge.get(Challenge.id == id)
        elif alias is not None:
            return Challenge.get(Challenge.alias == alias)
        else:
            raise ValueError("Invalid argument")
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
    elif flag.strip().lower() != chall.flag.strip().lower():
        ChallengeFailure.create(user=user, team=team, challenge=chall, attempt=flag, time=datetime.now())
        return "Incorrect flag"
    else:
        ChallengeSolve.create(user=user, team=team, challenge=chall, time=datetime.now())
        g.redis.hincrby("solves", chall.id, 1)
        if config.immediate_scoreboard:
            g.redis.delete("scoreboard")
            g.redis.delete("graph")
        return "Correct!"
