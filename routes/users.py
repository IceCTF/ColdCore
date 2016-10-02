from flask import Blueprint, g, request, render_template, url_for, redirect, session, flash

from data import user, team

from utils import decorators, ratelimit, captcha
import config
import exceptions

users = Blueprint("users", __name__, template_folder="../templates/users")


@users.route('/login/', methods=["GET", "POST"])
@ratelimit.ratelimit(limit=6, per=120)
def login():
    if request.method == "GET":
        return render_template("login.html")
    elif request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        success, id = user.login(username, password)
        if success:
            session["user_id"] = id
            flash("Login successful.")
            return redirect(url_for('teams.dashboard'))
        else:
            flash("Incorrect username or password", "error")
            return redirect(url_for('.login'))


@users.route('/register/', methods=["GET", "POST"])
@ratelimit.ratelimit(limit=6, per=120)
def register():
    if not config.registration:
        if "admin" in session and session["admin"]:
            pass
        else:
            return "Registration is currently disabled. Email icectf@icec.tf to create an account."

    if request.method == "GET":
        return render_template("register.html")
    elif request.method == "POST":
        try:
            captcha.verify_captcha()
        except exceptions.CaptchaError as e:
            flash(str(e))
            return redirect(url_for(".register"))

        username = request.form["username"].strip()
        user_email = request.form["email"].strip()
        password = request.form["password"].strip()
        confirm_password = request.form["confirm_password"].strip()
        background = request.form["background"].strip()
        country = request.form["country"].strip()

        tshirt_size = ""
        gender = ""
        if "tshirt_size" in request.form.keys():
            tshirt_size = request.form["tshirt_size"].strip()
        if "gender" in request.form.keys():
            gender = request.form["gender"].strip()

        if password != confirm_password:
            flash("Passwords do not match!")
            return redirect(url_for('.register'))

        join_team = bool(int(request.form["join_team"].strip()))
        if join_team:
            team_key = request.form["team_key"].strip()
            t = team.get_team(key=team_key)
            if not t:
                flash("This team could not be found, check your team key.")
                return redirect(url_for('.register'))
        else:
            team_name = request.form["team_name"].strip()
            team_affiliation = request.form["team_affiliation"].strip()
            try:
                t = team.create_team(team_name, team_affiliation)
            except exceptions.ValidationError as e:
                flash(str(e))
                return redirect(url_for('.register'))

        # note: this is technically a race condition, the team can exist without a user but w/e
        # the team keys are impossible to predict
        try:
            u = user.create_user(username, user_email,
                                 password, background,
                                 country, t,
                                 tshirt_size=tshirt_size, gender=gender)
        except exceptions.ValidationError as e:
            if not join_team:
                t.delete_instance()
            flash(str(e))
            return redirect(url_for('.register'))
        session["user_id"] = u.id
        flash("Registration finished")
        return redirect(url_for('.dashboard'))


@users.route('/logout/')
def logout():
    session.pop("user_id")
    flash("You've successfully logged out.")
    return redirect(url_for('.login'))


@users.route('/confirm_email/<confirmation_key>', methods=["GET"])
@decorators.login_required
def confirm_email(confirmation_key):
    try:
        user.confirm_email(g.user, confirmation_key)
        flash("Email confirmed!")
    except exceptions.ValidationError as e:
        flash(str(e))
    return redirect(url_for('.dashboard'))


@users.route('/forgot_password/', methods=["GET", "POST"])
@ratelimit.ratelimit(limit=6, per=120)
def forgot_password():
    if request.method == "GET":
        return render_template("forgot_password.html")
    elif request.method == "POST":
        username = request.form["username"].strip()
        if len(username) > 50 or not username:
            flash("You must have a username!")
            return redirect(url_for('.forgot_password'))
        user.forgot_password(username=username)
        flash("Forgot password email sent! Check your email.")
        return render_template("forgot_password.html")


@users.route('/reset_password/<password_reset_token>', methods=["GET", "POST"])
@ratelimit.ratelimit(limit=6, per=120)
def reset_password(password_reset_token):
    if request.method == "GET":
        return render_template("reset_password.html")
    elif request.method == "POST":
        password = request.form["password"].strip()
        confirm_password = request.form["confirm_password"].strip()

        if not password == confirm_password:
            flash("Password does not match")
            return render_template("reset_password.html", password_reset_token=password_reset_token)

        try:
            user.reset_password(password_reset_token, password)
            flash("Password successfully reset")
            return redirect(url_for(".login"))
        except exceptions.ValidationError as e:
            flash(str(e))
            return redirect(url_for(".reset_password", password_reset_token=password_reset_token))


@users.route('/user/', methods=["GET", "POST"])
@decorators.login_required
@ratelimit.ratelimit(limit=6, per=120)
def dashboard():
    if request.method == "GET":
        first_login = False
        if g.user.first_login:
            first_login = True
            g.user.first_login = False
            g.user.save()
        return render_template("user.html", first_login=first_login)
    elif request.method == "POST":
        username = request.form["username"].strip()
        email = request.form["email"].strip()
        password = request.form["password"].strip()
        confirm_password = request.form["confirm_password"].strip()
        background = request.form["background"].strip()
        country = request.form["country"].strip()

        tshirt_size = ""
        gender = ""
        if "tshirt_size" in request.form.keys():
            tshirt_size = request.form["tshirt_size"].strip()
        if "gender" in request.form.keys():
            gender = request.form["gender"].strip()

        if password != "":
            if password != confirm_password:
                flash("Password does not match confirmation")
                return redirect(url_for('.dashboard'))

        try:
            msg = user.update_user(g.user, username, email, password, background, country, tshirt_size, gender)
            flash(msg)
        except exceptions.ValidationError as e:
            flash(str(e))
        return redirect(url_for('.dashboard'))
