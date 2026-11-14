import os

from app.api.helpers.db import save_to_db
from app.models.event import Event, get_new_event_identifier
import click
from flask.cli import FlaskGroup

from app import current_app as app
from app.models import db
from app.models.speaker import Speaker
from populate_db import populate
from flask_migrate import stamp
from sqlalchemy import inspect as sa_inspect

from tests.all.integration.auth_helper import create_super_admin


@click.group(cls=FlaskGroup, create_app=lambda: app)
def manager():
    """Management commands (includes the Flask-Migrate `db` group)."""


@manager.command('list_routes')
def list_routes():
    import urllib.parse

    output = []
    for rule in app.url_map.iter_rules():
        methods = ','.join(rule.methods)
        line = urllib.parse.unquote("{:50s} {:20s} {}".format(
            rule.endpoint, methods, rule))
        output.append(line)

    for line in sorted(output):
        print(line)


@manager.command('add_event_identifier')
def add_event_identifier():
    events = Event.query.all()
    for event in events:
        event.identifier = get_new_event_identifier()
        save_to_db(event)


@manager.command('initialize_db')
@click.option('-c', '--credentials', help='Super admin credentials. Eg. username:password')
def initialize_db(credentials):
    with app.app_context():
        populate_data = True
        inspector = sa_inspect(db.engine)
        table_name = 'events'
        table_names = inspector.get_table_names()
        print("[LOG] Existing tables:")
        print("[LOG] " + ','.join(table_names))
        if table_name not in table_names:
            print("[LOG] Table not found. Attempting creation")
            try:
                db.create_all()
                stamp()
            except Exception:
                populate_data = False
                print("[LOG] Could not create tables. Either database does not exist or tables already created")
            if populate_data:
                credentials = credentials.split(":")
                admin_email = os.environ.get('SUPER_ADMIN_EMAIL', credentials[0])
                admin_password = os.environ.get('SUPER_ADMIN_PASSWORD', credentials[1])
                create_super_admin(admin_email, admin_password)
                populate()
        else:
            print("[LOG] Tables already exist. Skipping data population & creation.")


@manager.command('prepare_kubernetes_db')
@click.option('-c', '--credentials', default='open_event_test_user@fossasia.org:fossasia')
def prepare_kubernetes_db(credentials):
    with app.app_context():
        initialize_db.callback(credentials)


if __name__ == "__main__":
    manager()