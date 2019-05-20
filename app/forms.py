"""
 Copyright 2019 Frosty Elk AB
 Author: Arne Sikstrom
"""

from flask_wtf import FlaskForm
from wtforms.fields import *
from wtforms.validators import DataRequired


class RconAuthForm(FlaskForm):
    ip_address = StringField(u'Server IP Address', validators=[DataRequired()], default='')
    rcon_port = IntegerField(u'RCON Port', validators=[DataRequired()], default=27888)
    password = StringField(u'RCON Password', validators=[DataRequired()], default='')

    submit = SubmitField(u'Connect')


class RconCmdInput(FlaskForm):
    submit_rcon_cmd = SubmitField(u'Send Command')
    cmd_line = StringField()


class RefreshServerInfo(FlaskForm):
    refresh_server_submit = SubmitField(u'Refresh Server Info')


class MatchActionButtons(FlaskForm):
    submit_restart_match = SubmitField(u'Restart Game')
    submit_kick_all_bots = SubmitField(u'Kick All Bots')
    submit_list_players = SubmitField(u'List Players')
    submit_list_bans = SubmitField(u'List Bans')


class StatsForm(FlaskForm):
    submit_query = SubmitField(u'Update Server Stats')
