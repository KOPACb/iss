from flask import Flask

from config import  Config
from sqlalchemy.event import listen
from sqlalchemy import event, DDL
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, login_required


app = Flask(__name__, static_url_path='/static', static_folder='../static')
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login = LoginManager(app)
login.login_view = 'login'


from app import routes, models, errors
from sqlalchemy.event import listen
from app.models import User

@event.listens_for(User.__table__, 'after_create')
def insert_initial_values(*args, **kwargs):
    db.session.add(User(username='admin', level=7, password_hash='pbkdf2:sha256:150000$NSYNOJme$a9c67fbc439ecc56f8f311aa82b8e9a3289edcbd10b3a978c90de15648bf6fd8'))
    db.session.commit()
