import redis
r = redis.StrictRedis()
import json

def set_complex(key, val, ex):
    r.set(key, json.dumps(val), ex)

import utils
import utils.scoreboard
data = utils.scoreboard.calculate_scores()
graphdata = utils.scoreboard.calculate_graph(data)
set_complex("scoreboard", data, 120)
set_complex("graph", graphdata, 120)
