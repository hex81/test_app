# -*- coding:utf-8 -*-
# Create by hex7 at 11/22/18
#

import os

basedir = os.path.abspath(os.path.dirname(__name__))


class Config:

    SECRET_KEY = 'hard to guess string'
    # MAIL_SERVER = 'mailhub.lss.emc.com'
    # MAIL_PORT = 25
    # MAIL_USE_TLS = 'true'
    # FLASKY_MAIL_SUBJECT_PREFIX = '[Flasky]'
    # FLASKY_MAIL_SENDER = 'FLASKY ADMIN <flasky@emc.com>'
    APP_ADMIN = 'hexin0922@hotmail.com'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    RECORD_PER_PAGE = 50

    def __init__(self):
        pass

    @staticmethod
    def init_app(app):
        pass


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:postgres@localhost:5432/postgres'


config = {
    'production': ProductionConfig,
}
