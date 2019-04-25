"""
 Copyright 2019 Frosty Elk AB
 Author: Arne Sikstrom
"""

import json
import secrets
import socket

from valve.rcon import RCONError, RCON


class RconSession(object):
    """ Session Data"""

    def __init__(self, ip_address=None, rcon_port=None, password=None):
        self.ip_address = ip_address
        self.rcon_port = rcon_port
        self.password = password
        self.last_result = ''
        self.last_command = ''
        self.last_exception = ''
        self.valid = False
        self.rcon_token = self.ip_address + '_' + str(self.rcon_port) + '_' + secrets.token_urlsafe(16)

    def execute(self, command):
        rcon_connection = RCON((self.ip_address, self.rcon_port), self.password)
        try:
            rcon_connection.connect()
            rcon_connection.authenticate()
            self.last_result = rcon_connection(command)
            self.last_command = command
            rcon_connection.close()
            self.valid = True
            return True
        except (RCONError, ConnectionRefusedError, TimeoutError, socket.gaierror)as e:
            self.last_exception = e
            rcon_connection.close()
            self.valid = False
            return False

    def add_session_cmd_result(self, token_session):
        split_result = self.last_result.split('\n')
        command = 'RCON> ' + self.last_command

        if 'rcon_cmd_results' not in token_session:
            token_session['rcon_cmd_results'] = []

        token_session['rcon_cmd_results'].append(command)
        token_session['rcon_cmd_results'].extend(split_result)


class ServerConnection(object):
    """ An Rcon Connection to Warfallen servers"""

    def __init__(self, ip_address=None, rcon_port=None, password=None):
        self.ip_address = ip_address
        self.rcon_port = rcon_port
        self.password = password
        self.rcon_connection = None
        self.last_result = ''
        self.last_result_json = None
        self.last_command = ''
        self.last_exception = None
        self.results = []

    def connect(self, ip_address, rcon_port, password):
        self.ip_address = ip_address
        self.rcon_port = rcon_port
        self.password = password
        self.rcon_connection = RCON((self.ip_address, self.rcon_port), self.password)

        try:
            self.rcon_connection.connect()
            self.rcon_connection.authenticate()
        except (RCONError, ConnectionRefusedError)as e:
            self.last_exception = str(e)
            self.close()

    def is_connected(self):
        if self.rcon_connection is None:
            return False
        else:
            return self.rcon_connection.connected and self.rcon_connection.authenticated

    def execute(self, command):
        self.last_command = command

        try:
            self.last_result = self.rcon_connection(command)
            split = self.last_result.split('\n')
            self.results.extend(split)
        except (RCONError, ConnectionResetError) as e:
            self.last_exception = str(e)
            self.last_result = ''
            self.close()

        return self.last_result

    def execute_json(self, command):
        """ Parse result as JSON"""
        self.last_command = command

        try:
            result = self.rcon_connection(command)
            self.last_result_json = json.loads(result)

        except (RCONError, ConnectionResetError) as e:
            self.last_exception = e
            self.last_result = ''
            self.last_result_json = {}
            self.close()

        return self.last_result_json

    def close(self):
        return self.rcon_connection.close()

    def get_last_result(self):
        return self.last_result

    def get_results(self):
        return self.results

    def get_last_command(self):
        return self.last_command
