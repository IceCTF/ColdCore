from exceptions import ValidationError
from .database import Team
from utils import misc


def get_team(id=None, name=None, key=None):
    try:
        if name:
            return Team.get(Team.name == name)
        elif id:
            return Team.get(Team.id == id)
        elif key:
            return Team.get(Team.key == key)
        else:
            raise ValueError("Invalid call")
    except Team.DoesNotExist:
        return None


def validate(name, affiliation):
    if name is not None:
        if not name or len(name) > 50:
            raise ValidationError("A team name is required.")
        if get_team(name=name):
            raise ValidationError("A team with that name already exists.")


def create_team(name, affiliation):
    if not affiliation:
        affiliation = "No affiliation"
    validate(name, affiliation)

    team_key = misc.generate_team_key()
    team = Team.create(name=name, affiliation=affiliation, key=team_key)

    return True, team


def update_team(current_team, name, affiliation):
    if not affiliation:
        affiliation = "No affiliation"
    if current_team.name == name:
        name = None
    validate(name, affiliation)
    if name:
        current_team.name = name
    current_team.affiliation = affiliation
    current_team.save()
