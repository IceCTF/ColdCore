import redis
from data import scoreboard
import json
import config

r = redis.StrictRedis(host=config.redis.host, port=config.redis.port, db=config.redis.db)

def set_complex(key, val):
    r.set(key, json.dumps(val))


def run():
    data = scoreboard.calculate_scores()
    graphdata = scoreboard.calculate_graph(data)
    set_complex("scoreboard", data)
    set_complex("graph", graphdata)
