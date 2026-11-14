# python-flask-restful-api [![Build Status](https://travis-ci.org/akashtalole/python-flask-restful-api.svg?branch=master)](https://travis-ci.org/akashtalole/python-flask-restful-api) [![Coverage Status](https://coveralls.io/repos/github/akashtalole/python-flask-restful-api/badge.svg?branch=master)](https://coveralls.io/github/akashtalole/python-flask-restful-api?branch=master) [![Updates](https://pyup.io/repos/github/akashtalole/python-flask-restful-api/shield.svg)](https://pyup.io/repos/github/akashtalole/python-flask-restful-api/) [![Python 3](https://pyup.io/repos/github/akashtalole/python-flask-restful-api/python-3-shield.svg)](https://pyup.io/repos/github/akashtalole/python-flask-restful-api/) [![CII Best Practices](https://bestpractices.coreinfrastructure.org/projects/3185/badge)](https://bestpractices.coreinfrastructure.org/projects/3185)


Restful Python Flask API

```
python manage.py 
```

## Requirements

* Python 3.12 or newer
* PostgreSQL and Redis

Install the dependencies with `pip install -r requirements/dev.txt` and run the tests with
`pytest tests/all` (set `APP_CONFIG=config.TestingConfig`, `DATABASE_URL` and `TEST_DATABASE_URL` first).
Management commands are available through `python manage.py <command>` (Flask CLI, including
`db upgrade` for migrations and `run` for the development server).

## Configuration notes

* `SECRET_KEY` must be set in the environment (for example `python -c "import secrets; print(secrets.token_urlsafe(32))"`).
  It signs sessions and JWT access/refresh tokens, so every worker / replica must use the same value.
  If it is missing, a random key is generated for each process and tokens will not be valid across processes.
* The settings secret (used to sign e-mail verification / password reset tokens) is generated randomly on first start
  and stored in the database.
* Image/file imports only fetch public `http(s)` URLs; `file://` and addresses of the internal network are refused.

## Security

Dependencies are audited with `pip-audit` and the code with `bandit` on every push and weekly
(see `.github/workflows/ci.yml`). Dependabot keeps the pinned requirements up to date.
