import json
from flask import g

def get_complex(key):
    i = g.redis.get(key)
    if i is None:
        return None
    return json.loads(i.decode())

def set_complex(key, val, ex):
    g.redis.set(key, json.dumps(val), ex)
