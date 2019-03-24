"""Flask MIME JSON encoder and decoder supporting ISO8601 date/time format."""

__all__ = 'JsonIso8601MimeEncoder'.split()

from . import MimeEncoders
from datetime import date, time

try:
    MimeEncoders.json
except AttributeError:
    from . import json

class JsonIso8601MimeEncoder(MimeEncoders.json):
    """Flask MIME JSON encoder and decoder supporting ISO8601 date/time format."""

    class JSONEncoder(MimeEncoders.json.JSONEncoder):
        """JSON encoder supporting ISO8601 date/time format."""
        def default(self, value):
            if isinstance(value, (date, time)):
                return value.isoformat()
            return super(JsonIso8601MimeEncoder.JSONEncoder, self).default(value)

MimeEncoders.json_iso8601 = JsonIso8601MimeEncoder
