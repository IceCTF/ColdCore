import redis
import data.scoreboard
import json

r = redis.StrictRedis()

def set_complex(key, val):
    r.set(key, json.dumps(val))


def run():
    data = data.scoreboard.calculate_scores()
    graphdata = utils.scoreboard.calculate_graph(data)
    set_complex("scoreboard", data)
    set_complex("graph", graphdata)
