#!/usr//bin/env/python3
# -*- coding:utf-8 -*-
__author__ = 'Hiram Zhang'

import os
import sys

basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

# SQLite URI compatible
WIN = sys.platform.startswith('win')
if WIN:
    prefix = 'sqlite:///'
else:
    prefix = 'sqlite:////'


class BaseConfig:
    SECRET_KEY = os.getenv('SECRET_KEY', 'a default secret string')

    COOKIE_POOL = 'http://cookie_pool_host/rmhnair/random'

    CACHE_TYPE = 'redis'
    CACHE_REDIS_HOST = 'your redis container name'
    CACHE_REDIS_PORT = 6179
    CACHE_REDIS_DB = os.getenv('CACHE_REDIS_DB') or ''
    CACHE_REDIS_PASSWORD = os.getenv('CHCHE_REDIS_PASSWORD') or ''

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_DATABASE_URI = prefix + os.path.join(basedir, 'data.db')
