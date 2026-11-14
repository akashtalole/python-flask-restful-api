import factory

from app.factories.base import BaseFactory

from app.models.module import db, Module


class ModuleFactory(BaseFactory):

    class Meta:
        model = Module
        sqlalchemy_session = db.session

    donation_include = True
    ticket_include = True
    payment_include = True
