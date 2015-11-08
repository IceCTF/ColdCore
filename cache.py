from app import app
from flask import g
import redis

@app.before_request
def before_request():
    g.redis = redis.StrictRedis(host='localhost', port=6379, db=0)

@app.teardown_request
def teardown_request(exc):
    cache = getattr(g, 'redis', None)
    if cache is not None:
        cache.connection_pool.close()
