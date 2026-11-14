import factory

from app.factories.base import BaseFactory

import app.factories.common as common
from app.models.custom_system_role import db, CustomSysRole


class CustomSysRoleFactory(BaseFactory):
    class Meta:
        model = CustomSysRole
        sqlalchemy_session = db.session

    name = common.string_
