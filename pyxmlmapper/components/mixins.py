import logging

from .common import Default

logger = logging.getLogger(__name__)


class TypeCastMixin:
    @staticmethod
    def convert(_type, value):
        try:
            if isinstance(value, Default):
                return value.value
            return _type(value)
        except Exception as err:
            logger.critical(err)
            raise TypeError(err)
