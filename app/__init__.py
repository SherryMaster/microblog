import logging
import os
from logging.handlers import RotatingFileHandler, SMTPHandler

from flask import Flask
from config import Config, basedir
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail

app = Flask(__name__)
app.config.from_object(Config)
mail = Mail(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login = LoginManager(app)
setattr(login, "login_view", "login")

# In production, keep a rotating file log and optionally email ERROR-level
# records to the administrators.  Flask's debugger already provides detailed
# error output during development, so these handlers are only installed when
# debug mode is off.  The environment check keeps the book's FLASK_DEBUG=1
# workflow compatible with current Flask CLI loading behavior.
debug_mode = app.debug or os.environ.get('FLASK_DEBUG') == '1'
if not debug_mode:
    if app.config['MAIL_SERVER']:
        auth = None
        if app.config['MAIL_USERNAME'] or app.config['MAIL_PASSWORD']:
            auth = (app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
        secure = () if app.config['MAIL_USE_TLS'] else None
        mail_handler = SMTPHandler(
            mailhost=(app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
            fromaddr='no-reply@' + app.config['MAIL_SERVER'],
            toaddrs=app.config['ADMINS'],
            subject='Microblog Failure',
            credentials=auth,
            secure=secure,
        )
        mail_handler.setLevel(logging.ERROR)
        app.logger.addHandler(mail_handler)

    log_dir = os.path.join(basedir, 'logs')
    if not os.path.exists(log_dir):
        os.mkdir(log_dir)
    file_handler = RotatingFileHandler(
        os.path.join(log_dir, 'microblog.log'),
        maxBytes=10240,
        backupCount=10,
    )
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s '
        '[in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)

    app.logger.setLevel(logging.INFO)
    app.logger.info('Microblog startup')


from app import routes, models, errors
