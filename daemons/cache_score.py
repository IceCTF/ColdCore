import redis
from data import scoreboard
import json
import config
from data.database import db


def run():
    r = redis.StrictRedis(host=config.redis.host, port=config.redis.port, db=config.redis.db)
    db.connect()

    def set_complex(key, val):
        r.set(key, json.dumps(val))
    data = scoreboard.calculate_scores()
    graphdata = scoreboard.calculate_graph(data)
    set_complex("scoreboard", data)
    set_complex("graph", graphdata)
    db.close()
