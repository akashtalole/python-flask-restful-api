import factory

from app.factories.base import BaseFactory

import app.factories.common as common
from app.models.panel_permission import db, PanelPermission


class PanelPermissionFactory(BaseFactory):
    class Meta:
        model = PanelPermission
        sqlalchemy_session = db.session

    panel_name = common.string_
    can_access = True
