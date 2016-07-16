import config
import requests

def send_email(to, subject, text):
    return requests.post("{}/messages".format(config.secret.mailgun_url), {"from": config.mail_from, "to": to, "subject": subject, "text": text}, auth=("api", config.secret.mailgun_key))


def send_confirmation_email(team_email, confirmation_key):
    send_email(team_email, "Welcome to {}!".format(config.ctf_name),
"""Hello, and thanks for registering for {}! Before you can start solving problems,
you must confirm your email by clicking the link below:
https://play.icec.tf/confirm_email/{}

Once you've done that, your account will be enabled, and you will be able to access
the challenges. If you have any trouble, feel free to contact an organizer!

If you didn't register an account, then you can disregard this email.
""".format(config.ctf_name, confirmation_key))

def is_valid_email(email):
    return not email.strip().lower().endswith(config.disallowed_domain)

def send_password_reset_email(team_email, password_reset_token):
    send_email(team_email, "{} Password Reset".format(config.ctf_name),
"""To reset your password click the link below and enter a new password. This link will expire in 24 hours.
https://play.icec.tf/reset_password/{}

If you didn't request this email, then you can disregard it.
""".format(password_reset_token))
