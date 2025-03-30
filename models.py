from app import app
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash,check_password_hash
from datetime import datetime
db=SQLAlchemy(app)
class User(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    email=db.Column(db.String(120),unique=True,nullable=False)
    passhash=db.Column(db.String(120),nullable=False)
    fullname=db.Column(db.String(80),nullable=False)
    qualification=db.Column(db.String(120),nullable=False)
    dob=db.Column(db.Date,nullable=False)
    admin=db.Column(db.Boolean,nullable=False,default=False)
    scores=db.relationship('Scores',backref='user',lazy=True,cascade='all,delete-orphan')

class Subject(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(120),unique=True,nullable=False)
    credits=db.Column(db.Integer,nullable=False)
    semester=db.Column(db.Integer,nullable=False)
    description=db.Column(db.String(120),nullable=False)
    chapters=db.relationship('Chapter',backref='subject',lazy=True,cascade='all,delete-orphan')

class Chapter(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(120),unique=True,nullable=False)
    description=db.Column(db.String(120),nullable=False)
    subject_id=db.Column(db.Integer,db.ForeignKey('subject.id'),nullable=False)
    quizzes=db.relationship('Quiz',backref='chapter',lazy=True,cascade='all,delete-orphan')

class Quiz(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    chapter_id=db.Column(db.Integer,db.ForeignKey('chapter.id'),nullable=False)
    quiz_date=db.Column(db.Date,nullable=False)
    quiz_duration=db.Column(db.Time,nullable=False)
    remarks=db.Column(db.String(120),nullable=False)
    questions=db.relationship('Question',backref='quiz',lazy=True,cascade='all,delete-orphan')
    scores=db.relationship('Scores',backref='quiz',lazy=True,cascade='all,delete-orphan')

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)
    statement = db.Column(db.String(120), nullable=False)
    option1 = db.Column(db.String(120), nullable=False)
    option2 = db.Column(db.String(120), nullable=False)
    option3 = db.Column(db.String(120), nullable=False)
    option4 = db.Column(db.String(120), nullable=False)
    answer = db.Column(db.String(120), nullable=False)

class Scores(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    user_id=db.Column(db.Integer,db.ForeignKey('user.id'),nullable=False)
    quiz_id=db.Column(db.Integer,db.ForeignKey('quiz.id'),nullable=False)
    date_of_attempt = db.Column(db.Date, nullable=False)
    total_time=db.Column(db.Time,nullable=False)
    score=db.Column(db.Integer,nullable=False)

with app.app_context():
    db.create_all()
    ad=User.query.filter_by(admin=True).first()
    if not ad:
        password_hash=generate_password_hash('admin')
        ad = User(id=0,email='default@example.com',passhash=password_hash,fullname='Default User',qualification='Default Qualification',dob=datetime.strptime('1900-01-01', '%Y-%m-%d').date(),admin=True)
        db.session.add(ad)
        db.session.commit()
    
