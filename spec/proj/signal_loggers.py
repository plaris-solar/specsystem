from django.core.signals import request_started
import logging
logger = logging.getLogger('requests')


def callback(sender, environ, **kwargs):
    if not 'PATH_INFO' in environ: # pragma nocover
        return

    log_msg = f'{environ["REQUEST_METHOD"]} {environ["PATH_INFO"]}:'

    if 'HTTP_REFERER' in environ: # pragma nocover
        log_msg += f'   {environ["HTTP_REFERER"]}'
    logger.debug(log_msg)


def log_all_requests():
    request_started.connect(callback)
