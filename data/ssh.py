from .database import SshAccount, Team
from peewee import fn

def count_accounts():
    return SshAccount.select().count()

def count_unassigned():
    return SshAccount.select().where(SshAccount.team == None).count()

def get_teams_without_ssh():
    accounts = SshAccount.select(SshAccount.team).where(SshAccount.team.is_null(False))
    return list(Team.select().where(Team.id.not_in(accounts)))

def create_accounts(accounts):
    for account in accounts:
        SshAccount.create(username=account["username"], password=account["password"],
                          hostname=account["hostname"], port=account["port"], team=None)

def assign_shell_account(team):
    acct = SshAccount.select().order_by(fn.Random()).get()
    acct.team = team
    acct.save()
