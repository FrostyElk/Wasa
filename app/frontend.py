"""
 Copyright 2019 Frosty Elk AB
 Author: Arne Sikstrom
"""

import json

from flask import Blueprint, render_template, flash, redirect, url_for, session
from flask_nav.elements import Navbar, View, Subgroup, Link

from .connection import RconSession
from .forms import RconAuthForm, RconCmdInput, RefreshServerInfo, MatchActionButtons
from .nav import nav

frontend = Blueprint('frontend', __name__)

nav.register_element('frontend_top', Navbar(
    View('WarFallen Server Administration', '.index'),
    View('RCON', '.rcon_auth'),
    Subgroup(
        'Links'
        , Link('WarFallen Home', 'https://www.warfallen.com/')
        , Link('WarFallen Steam', 'https://store.steampowered.com/app/672040/WarFallen/')
    )
))


def add_session_result(result):
    split = result.split('\n')

    if 'rcon_cmd_results' not in session:
        session['rcon_cmd_results'] = []

    session['rcon_cmd_results'].extend(split)


@frontend.route('/')
def index():
    return render_template('index.html')


@frontend.route('/rcon/', methods=('GET', 'POST'))
def rcon():
    rcon_session = session['rcon_session']

    if not rcon_session or rcon_session.valid is False:
        return redirect(url_for('.rcon_auth'))

    rcom_cmd_line_form = RconCmdInput()
    server_refresh_form = RefreshServerInfo()
    match_action_form = MatchActionButtons()

    if rcom_cmd_line_form.is_submitted() and rcom_cmd_line_form.submit_rcon_cmd.data:

        if session['rcon_session'].execute(rcom_cmd_line_form.cmd_line.data):
            session['rcon_session'].add_session_cmd_result()
        else:
            flash('Connection failed to {}:{}'.format(rcon_session.ip_address, rcon_session.rcon_port))
            session.pop('rcon_session')
            return redirect(url_for('.rcon_auth'))

    if server_refresh_form.is_submitted() and server_refresh_form.refresh_server_submit.data:

        if rcon_session.execute('status json'):
            session['server_info_json'] = json.loads(rcon_session.last_result)
            return redirect(url_for('.rcon'))
        else:
            flash('Connection failed to {}:{}'.format(rcon_session.ip_address, rcon_session.rcon_port))
            session.pop('rcon_session')
            return redirect(url_for('.rcon_auth'))

    if match_action_form.is_submitted() and match_action_form.submit_restart_match.data:

        if rcon_session.execute('RestartGame'):
            session['rcon_session'].add_session_cmd_result()
        else:
            flash('Connection failed to {}:{}'.format(rcon_session.ip_address, rcon_session.rcon_port))
            session.pop('rcon_session')
            return redirect(url_for('.rcon_auth'))

    if match_action_form.is_submitted() and match_action_form.submit_kick_all_bots.data:

        if rcon_session.execute('BotKick'):
            session['rcon_session'].add_session_cmd_result()
        else:
            flash('Connection failed to {}:{}'.format(rcon_session.ip_address, rcon_session.rcon_port))
            session.pop('rcon_session')
            return redirect(url_for('.rcon_auth'))

    return render_template('rcon.html', rcom_cmd_line_form=rcom_cmd_line_form,
                           server_refresh_form=server_refresh_form, match_action_form=match_action_form)


@frontend.route('/rcon-auth/', methods=('GET', 'POST'))
def rcon_auth():
    form = RconAuthForm()

    if form.is_submitted():
        rcon_session = RconSession(form.ip_address.data, form.rcon_port.data, form.password.data)

        if rcon_session.execute('status json'):
            session['rcon_session'] = rcon_session
            session['server_info_json'] = json.loads(rcon_session.last_result)
            session['rcon_cmd_results'] = []

            if session['server_info_json']['success']:
                return redirect(url_for('.rcon'))
            else:
                session.pop('rcon_session')
                flash('Connection failed to {}:{}. Reason: {}'.format(form.ip_address.data, form.rcon_port.data,
                                                                      session['server_info_json']['error']))
        else:
            print(rcon_session.last_exception)
            flash('Connection failed to {}:{}'.format(form.ip_address.data, form.rcon_port.data))

    return render_template('rcon-auth.html', form=form)
