import logging
from functools import wraps

from config import LIST_ALLOWED_USERS


def restricted(func):
    @wraps(func)
    def wrapped(_, bot, update, *args, **kwargs):
        user_id = update.effective_user.id
        if LIST_ALLOWED_USERS:
          if user_id not in LIST_ALLOWED_USERS:
              logging.error("Unauthorized access denied for {}.".format(user_id))
              return
        return func(_, bot, update, *args, **kwargs)
    return wrapped
