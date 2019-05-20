"""
 Copyright 2019 Frosty Elk AB
 Author: Arne Sikstrom
"""

import json

from flask import Blueprint, render_template, flash, redirect, url_for, session, request

from .connection import RconSession, SteamServerData
from .forms import RconAuthForm, RconCmdInput, RefreshServerInfo, MatchActionButtons, StatsForm

frontend = Blueprint('frontend', __name__)


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
    rtok = request.args.get('rtok')
    if not rtok or rtok not in session:
        return redirect(url_for('.rcon_auth'))

    token_session = session[rtok]

    if not token_session or 'rcon_session' not in token_session:
        return redirect(url_for('.rcon_auth'))

    rcon_session = token_session['rcon_session']

    if not rcon_session:
        return redirect(url_for('.rcon_auth'))

    rcom_cmd_line_form = RconCmdInput()
    server_refresh_form = RefreshServerInfo()
    match_action_form = MatchActionButtons()

    if rcom_cmd_line_form.is_submitted() and rcom_cmd_line_form.submit_rcon_cmd.data:
        if token_session['rcon_session'].execute(rcom_cmd_line_form.cmd_line.data):
            token_session['rcon_session'].add_session_cmd_result(token_session)
        else:
            flash('Connection failed to {}:{}'.format(rcon_session.ip_address, rcon_session.rcon_port))
            token_session.pop('rcon_session')
            return redirect(url_for('.rcon_auth'))

    if server_refresh_form.is_submitted() and server_refresh_form.refresh_server_submit.data:
        if rcon_session.execute('status json'):
            token_session['server_info_json'] = json.loads(rcon_session.last_result)
            redir_url = url_for('.rcon') + '?rtok=' + rtok
            return redirect(redir_url)
        else:
            flash('Connection failed to {}:{}'.format(rcon_session.ip_address, rcon_session.rcon_port))
            token_session.pop('rcon_session')
            return redirect(url_for('.rcon_auth'))

    if match_action_form.is_submitted() and match_action_form.submit_restart_match.data:
        if rcon_session.execute('RestartGame'):
            token_session['rcon_session'].add_session_cmd_result(token_session)
        else:
            flash('Connection failed to {}:{}'.format(rcon_session.ip_address, rcon_session.rcon_port))
            token_session.pop('rcon_session')
            return redirect(url_for('.rcon_auth'))

    if match_action_form.is_submitted() and match_action_form.submit_kick_all_bots.data:
        if rcon_session.execute('BotKick'):
            rcon_session.add_session_cmd_result(token_session)
        else:
            flash('Connection failed to {}:{}'.format(rcon_session.ip_address, rcon_session.rcon_port))
            token_session.pop('rcon_session')
            return redirect(url_for('.rcon_auth'))

    if match_action_form.is_submitted() and match_action_form.submit_list_players.data:
        if rcon_session.execute('ListPlayers'):
            rcon_session.add_session_cmd_result(token_session)
        else:
            flash('Connection failed to {}:{}'.format(rcon_session.ip_address, rcon_session.rcon_port))
            token_session.pop('rcon_session')
            return redirect(url_for('.rcon_auth'))

    if match_action_form.is_submitted() and match_action_form.submit_list_bans.data:
        if rcon_session.execute('ListBans'):
            rcon_session.add_session_cmd_result(token_session)
        else:
            flash('Connection failed to {}:{}'.format(rcon_session.ip_address, rcon_session.rcon_port))
            token_session.pop('rcon_session')
            return redirect(url_for('.rcon_auth'))

    return render_template('rcon.html', rcom_cmd_line_form=rcom_cmd_line_form,
                           server_refresh_form=server_refresh_form, match_action_form=match_action_form,
                           session_data=token_session)


@frontend.route('/rcon-auth/', methods=('GET', 'POST'))
def rcon_auth():
    form = RconAuthForm()

    if form.is_submitted():
        rcon_session = RconSession(form.ip_address.data, form.rcon_port.data, form.password.data)

        if rcon_session.execute('status json'):
            rcon_token = rcon_session.rcon_token

            rcon_last_result_json = json.loads(rcon_session.last_result)

            if rcon_last_result_json['success']:
                session[rcon_token] = dict()
                session[rcon_token]['rcon_session'] = rcon_session
                session[rcon_token]['server_info_json'] = rcon_last_result_json
                session[rcon_token]['rcon_cmd_results'] = []
                redir_url = url_for('.rcon') + '?rtok=' + rcon_token
                return redirect(redir_url)
            else:
                session[rcon_token].pop('rcon_session')
                flash('Connection failed to {}:{}. Reason: {}'.format(form.ip_address.data, form.rcon_port.data,
                                                                      session[rcon_token]['server_info_json']['error']))
        else:
            print(rcon_session.last_exception)
            flash('Connection failed to {}:{}'.format(form.ip_address.data, form.rcon_port.data))

    return render_template('rcon-auth.html', form=form)


@frontend.route('/stats/', methods=('GET', 'POST'))
def stats():
    stats_form = StatsForm()

    steam_server_data = SteamServerData()

    if stats_form.is_submitted() and stats_form.submit_query:
        steam_server_data.execute()

    return render_template('stats.html', stats_form=stats_form, stats_data=steam_server_data)
