import os

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024 # 16 megabytes
