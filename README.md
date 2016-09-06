# ColdPlatform
This is the platform for IceCTF. It is based off of the platform for TJCTF, (https://github.com/TJCSec/ctf-platform)[https://github.com/TJCSec/ctf-platform]

## Installation
Edit `config.py` to your liking. The variable names should be fairly
self-explanatory.

You're going to want to create a file called `secrets`. It will look like this:

```yml
mailgun_url: https://api.mailgun.net/v3/tjctf.org
mailgun_key: key-asdflkjasdhflkjsdahflkhsdaklfjhasd
recaptcha_key: asdlkfjhasdlkjfhlsdakjfh
recaptcha_secret: sdakjfhsdalkfjhsdalkfjh
key: this can be anything you want, it is your flask secret_key
shell_host: shell
shell_username: shellaccounts
shell_privkey: path to private key used to log in
```

For production, create a file called `database` as well, with the settings
```
host: localhost
database: ctf
user: user
password: password
```

To run the server with production settings, set the environment variable `PRODUCTION=1` before running the server.

You can create some problem YAML files that look like this:

```yml
name: Problem Name
alias: problem alias
author: ME!
category: Binary
description: binary binary binary binary. i love binary
points: 250
flags: "flag{whatever}"
```

Then add them with `./ctftool challenges add problem.yml` and it'll get put in the
database.

Run `python3 app.py` and you have a server running. You probably want to deploy
it with `gunicorn` or similar, long-term.

## ctftool

You can run `./ctftool challenges scan ../ctf-problems/` and get a fully populated database
with information from all the problem.yml files, and automatically generated
static file names, and automatic substitutions for static file links in
problem.yml. More documentation on this to come soon.

## Contributing

There are some missing features in the platform, and if you would like to contribute, feel free to send pull requests!

If you find any issues or would like to send a feature request feel free to create an issue.
