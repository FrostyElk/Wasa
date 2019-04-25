"""
 Copyright 2019 Frosty Elk AB
 Author: Arne Sikstrom
"""

import secrets


class Config(object):
    """ Global Configuration """

    SESSION_TYPE = 'filesystem'
    DEBUG = True
    BOOTSTRAP_SERVE_LOCAL = False
    SECRET_KEY = secrets.token_urlsafe(24)
