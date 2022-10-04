#!/usr/bin/env python
# -*- coding:utf-8 _*-
# Create by hex7 at 11/15/18
#

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


class NameForm(FlaskForm):
    name = StringField('What is your name?', validators=[DataRequired()])
    submit = SubmitField('Submit')
