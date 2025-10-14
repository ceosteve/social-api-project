import logging
from logging.config import dictConfig
from app.logging_context import UserContextFilter


def setup_config():
    logging_config={
        "version":1,
        "disable_existing_loggers":False,
        "formatters":{
            "default":{
                "format":"[%(asctime)s] [user=%(user_id)s] %(levelname)s in %(module)s: %(message)s"
            },
            "detailed":{
                "format":"[%(asctime)s] [user=%(user_id)s] %(levelname)s [%(name)s:%(lineno)d] %(message)s"
            }
        },

        "filters":{
            "user-context":{
                "()":UserContextFilter,
            },
        },
        "handlers":{
            "console":{
                "class":"logging.StreamHandler",
                "formatter":"default",
                "filters":["user-context"]
            },

            "file":{
                "class":"logging.handlers.RotatingFileHandler",
                "formatter":"detailed",
                "filename":"logs/app.log",
                "encoding":"utf-8",
                "maxBytes":1048576,
                "backupCount":7,
            },
        },
        "root":{
            "level":"INFO",
            "handlers":["console", "file"]
        },
        
    }

    dictConfig(logging_config)
    return logging.getLogger("socialapi")