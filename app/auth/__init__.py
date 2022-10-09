#!/usr/bin/env python
# -*- coding:utf-8 _*-
"""
@author: Xin He
@contact: hexin0922@hotmail.com
@file: __init__.py.py
@time: 11/23/18 2:35 PM
@desc:

"""

from flask import Blueprint

auth = Blueprint('auth', __name__)

from . import views