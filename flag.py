from database import Challenge, ChallengeSolve, ChallengeFailure
from flask import g
from ctferror import *
from datetime import datetime
import config

def submit_flag(team, challenge, flag):
    if g.redis.get("rl{}".format(team.id)):
        return FLAG_SUBMISSION_TOO_FAST

    if team.solved(challenge):
        return FLAG_SUBMITTED_ALREADY
    elif challenge.flag != flag:
        g.redis.set("rl{}".format(team.id), str(datetime.now()), config.flag_rl)
        ChallengeFailure.create(team=team, challenge=challenge, attempt=flag, time=datetime.now())
        return FLAG_INCORRECT
    else:
        ChallengeSolve.create(team=team, challenge=challenge, time=datetime.now())
        return SUCCESS
