from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:MyNewPass@localhost:3306/blogz'
app.config['SQLALCHEMY_ECHO'] = True

app.secret_key = 'q&MEnnk!VzN6AHQ@'

db = SQLAlchemy(app)