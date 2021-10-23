# import the Flask class from the flask module
from flask import Flask
from flask_sqlalchemy import SQLAlchemy


# create the application object
app = Flask(__name__)
app.config.from_pyfile('../instance/config.py')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///posts.db'
db = SQLAlchemy(app)

def get_users():
    from calblog.models import User
    users = []
    users.append(User(id=1, username=app.config['USERNAME'], password=app.config['PASSWORD']))
    return users

from calblog import routes