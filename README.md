# Flagbase
This is the platform for TJCTF. It's (what I think is) the best of the MITRE,
CTFd, and picoCTF platforms rolled up into a Flask application.

I'm bad at naming things.

## Installation
You're going to want to edit `config.py`. The variable names should be fairly
self-explanatory.

You're going to want to create a file called `secrets`. It will look like this:

```yml
mailgun_url: https://api.mailgun.net/v3/tjctf.org
mailgun_key: key-asdflkjasdhflkjsdahflkhsdaklfjhasd
recaptcha_key: asdlkfjhasdlkjfhlsdakjfh
recaptcha_secret: sdakjfhsdalkfjhsdalkfjh
key: this can be anything you want, it is your flask secret_key
```

You should edit line 2 of database.py, unless you want to use SQLite. This uses
Peewee, so you can use any Peewee-supported database.

You can create some problem YAML files that look like this:

```yml
name: Problem Name
author: ME!
category: Binary
description: binary binary binary binary. i love binary
points: 250
flags: "flag{whatever}"
```

Then add them with `./ctftool add-challenge problem.yml` and it'll get put in the
database.

Run `python app.py` and you have a server running. You probably want to deploy
it with `gunicorn` or similar, long-term.

## ctftool

You can do some really fancy stuff with `ctftool`. If you have a directory structure
like this:

- ctf-platform
- ctf-problems
    - problem1
        - problem.yml
        - static.yml
    - problem2
        - problem.yml
        - static.yml
    - problem3
        - problem.yml
    - problem4

You can run `./ctftool scan ../ctf-problems/` and get a fully populated database
with information from all the problem.yml files, and automatically generated
static file names, and automatic substitutions for static file links in
problem.yml. More documentation on this to come soon.
