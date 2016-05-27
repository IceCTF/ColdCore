import redis
r = redis.StrictRedis()
import json

def set_complex(key, val):
    r.set(key, json.dumps(val))

import utils
import utils.scoreboard
data = utils.scoreboard.calculate_scores()
graphdata = utils.scoreboard.calculate_graph(data)
set_complex("scoreboard", data)
set_complex("graph", graphdata)
