import os
from datetime import datetime

production = os.getenv("PRODUCTION", None) is not None
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

ctf_name = "IceCTF"
#IRC Channel
ctf_chat_channel = "#IceCTF"
ctf_home_url = "https://icec.tf"
eligibility = "In order to be eligible for prizes, all members of your team must be Icelandic residents, and you must not have more than three team members."
tagline = "The Icelandic Hacking Competition"

cdn = True
apisubmit = True
registration = True

proxied_ip_header = "X-Forwarded-For"

flag_rl = 5
teams_on_graph = 10

mail_from = "notice@icec.tf"

immediate_scoreboard = False

# IPs that are allowed to confirm teams by posting to /teamconfirm/
# Useful for verifying resumes and use with resume server.
confirm_ip = []

static_prefix = "http://127.0.0.1/static/"
static_dir = "{}/static/".format(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
custom_stylesheet = "css/main.css"

competition_begin = datetime(1970, 1, 1, 0, 0)
competition_end = datetime(2018, 1, 1, 0, 0)

if production:
    competition_begin = datetime(2016, 8, 12, hour=16, minute=0, second=0)
    competition_end = datetime(2016, 8, 26, hour=16, minute=0, second=0)

# Are you using a resume server?
resumes = False
# If yes, where's it hosted? Otherwise, just put None.
resume_server = None

disallowed_domain = "icec.tf"


def competition_is_running():
    return competition_begin < datetime.now() < competition_end

# Don't touch these. Instead, copy secrets.example to secrets and edit that.
import yaml
from collections import namedtuple
with open("secrets") as f:
    _secret = yaml.load(f)
    secret = namedtuple('SecretsDict', _secret.keys())(**_secret)

_redis = {
    'host': 'localhost',
    'port': 6379,
    'db': 0
}

if production:
    with open("database") as f:
        _database = yaml.load(f)
        database = namedtuple('DatabaseDict', _database.keys())(**_database)
    _redis['db'] = 1

redis = namedtuple('RedisDict', _redis.keys())(**_redis)
