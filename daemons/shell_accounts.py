import spur
import random
import config
from data.database import db
from data import ssh
import utils.misc


def run():
    db.connect()

    try:
        shell = spur.SshShell(
            hostname=config.secrets.shell_host,
            username=config.secrets.shell_username,
            private_key_file=config.secrets.shell_privkey,
            port=config.shell_port,
            missing_host_key=spur.ssh.MissingHostKey.accept
        )

        result = shell.run(["sudo", "useradd", "--help"])

        if result.return_code != 0:
            raise ValueError("Unable to sudo useradd.")

        account_count = ssh.count_accounts()
        if account_count >= config.shell_max_accounts:
            raise ValueError("Max SSH accounts already created!")

        free_account_count = ssh.count_unassigned()

        new_accounts = max(config.shell_free_acounts - free_account_count, 0)

        print("Checking that all teams have been assigned accounts...")

        print("{}/{} shell accounts allocated adding {}...".format(free_account_count, account_count, new_accounts))
        teams = ssh.get_teams_without_ssh()

        if len(teams) > 0:
            print("{} teams without accounts present! Adding these as well.".format(len(teams)))
            new_accounts += len(teams)

        accounts = []
        while new_accounts > 0:
            username = random.choice(config.shell_user_prefixes) + \
                str(random.randint(0, config.shell_max_accounts))

            plaintext_password = utils.misc.generate_random_string(config.shell_password_length, allowed_chars="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ123456789")

            hashed_password = shell.run(["bash", "-c", "echo '{}' | openssl passwd -1 -stdin".format(plaintext_password)])
            hashed_password = hashed_password.output.decode("utf-8").strip()

            shell_cmd = config.shell_user_creation.format(username=username, password=hashed_password)

            result = shell.run(shell_cmd.split(), allow_error=True)

            if result.return_code == 9:
                print("Collision! Retrying.")
                continue
            elif result.return_code != 0:
                raise RuntimeError(result.stderr)

            print("\t{}:{}".format(username, plaintext_password))

            account = {
                "username": username,
                "password": plaintext_password,
                "hostname": config.shell_host,
                "port": config.shell_port
            }

            accounts.append(account)

            new_accounts -= 1

        if len(accounts) > 0:
            ssh.insert_accounts(accounts)
            print("Successfully imported accounts.")

        for team in teams:
            ssh.assign_shell_account(team)

    except spur.ssh.ConnectionError:
        raise RuntimeError("Could not connect to shell server.")
    db.close()
