# ctf-platform
This is the platform for TJCTF. It's (what I think is) the best of the MITRE,
CTFd, and picoCTF platforms rolled up into a Flask application.

## Installation
You're going to want to edit `config.py`. The variable names should be fairly
self-explanatory.

You should edit line 2 of database.py, unless you want to use SQLite. This uses
Peewee, so you can use any Peewee-supported database.

You can create some problem YAML files that look like this:

```yml
name: Problem Name
category: Binary
description: binary binary binary binary. i love binary
points: 250
flags: "flag{whatever}"
```

Then add them with `./ctftool add-problem problem.yml` and it'll get put in the
database.

Run `python app.py` and you have a server running. You probably want to deploy
it with `gunicorn` or similar, long-term.
