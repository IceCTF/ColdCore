from exceptions import ValidationError
from .database import User, UserAccess
from datetime import datetime, timedelta
import utils
import utils.email
import utils.misc


def get_user(username=None, id=None):
    try:
        if username:
            return User.get(User.username == username)
        elif id:
            return User.get(User.id == id)
        else:
            raise ValueError("Invalid call")
    except User.DoesNotExist:
        return None


def login(username, password):
    user = get_user(username=username)
    if not user:
        return False, None

    if(user.check_password(password)):
        UserAccess.create(user=user, ip=utils.misc.get_ip(), time=datetime.now())
        return True, user.id
    return False, None


def validate(username, email, password, background, country, tshirt_size=None, gender=None):
    if not email or "." not in email or "@" not in email:
        raise ValidationError("You must have a valid email!")

    if not utils.email.is_valid_email(email):
        raise ValidationError("You're lying")

    if background not in utils.select.BackgroundKeys:
        raise ValidationError("Invalid Background")

    if country not in utils.select.CountryKeys:
        raise ValidationError("Invalid Background")

    if tshirt_size and (tshirt_size not in utils.select.TShirts):
        raise ValidationError("Invalid T-shirt size")

    if gender and (gender not in ["M", "F"]):
        raise ValidationError("Invalid gender")

    if password is not None:
        if len(password) < 6:
            raise ValidationError("Password is too short.")
    if username is not None:
        if not username or len(username) > 50:
            raise ValidationError("Invalid username")
        if get_user(username=username):
            raise ValidationError("That username has already been taken.")


def create_user(username, email, password, background, country, team, tshirt_size=None, gender=None):
    validate(username, email, password, background, country, tshirt_size=tshirt_size, gender=gender)

    assert team is not None
    confirmation_key = utils.misc.generate_confirmation_key()

    user = User.create(username=username, email=email,
                       background=background, country=country,
                       tshirt_size=tshirt_size, gender=gender,
                       email_confirmation_key=confirmation_key,
                       team=team)
    user.set_password(password)
    user.save()

    UserAccess.create(user=user, ip=utils.misc.get_ip(), time=datetime.now())

    utils.email.send_confirmation_email(email, confirmation_key)

    return user


def confirm_email(current_user, confirmation_key):
    if current_user.email_confirmed:
        raise ValidationError("Email already confirmed")
    if current_user.confirmation_key == confirmation_key:
        current_user.email_confirmed = True
        current_user.save()
    else:
        raise ValidationError("Invalid confirmation key!")


def forgot_password(username):
    user = get_user(username=username)
    if user is None:
        return
    user.password_reset_token = utils.misc.generate_confirmation_key()
    user.password_reset_expired = datetime.now() + timedelta(days=1)
    user.save()
    utils.email.send_password_reset_email(user.email, user.password_reset_token)


def reset_password(token, password):
    if len(password) < 6:
        raise ValidationError("Password is too short!")
    try:
        user = User.get(User.password_reset_token == token)
        if user.password_reset_expired < datetime.now():
            raise ValidationError("Token expired")
        user.set_password(password)
        user.password_reset_token = None
        user.save()
    except User.DoesNotExist:
        raise ValidationError("Invalid reset token!")


def update_user(current_user, username, email, password, background, country, tshirt_size=None, gender=None):
    if username == current_user.username:
        username = None
    if password == "":
        password = None
    validate(username, email, password, background, country, tshirt_size, gender)
    if username:
        current_user.username = username
    if password:
        current_user.set_password(password)
    email_changed = (current_user.email != email)  # send email after saving to db
    if email_changed:
        current_user.email_confirmation_key = utils.misc.generate_confirmation_key()
        current_user.email_confirmed = False
    current_user.email = email
    current_user.background = background
    current_user.country = country
    current_user.tshirt_size = tshirt_size
    current_user.gender = gender
    current_user.save()

    if email_changed:
        utils.email.send_confirmation_email(email, current_user.email_confirmation_key)
        return "Changes saved. Check your email for a new confirmation key."
    else:
        return "Changes saved."
