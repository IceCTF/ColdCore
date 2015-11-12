ctf_name = "TJCTF"
eligibility = "In order to be eligible for prizes, all members of your team must be in high school, and you must not have more than four team members."
tagline = "a cybersecurity competition created by TJHSST students"
competition_is_running = True
cdn = True
apisubmit = True
proxied_ip_header = "X-Forwarded-For"
flag_rl = 10
teams_on_graph = 10
mail_from = "tjctf@sandbox1431.mailgun.org"

# Don't touch these. Instead, copy secrets.example to secrets and edit that.
import yaml
from collections import namedtuple
with open("secrets") as f:
    _secret = yaml.load(f)
    secret = namedtuple('SecretsDict', _secret.keys())(**_secret)
