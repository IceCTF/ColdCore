import redis
r = redis.StrictRedis()

def set_complex(key, val, ex):
    r.set(key, json.dumps(val), ex)

import utils
import utils.scoreboard
data = utils.scoreboard.calculate_scores()
graphdata = utils.scoreboard.calculate_graph(data)
utils.scoreboard.set_complex("scoreboard", data, 120)
utils.scoreboard.set_complex("graph", graphdata, 120)
