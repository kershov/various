#!/usr/bin/env python
# -*- coding: utf-8 -*-

#    _____  ._______  ___ __________
#   /     \ |   \   \/  / \______   \_____ _______  ______ ___________
#  /  \ /  \|   |\     /   |     ___/\__  \\_  __ \/  ___// __ \_  __ \
# /    Y    \   |/     \   |    |     / __ \|  | \/\___ \\  ___/|  | \/
# \____|__  /___/___/\  \  |____|    (____  /__|  /____  >\___  >__|
#         \/          \_/                 \/           \/     \/

'''
MIX Parser
~~~~~~~~~~

The script connects to the MIIIX.org website and:
1. Authenticates with given credentials.
2. Initiates generation of a file from one of the the two given categories.
   The categories are: Tyres, Rims.
3. Waits until generation is finished.
4. Downloads generated file and saves it at the given path.
5. Optionally uploads downloaded files to a client's FTP-server.
6. Logs all its actions to the system's stdin and log-file.


How to Run:
    $ env "MIX_USR={login_name}" "MIX_PWD={password}" {path_to_python} {path_to_script}

    where:
        {login_name}        - your login at MIIIX.org
        {password}          - your password at MIIIX.org
        {path_to_python}    - path to your python binary, e.g. /usr/bin/python
        {path_to_script}    - path to this script, e.g. /usr/local/bin/tyres-n-rims.py

    If env-vars with login & password aren't set, the default ones will be used.


~~~~~~~~~~

MIT License

Copyright (c) 2018 Konstantin Ershov (konstantin.ershov@gmail.com)

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''

import os, sys
import requests, json
from datetime import datetime
import logging, logging.handlers
from ftplib import FTP


class MIIIX_Parser():

    ### SETTINGS ###
    MIIIX_ORG = 'http://miiix.org'
    # Get login & password from OS env-variables
    USER_LOGIN = os.environ.get('MIX_USR') or '_login_'
    USER_PASSWORD = os.environ.get('MIX_PWD') or '_password_'

    # Set timeout
    TIMEOUT = 3600 # 1h

    # Paths
    DOWNLOADS = '/var/www/www-root/data/www/baza-koles.ru/MIIIX/'
    LOG_FILE = os.path.join(DOWNLOADS, 'tyres-n-rims.log')

    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36',
    }
    ### SETTINGS: END

    def __init__(self, url=MIIIX_ORG, login=USER_LOGIN, password=USER_PASSWORD, timeout=TIMEOUT):
        self.url = url
        self.login = login
        self.password = password
        self.login_url = self.url + '/login'
        self.protected_url = self.url + '/storage/export'
        self.api_url = self.protected_url + '/do'
        self.timeout = timeout

        # tyres@id = 1 (processed up to 30 mins, 15MB)
        # rims@id =2 (processed around 30 sec, 1.5MB)
        self.export_categories = {
            'tyres': 1,
            'rims': 2,
        }

        self.login_payload = {
            'LoginForm[login]': self.login,
            'LoginForm[passwd]': self.password,
        }

        # FTP Settings
        #    To be filled in if needed!
        self.ftp_settings = {
            'host': '_NA_',
            'user': '_NA_',
            'passwd': '_NA_',
        }
        self.ftp_settings_upload_dir = '_NA_'


    def run(self):
        # Init Logger
        self.init_logger(logfile=self.LOG_FILE, level=logging.INFO, console_enabled=True)

        self.logger.info('Script started...')
        # Ensure the session context is closed after use
        with requests.Session() as session:
            self.logger.info('Trying to authenticate...')

            response = self.send_request(session.post, self.login_url, headers=self.HEADERS, data=self.login_payload, disable_log=True)
            if response.ok:
                self.logger.info('Successfully authenticated and logged in!')
                # Export all the export categories
                for category_id in self.export_categories.values():
                    payload = self.set_export_payload(category_id)
                    # Generate & download files
                    self.run_export(session, payload)
            else:
                self.die("Can't login. Status code: {}".format(response.status_code))

        self.logger.info('Script finished successfully!')


    def run_export(self, session, api_payload):
        api_specific_headers = {
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'X-Requested-With': 'XMLHttpRequest',
        }

        # Extend headers with API-specific ones
        api_headers = dict(self.HEADERS, **api_specific_headers)

        self.logger.info('Sending API-request... It will take some time (up to 30 mins) to get a response.')
        api_response = self.send_request(session.post, self.api_url, headers=api_headers, data=api_payload, timeout=self.timeout)
        try:
            json = api_response.json()
        except ValueError:
            self.die('No JSON object could be decoded. Status code: {}'.format(api_response.status_code))

        if api_response.ok and json['err'] == False:
            self.logger.info('Valid API-response recieved. File generated successfully!')
            # Download generated file
            self.save_file_from_json(json, session)
        else:
            self.die('Failed to POST data! Status code: {}'.format(api_response.status_code))


    def save_file_from_json(self, json, session):
        remote_file = json['obj']['file']
        file_url = self.url + remote_file
        file_remote_name = remote_file.split('/')[-1]
        file_created_at = datetime.strptime(json['obj']['created_at'], '%Y-%m-%d %H:%M:%S')
        file_prefix = file_created_at.strftime('%Y%m%dT%H%M%S_')
        file_name = self.DOWNLOADS + file_prefix + file_remote_name

        self.logger.info('Downloading \'{}\' from \'{}\'...'.format(file_remote_name, file_url))

        response = self.send_request(session.get, file_url)
        if response.ok:
            with open(file_name, 'wb') as f:
                result = f.write(response.content)

            self.logger.info('File \'{}\' was succesfully downloaded and saved as \'{}\' ({} bytes were written)!'.format(file_remote_name, file_name, len(response.content)))

            # Upload files to FTP-server. Won't be run if enabled=False
            self.ftp_upload(file_name, enabled=False)

        else:
            self.die('File download failed. Status code: {}'.format(response.status_code))


    def set_export_payload(self, storage_category):
        '''
        @storage_category - sets the storage_category_id variable

        Valid options are:
            1: tyres
            2: rims
        '''
        if storage_category in [1, 2]:
            return {
                'format': 'xls',
                'storage_category_id': storage_category,
                'storage_department_id': 1,
                'filter[best_price][usage]': 0,
                'filter[qty][value]': 4,
                'filter[delta][value]': 2,
            }
        else:
            self.die(
                'storage_department_id can be whether 1 for tyres or 2 for rims. ' + \
                'The value you provided \'{}\' is wrong! Exiting...'.format(storage_category)
            )


    def send_request(self, req, *args, **kwargs):
        req_type = (req.__name__.upper() + " ") if req.__name__.upper() in ['GET', 'POST'] else ''

        message = 'Sending {}request...'.format(req_type)
        if args:
            args_msg = ' Args: ' + ', '.join(map(str, args)) + '.'
            message += args_msg
        if kwargs:
            kwargs_msg = ' Keyword args [\'data\']: '
            if ('disable_log' in kwargs) and kwargs['disable_log']:
                kwargs_msg += "<DISABLED>"
            else:
                kwargs_msg += "{}".format(kwargs['data'])

            # Clear out kwargs for futher processing by requests
            kwargs.pop('disable_log', None)
            message += kwargs_msg

        self.logger.info(message)
        try:
            response = req(*args, **kwargs)
        except Exception as err:
            self.die(err)
        else:
            self.logger.info('Success! Got response.')
            return response


    def ftp_upload(self, file, enabled=True):
        if enabled:
            ftp = FTP(**self.ftp_settings)
            ftp.cwd(self.ftp_settings_upload_dir)

            with open(file, 'rb') as f:
                result = ftp.storbinary('STOR {}'.format(file.split('/')[-1]), f)
                if result == '226 Transfer complete':
                    self.logger.info('FTP: File uloaded successfully!')

            ftp.quit()


    def init_logger(self, logfile, level, console_enabled=False):
        self.logger = logging.getLogger(name=logfile)
        self.logger.setLevel(level)
        formatter = logging.Formatter(
            '[ %(asctime)s : %(levelname)s : %(funcName)s : %(lineno)s ] %(message)s', 
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        if console_enabled:
            console = logging.StreamHandler(sys.stdout)
            console.setLevel(level)
            console.setFormatter(formatter)
            self.logger.addHandler(console)

        logfile = logging.handlers.RotatingFileHandler(logfile, maxBytes=1048576, backupCount=5)
        logfile.setLevel(level)
        logfile.setFormatter(formatter)
        self.logger.addHandler(logfile)


    def die(self, message):
        self.logger.critical('ERROR! {}'.format(message))
        sys.exit(1)


### MAIN CODE ###
if __name__ == '__main__':
    parser = MIIIX_Parser()
    parser.run()
