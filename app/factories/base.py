import factory

from app.models import db


class BaseFactory(factory.alchemy.SQLAlchemyModelFactory):
    """
    Base for all model factories.

    Factories reference related rows by id (e.g. `event_id = 1`) and create the related
    object afterwards through a `RelatedFactory`. Autoflush is therefore disabled while an
    object is generated, so that nothing is flushed before the related row exists. The whole
    unit of work is flushed in dependency order when the caller saves/commits.
    """

    class Meta:
        abstract = True

    @classmethod
    def _generate(cls, strategy, params):
        with db.session.no_autoflush:
            return super()._generate(strategy, params)
