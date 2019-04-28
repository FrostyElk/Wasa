"""
 Copyright 2019 Frosty Elk AB
 Author: Arne Sikstrom
"""

import secrets


class Config(object):
    """ Global Configuration """

    SESSION_TYPE = 'filesystem'
    DEBUG = True
    SECRET_KEY = secrets.token_urlsafe(24)
