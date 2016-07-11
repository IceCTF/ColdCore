import config
import requests

def send_email(to, subject, text):
    return requests.post("{}/messages".format(config.secret.mailgun_url), {"from": config.mail_from, "to": to, "subject": subject, "text": text}, auth=("api", config.secret.mailgun_key))


# TODO Make a confirmation link
def send_confirmation_email(team_email, confirmation_key):
    send_email(team_email, "Welcome to {}!".format(config.ctf_name),
"""Hello, and thanks for registering for {}! Before you can start solving problems,
you must confirm your email by entering this code into the team dashboard:

{}

Once you've done that, your account will be enabled, and you will be able to access
the challenges. If you have any trouble, feel free to contact an organizer!

If you didn't register an account, then you can disregard this email.
""".format(config.ctf_name, confirmation_key))

def is_valid_email(email):
    return not email.strip().lower().endswith(config.disallowed_domain)
