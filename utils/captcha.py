from flask import request
from . import misc
from exceptions import CaptchaError

import config
import requests


def verify_captcha():
    if "g-recaptcha-response" not in request.form:
        raise CaptchaError("Captcha not completed!")

    captcha_response = request.form["g-recaptcha-response"]
    verify_data = dict(secret=config.secret.recaptcha_secret, response=captcha_response, remoteip=misc.get_ip())
    result = requests.post("https://www.google.com/recaptcha/api/siteverify", verify_data).json()["success"]
    if not result:
        raise CaptchaError("Captcha Invalid!")

    return True
