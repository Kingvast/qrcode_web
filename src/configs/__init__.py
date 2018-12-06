"""
基础配置信息
通过 configs/__init__.py 将这个模块设置为默认的 config
"""
DEBUG = True

# sanic server config
HOST = '0.0.0.0'
PORT = 8000
WORKERS = 1

# db server
COUCHDB_URL = 'http://couchdb:5984'
COUCHDB_USER = 'develop'
COUCHDB_PASSWORD = 'devpwd'
COUCHDB_DATABASE = 'qrcode'
COUCHDB_RECORDS = 'records'

# app files dir
APP_FILES_DIR = '/opt/app_files/'
# app images dir
APP_IMAGES_DIR = '/opt/images/'

# sentry, Fixme: 设置合适的 sentry dsn
SENTRY_DSN = ''

APP_URL = 'https://localhost:8008/download?app_name='
