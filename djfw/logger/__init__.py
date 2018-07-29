import logging
import sys


class DBLogHandler(logging.Handler):
    def emit(self, record):
        if record.name == 'django.db.backends':
            return
        try:
            from djfw.logger.models import LogMessage
            log_message = LogMessage()
            log_message.level = record.levelno
            log_message.create_time = record.created
            log_message.module_name = record.module
            log_message.logger_name = record.name
            try:
                log_message.body = record.message
            except AttributeError:
                log_message.body = record.msg
            log_message.save()
        except:
            (exc_type, exc_value, exc_traceback) = sys.exc_info()
            logging.error(exc_type)
            logging.error(exc_value)
