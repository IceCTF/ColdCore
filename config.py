import os
from datetime import datetime

production = os.getenv("PRODUCTION", None) is not None
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

ctf_name = "IceCTF"
eligibility = "In order to be eligible for prizes, all members of your team must be Icelandic residents, and you must not have more than three team members."
tagline = "The Icelandic Hacking Competition"
# IRC Channel
ctf_chat_channel = "#IceCTF"
ctf_home_url = "https://icec.tf"

# Serve javascript libraries from CDN
cdn = True
# Allow users to submit via an api?
apisubmit = True
# Allow registration?
registration = True
# If running behind proxy (nginx), which header contains the real IP
proxied_ip_header = "X-Forwarded-For"
# How many teams to show on the scoreboard graph
teams_on_graph = 10

# Which email to send out notifications from
mail_from = "notice@icec.tf"

# Wether to render the scoreboard on request or cache
immediate_scoreboard = False

# Banned email domains
disallowed_domain = "icec.tf"

# Where the static stuff is stored
static_prefix = "/problem-static/"
static_dir = "{}/problem_static/".format(os.path.dirname(os.path.abspath(__file__)))
custom_stylesheet = "css/main.css"

# Shell accounts?

enable_shell = True

shell_port = 22
shell_host = "shell.icec.tf"

shell_user_prefixes = ["ctf-"]
shell_password_length = 6
shell_free_acounts = 10
shell_max_accounts = 99999

shell_user_creation = "sudo useradd -m {username} -p {password} -g ctf -b /home_users"


# when the competition begins
competition_begin = datetime(1970, 1, 1, 0, 0)
competition_end = datetime(2018, 1, 1, 0, 0)

if production:
    competition_begin = datetime(2016, 8, 12, hour=16, minute=0, second=0)
    competition_end = datetime(2016, 8, 26, hour=16, minute=0, second=0)


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
