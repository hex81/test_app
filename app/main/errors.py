# uncompyle6 version 3.2.4
# Python bytecode 2.7 (62211)
# Decompiled from: Python 2.7.15rc1 (default, Nov 12 2018, 14:31:15) 
# [GCC 7.3.0]
# Embedded file name: /home/hex7/PycharmProjects/flask_learn/app/main/errors.py
# Compiled at: 2018-11-27 17:35:18
from flask import render_template
from . import main

@main.errorhandler(403)
def page_not_found(e):
    return (
     render_template('403.html'), 403)


@main.errorhandler(404)
def page_not_found(e):
    return (
     render_template('404.html'), 404)


@main.errorhandler(500)
def internal_server_error(e):
    return (
     render_template('500.html'), 500)
# okay decompiling errors.pyc
