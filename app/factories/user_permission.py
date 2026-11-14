import factory

from app.factories.base import BaseFactory

import app.factories.common as common
from app.models.user_permission import db, UserPermission


class UserPermissionFactory(BaseFactory):
    class Meta:
        model = UserPermission
        sqlalchemy_session = db.session

    name = common.string_
    description = common.string_

    unverified_user = True
    anonymous_user = True
