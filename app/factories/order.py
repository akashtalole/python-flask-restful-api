import factory

from app.factories.base import BaseFactory

from app.factories.event import EventFactoryBasic
from app.models.order import Order
from app.models.ticket import db


class OrderFactory(BaseFactory):
    class Meta:
        model = Order
        sqlalchemy_session = db.session

    event = factory.RelatedFactory(EventFactoryBasic)
    event_id = 1
    payment_mode = 'free'
    status = 'initializing'
