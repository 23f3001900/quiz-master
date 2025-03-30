import os
from dotenv import load_dotenv
from app import app
load_dotenv()

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY','default_secret_key')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI','sqlite:///db.sqlite3')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = os.getenv('SQLALCHEMY_TRACK_MODIFICATIONS','False')=='True'