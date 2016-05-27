from database import Team, Challenge, ChallengeSolve, ScoreAdjustment
from datetime import datetime

import config

def get_all_scores(teams, solves, adjustments):
    scores = {team.id: 0 for team in teams}
    for solve in solves:
        scores[solve.team_id] += solve.challenge.points

    for adjustment in adjustments:
        scores[adjustment.team_id] += adjustment.value

    return scores

def get_last_solves(teams, solves):
    last = {team.id: datetime(1970, 1, 1) for team in teams}
    for solve in solves:
        if solve.time > last[solve.team_id]:
            last[solve.team_id] = solve.time
    return last

def calculate_scores():
    solves = ChallengeSolve.select(ChallengeSolve, Challenge).join(Challenge)
    adjustments = ScoreAdjustment.select()
    teams = Team.select()

    team_solves = {team.id: [] for team in teams}
    team_mapping = {team.id: team for team in teams}
    scores = {team.id: 0 for team in teams}
    for solve in solves:
        scores[solve.team_id] += solve.challenge.points
        team_solves[solve.team_id].append(solve)
    for adjustment in adjustments:
        scores[adjustment.team_id] += adjustment.value

    most_recent_solve = {tid: max([i.time for i in team_solves[tid]]) for tid in team_solves if team_solves[tid]}
    scores = {i: j for i, j in scores.items() if i in most_recent_solve}
    # eligible, teamid, teamname, affiliation, score
    return [(team_mapping[i[0]].eligible, i[0], team_mapping[i[0]].name, team_mapping[i[0]].affiliation, i[1]) for idx, i in enumerate(sorted(scores.items(), key=lambda k: (-k[1], most_recent_solve[k[0]])))]

def calculate_graph(scoredata):
    solves = list(ChallengeSolve.select(ChallengeSolve, Challenge).join(Challenge).order_by(ChallengeSolve.time))
    adjustments = list(ScoreAdjustment.select())
    scoredata = [i for i in scoredata if i[0]] # Only eligible teams are on the score graph
    graph_data = []
    for eligible, tid, name, affiliation, score in scoredata[:config.teams_on_graph]:
        our_solves = [i for i in solves if i.team_id == tid]
        team_data = []
        s = sum([i.value for i in adjustments if i.team_id == tid])
        for i in sorted(our_solves, key=lambda k: k.time):
            team_data.append((str(i.time), s))
            s += i.challenge.points
            team_data.append((str(i.time), s))
        team_data.append((str(datetime.now()), score))
        graph_data.append((name, team_data))
    return graph_data

