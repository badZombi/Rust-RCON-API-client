# -*- coding: utf-8 -*-

import os
import json


BASE_DIR = os.path.dirname(os.path.abspath(__file__))

if not os.environ.get('FA_KEY'):
    from dotenv import load_dotenv
    DOTENV_PATH = os.path.join(BASE_DIR, '.env')
    load_dotenv(DOTENV_PATH)


class Config(object):
    API_SERVER=os.environ.get('API_SERVER')
    SECRET_KEY=os.environ.get('SECRET_KEY')
    FA_KEY=os.environ.get('FA_KEY')
    PLAYERS=json.loads(os.environ.get('PLAYERS'))
    ITEMS=json.loads(os.environ.get('ITEMS'))

