import factory

from app.factories.base import BaseFactory

import app.factories.common as common
from app.models.role import db, Role


class RoleFactory(BaseFactory):
    class Meta:
        model = Role
        sqlalchemy_session = db.session

    name = common.string_
    title_name = common.string_
