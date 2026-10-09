from datetime import date, datetime
from decimal import Decimal

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    def to_dict(self) -> dict:
        """Serialize model row to a JSON-safe dict."""
        data = {}
        for column in self.__table__.columns:
            value = getattr(self, column.name)
            if isinstance(value, Decimal):
                value = float(value)
            elif isinstance(value, (datetime, date)):
                value = value.isoformat()
            data[column.name] = value
        return data
