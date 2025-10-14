import logging
from contextvars import ContextVar

# store user id per request

user_id_context = ContextVar("user_id",default="-")

class UserContextFilter(logging.Filter):
    def filter(self, record):
        try:
            record.user_id = user_id_context.get()
        # except Exception as e:
        #     user_id = "-"
        # setattr(record, "user_id", user_id or "-")
        finally:
            return True
    