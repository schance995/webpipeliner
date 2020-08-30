from flask import Flask, Request # necessary import
from config import Config
import logging
from logging.handlers import RotatingFileHandler
import os
from flask_bootstrap import Bootstrap
from flask_wtf.csrf import CSRFProtect

# initialize app and libraries
app = Flask(__name__)
app.config.from_object(Config)

# to resolve circular import in routes.py
from project import routes, errors # necessary import

bootstrap = Bootstrap(app)
csrf = CSRFProtect(app)

# logs printed in debug mode
if not app.debug:
    if not os.path.exists('logs'):
        os.mkdir('logs')
    file_handler = RotatingFileHandler(
        'logs/webpipeliner.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)

    app.logger.setLevel(logging.INFO)
    app.logger.info('WebPipeliner startup')
