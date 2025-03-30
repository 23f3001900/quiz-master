from app import app
from flask import render_template, request, redirect, url_for, flash, session
from models import db,User,Subject,Chapter,Quiz,Question,Scores
from werkzeug.security import generate_password_hash,check_password_hash
from datetime import datetime,time, timedelta, date
from functools import wraps
import csv
from uuid import uuid4
def check_admin(func):
    @wraps(func)
    def inner(*args,**kwargs):
        if 'user_id' not in session:
            flash('Please login to continue')
            return redirect(url_for('login'))
        user=User.query.get(session['user_id'])
        if not user.admin:
            flash('You are not authorized to access this page')
            return redirect(url_for('index'))
        return func(*args,**kwargs)
    return inner
def check_auth(func):
    @wraps(func)
    def inner(*args,**kwargs):
        if 'user_id' in session:
            return func(*args,**kwargs)
        else:
            flash('Please login to continue')
            return redirect(url_for('login'))
    return inner

@app.route('/admin')
@check_admin
def admin():
    user = User.query.get(session.get('user_id'))
    subjects=Subject.query.all()
    parameters = request.args.get('parameter')
    query = request.args.get('query')
    if parameters=='subject':
        subjects=Subject.query.filter(Subject.name.ilike(f'%{query}%')).all() 
    elif parameters=='chapter':
        filtered_subjects = []
        for subject in subjects:
            subject.chapters=[chapter for chapter in subject.chapters if query.lower() in chapter.name.lower()]
            if subject.chapters:
                filtered_subjects.append(subject)
        subjects=filtered_subjects
    return render_template('admin.html',subjects=subjects,user=user)



@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login_post():
    em=request.form.get('Email')
    pa=request.form.get('Password')
    if not em or not pa:
        flash('Please fill all the fields to login')
        return redirect(url_for('login'))
    
    user=User.query.filter_by(email=em).first()
    if not user:
        flash('Email not registered.Please register')
        return redirect(url_for('register'))
    if not check_password_hash(user.passhash,pa):
        flash('Incorrect password')
        return redirect(url_for('login'))
    session['user_id']=user.id
    flash('Logged in successfully')
    return redirect(url_for('index'))


@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/register', methods=['POST'])
def register_post():
    name=request.form.get('Name')
    email=request.form.get('Email')
    dob=request.form.get('DOB')
    qua=request.form.get('Qualification')
    password=request.form.get('Password')
    confirm=request.form.get('CPassword')
    if not name or not email or not dob or not qua or not password or not confirm:
        flash('Kindly fill all the fields to register')
        return redirect(url_for('register'))
    if password!=confirm:
        flash('Passwords do not match')
        return redirect(url_for('register'))
    
    user=User.query.filter_by(email=email).first()
    if user:
        flash('Email already registered')
        return redirect(url_for('register'))
    pydob=datetime.strptime(dob,'%Y-%m-%d').date()
    passhash=generate_password_hash(password)
    new_user=User(email=email,fullname=name,qualification=qua,dob=pydob,passhash=passhash)
    db.session.add(new_user)
    db.session.commit()
    
    return redirect(url_for('login'))

@app.route('/profile')
@check_auth
def profile():
    user=User.query.get(session['user_id'])
    return render_template('profile.html',user=user)

@app.route('/profile', methods=['POST'])
@check_auth
def profile_post():
    em=request.form.get('Email')
    cpassword=request.form.get('CPassword')
    npassword=request.form.get('NPassword')
    name=request.form.get('Name')
    dob=request.form.get('DOB')
    qua=request.form.get('Qualification')

    if not em or not cpassword:
        flash('Please fill all the fields to update profile')
        return redirect(url_for('profile'))
    
    user=User.query.get(session['user_id'])
    if not check_password_hash(user.passhash,cpassword):
        flash('Incorrect password')
        return redirect(url_for('profile'))
    
    if name:
        user.fullname=name
    if dob:
        user.dob=datetime.strptime(dob,'%Y-%m-%d').date()       
    if qua:
        user.qualification=qua
    if npassword:
        user.passhash=generate_password_hash(npassword)
    db.session.commit()
    flash('Profile updated successfully')
    return redirect(url_for('profile'))




@app.route('/logout')
@check_auth
def logout():
    session.pop('user_id')
    return redirect(url_for('login'))

@app.route('/subjects/add')
@check_admin
def add_subject():
    user = User.query.get(session.get('user_id'))
    return render_template('subject/add.html', user=user)

@app.route('/subjects/add', methods=['POST'])
@check_admin
def add_subject_post():
    name=request.form.get('name')
    credits=request.form.get('credits')
    semester=request.form.get('semester')
    desc=request.form.get('description')
    if not name or not credits or not semester or not desc:
        flash('Please fill all the fields to add subject')
        return redirect(url_for('add_subject'))
    subject=Subject.query.filter_by(name=name).first()
    if subject:
        flash('Subject already exists')
        return redirect(url_for('add_subject'))
    new_subject=Subject(name=name,credits=credits,semester=semester,description=desc)
    db.session.add(new_subject)
    db.session.commit()
    flash('Subject added successfully')
    return redirect(url_for('admin'))

@app.route('/subjects/<int:id>/show')
@check_admin
def show_subject(id):
    user = User.query.get(session.get('user_id'))
    subject=Subject.query.get(id)
    if not subject:
        flash('Subject does not exist')
        return redirect(url_for('admin'))
    return render_template('subject/show.html',subject=subject,user=user)

@app.route('/subjects/<int:id>/edit')
@check_admin
def edit_subject(id):
    user = User.query.get(session.get('user_id'))
    subject=Subject.query.get(id)
    if not subject:
        flash('Subject does not exist')
        return redirect(url_for('admin'))
    return render_template('subject/edit.html',subject=subject,user=user)

@app.route('/subjects/<int:id>/edit', methods=['POST'])
@check_admin
def edit_subject_post(id):
    subject=Subject.query.get(id)
    if not subject:
        flash('Subject does not exist')
        return redirect(url_for('admin'))
    name=request.form.get('name')
    credits=request.form.get('credits')
    semester=request.form.get('semester')
    desc=request.form.get('description')
    if not (credits or semester or desc):
        flash('No changes made')
        return redirect(url_for('edit_subject'))
    if name!=subject.name:
        flash('Subject does not exist')
        return redirect(url_for('edit_subject'))
    if credits:
        subject.credits=credits
    if semester:
        subject.semester=semester
    if desc:
        subject.description=desc
    db.session.commit()
    flash('Subject updated successfully')
    return redirect(url_for('admin'))


@app.route('/subjects/<int:id>/delete')
@check_admin
def delete_subject(id):
    user = User.query.get(session.get('user_id'))
    subject=Subject.query.get(id)
    if not subject:
        flash('Subject does not exist')
        return redirect(url_for('admin'))
    return render_template('subject/delete.html',subject=subject,user=user)

@app.route('/subjects/<int:id>/delete', methods=['POST'])
@check_admin
def delete_subject_post(id):
    subject=Subject.query.get(id)
    if not subject:
        flash('Subject does not exist')
        return redirect(url_for('admin'))
    db.session.delete(subject)
    db.session.commit()
    flash('Subject deleted successfully')
    return redirect(url_for('admin'))

@app.route('/chapters/add/<int:subject_id>')
@check_admin
def add_chapter(subject_id):
    user = User.query.get(session.get('user_id'))
    subject=Subject.query.get(subject_id)
    if not subject:
        flash('Subject does not exist')
        return redirect(url_for('admin'))
    return render_template('chapter/add.html',subject=subject,user=user)

@app.route('/chapters/add/<int:subject_id>', methods=['POST'])
@check_admin
def add_chapter_post(subject_id):
    subject=Subject.query.get(subject_id)
    if not subject:
        flash('Subject does not exist')
        return redirect(url_for('admin'))
    name=request.form.get('name')
    desc=request.form.get('description')
    if not name or not desc :
        flash('Please fill all the fields to add chapter')
        return redirect(url_for('add_chapter'))
    chapter=Chapter.query.filter_by(name=name).first()
    if chapter:
        flash('Chapter already exists')
        return redirect(url_for('add_chapter'))
    new_chapter=Chapter(name=name,description=desc,subject_id=subject_id)
    db.session.add(new_chapter)
    db.session.commit()
    flash('Chapter added successfully')
    return redirect(url_for('show_subject',id=subject_id))

@app.route('/chapters/delete/<int:id>')
@check_admin
def delete_chapter(id):
    user = User.query.get(session.get('user_id'))
    chapter=Chapter.query.get(id)
    if not chapter:
        flash('Chapter does not exist')
        return redirect(url_for('admin'))
    return render_template('chapter/delete.html',chapter=chapter,user=user)

@app.route('/chapters/delete/<int:id>', methods=['POST'])
@check_admin
def delete_chapter_post(id):
    chapter=Chapter.query.get(id)
    if not chapter:
        flash('Chapter does not exist')
        return redirect(url_for('admin'))
    db.session.delete(chapter)
    db.session.commit()
    flash('Subject deleted successfully')
    return redirect(url_for('admin'))

@app.route('/chapters/edit/<int:id>')
@check_admin
def edit_chapter(id):
    user = User.query.get(session.get('user_id'))
    chapter=Chapter.query.get(id)
    if not chapter:
        flash('Chapter does not exist')
        return redirect(url_for('admin'))
    return render_template('chapter/edit.html',chapter=chapter,user=user)

@app.route('/chapters/edit/<int:id>', methods=['POST'])
@check_admin
def edit_chapter_post(id):
    chapter=Chapter.query.get(id)
    if not chapter:
        flash('Chapter does not exist')
        return redirect(url_for('admin'))
    name=request.form.get('name')
    desc=request.form.get('description')
    if not(name or desc):
        flash('No changes made')
        return redirect(url_for('edit_chapter'))
    chapter1=Chapter.query.filter_by(name=name).first()
    if name:
        if chapter1:
            flash('Chapter already exists')
            return redirect(url_for('edit_chapter'))
        chapter.name=name
    if desc:
        chapter.description=desc
    db.session.commit()
    flash('Subject updated successfully')
    return redirect(url_for('admin'))

@app.route('/chapters/show/<int:id>')
@check_admin
def show_chapter(id):
    user = User.query.get(session.get('user_id'))
    chapter=Chapter.query.get(id)
    if not chapter:
        flash('Chapter does not exist')
        return redirect(url_for('admin'))
    return render_template('chapter/show.html',chapter=chapter,user=user)

@app.route('/quiz/add/<int:chapter_id>')
@check_admin
def add_quiz(chapter_id):
    user = User.query.get(session.get('user_id'))
    chapter = Chapter.query.get(chapter_id)
    if not chapter:
        flash('Chapter does not exist')
        return redirect(url_for('admin'))
    return render_template('quiz/add.html', chapter=chapter, user=user)


@app.route('/quiz/add/<int:chapter_id>', methods=['POST'])
@check_admin
def add_quiz_post(chapter_id):
    chapter = Chapter.query.get(chapter_id)
    if not chapter:
        flash('Chapter does not exist')
        return redirect(url_for('admin'))
    
    date = request.form.get('date')
    duration = request.form.get('duration')
    remarks = request.form.get('remarks')

    if not date or not duration or not remarks:
        flash('Please fill all the fields to add quiz')
        return redirect(url_for('add_quiz', chapter_id=chapter_id))
    try:
        quiz_date = datetime.strptime(date, '%Y-%m-%d').date()
    except ValueError:
        flash('Invalid date format. Please use YYYY-MM-DD.')
        return redirect(url_for('add_quiz', chapter_id=chapter_id))
    
    try:
        # Assuming duration_str is in hours, convert it to a time object
        duration_hours = int(duration)
        quiz_duration = time(hour=duration_hours)  # Set hours; minutes default to 0
    except ValueError:
        flash('Invalid duration format. Please enter a whole number in hours.')
        return redirect(url_for('add_quiz', chapter_id=chapter_id))
    
    new_quiz = Quiz(quiz_date=quiz_date, quiz_duration=quiz_duration, remarks=remarks, chapter_id=chapter_id)
    db.session.add(new_quiz)
    db.session.commit()
    
    flash('Quiz added successfully')
    return redirect(url_for('show_chapter',id=chapter_id))


@app.route('/quiz/delete/<int:id>')
@check_admin
def delete_quiz(id):
    user = User.query.get(session.get('user_id'))
    quiz=Quiz.query.get(id)
    chapter_id=quiz.chapter_id
    if not quiz:
        flash('Quiz does not exist')
        return redirect(url_for('show_chapter',id=chapter_id))
    return render_template('quiz/delete.html',quiz=quiz,user=user)

@app.route('/quiz/delete/<int:id>', methods=['POST'])
@check_admin
def delete_quiz_post(id):
    quiz=Quiz.query.get(id)
    if not quiz:
        flash('Quiz does not exist')
        return redirect(url_for('show_chapter',id=quiz.chapter_id))
    db.session.delete(quiz)
    db.session.commit()
    flash('Quiz deleted successfully')
    return redirect(url_for('show_chapter',id=quiz.chapter_id))

@app.route('/quiz/edit/<int:id>')
@check_admin
def edit_quiz(id):
    user = User.query.get(session.get('user_id'))
    quiz=Quiz.query.get(id)
    if not quiz:
        flash('Quiz does not exist')
        return redirect(url_for('admin'))
    return render_template('quiz/edit.html',quiz=quiz,user=user)

@app.route('/quiz/edit/<int:id>', methods=['POST'])
@check_admin
def edit_quiz_post(id):
    quiz=Quiz.query.get(id)
    if not quiz:
        flash('Quiz does not exist')
        return redirect(url_for('admin'))
    date=request.form.get('name')
    duration=request.form.get('duration')
    remarks=request.form.get('remarks')
    if not(date or duration or remarks):
        flash('No changes made')
        return redirect(url_for('edit_quiz',id=id))
    if date:
        try:
            quiz_date = datetime.strptime(date, '%Y-%m-%d').date()
        except ValueError:
            flash('Invalid date format. Please use YYYY-MM-DD.')
            return redirect(url_for('edit_quiz',id=id))
        quiz.quiz_date=quiz_date
    if duration:
        try:
            # Assuming duration_str is in hours, convert it to a time object
            duration_hours = int(duration)
            quiz_duration = time(hour=duration_hours)  # Set hours; minutes default to 0
        except ValueError:
            flash('Invalid duration format. Please enter a whole number in hours.')
            return redirect(url_for('edit_quiz',id=id))
        quiz.quiz_duration=quiz_duration
    if remarks:
        quiz.remarks=remarks
    db.session.commit()
    flash('Quiz updated successfully')
    return redirect(url_for('admin'))

@app.route('/quiz/show/<int:id>')
@check_admin
def show_quiz(id):
    user = User.query.get(session.get('user_id'))
    quiz=Quiz.query.get(id)
    if not quiz:
        flash('Quiz does not exist')
        return redirect(url_for('admin'))
    return render_template('quiz/show.html',quiz=quiz,user=user)

@app.route('/question/add/<int:quiz_id>')
@check_admin
def add_question(quiz_id):
    user = User.query.get(session.get('user_id'))
    quiz = Quiz.query.get(quiz_id)
    if not quiz:
        flash('Quiz does not exist')
        return redirect(url_for('admin'))
    return render_template('question/add.html', quiz=quiz,user=user)


@app.route('/question/add/<int:quiz_id>', methods=['POST'])
@check_admin
def add_question_post(quiz_id):
    quiz = Quiz.query.get(quiz_id)
    if not quiz:
        flash('Chapter does not exist')
        return redirect(url_for('admin'))
    
    statement = request.form.get('statement')
    option1 = request.form.get('option1')
    option2 = request.form.get('option2')
    option3 = request.form.get('option3')
    option4= request.form.get('option4')
    answer_index = request.form.get('correct_option')
    

    if not statement or not option1 or not option2 or not option3 or not option4 or not answer_index:
        flash('Please fill all the fields to add question')
        return redirect(url_for('add_question', quiz_id=quiz_id))
    statement = statement.strip()
    option1 = option1.strip()
    option2 = option2.strip()
    option3 = option3.strip()
    option4 = option4.strip()
    options = [option1, option2, option3, option4]
    try:
        answer = options[int(answer_index) - 1]  # Map "1" to option1, "2" to option2, etc.
    except (IndexError, ValueError):  # Handle invalid indices
        flash('Invalid correct option selected')
        return redirect(url_for('add_question', quiz_id=quiz_id))

    # Validate that the answer matches one of the options
    if answer not in options:
        flash('The answer must match one of the provided options')
        return redirect(url_for('add_question', quiz_id=quiz_id))
        
    existing_question = Question.query.filter_by(quiz_id=quiz_id, statement=statement).first()
    if existing_question:
        flash('A question with this statement already exists in the quiz')
        return redirect(url_for('add_question', quiz_id=quiz_id))
    
    options = [option1, option2, option3, option4]
    if len(set(options)) < 4:
        flash('All options must be unique')
        return redirect(url_for('add_question', quiz_id=quiz_id))


    
    new_question = Question(statement=statement, option1=option1, option2=option2, option3=option3, option4=option4, answer=answer, quiz_id=quiz_id)
    db.session.add(new_question)
    db.session.commit()
    
    flash('Question added successfully')
    return redirect(url_for('show_quiz',id=quiz_id))


@app.route('/question/delete/<int:id>')
@check_admin
def delete_question(id):
    user = User.query.get(session.get('user_id'))
    question=Question.query.get(id)
    quiz_id=question.quiz_id
    if not question:
        flash('Question does not exist')
        return redirect(url_for('show_quiz',id=quiz_id))
    return render_template('question/delete.html',question=question,user=user)

@app.route('/question/delete/<int:id>', methods=['POST'])
@check_admin
def delete_question_post(id):
    question=Question.query.get(id)
    if not question:
        flash('Question does not exist')
        return redirect(url_for('show_quiz',id=question.quiz_id))
    db.session.delete(question)
    db.session.commit()
    flash('Question deleted successfully')
    return redirect(url_for('show_quiz',id=question.quiz_id))

@app.route('/question/edit/<int:id>')
@check_admin
def edit_question(id):
    user = User.query.get(session.get('user_id'))
    question=Question.query.get(id)
    if not question:
        flash('Question does not exist')
        return redirect(url_for('admin'))
    return render_template('question/edit.html',question=question,user=user)

@app.route('/question/edit/<int:id>', methods=['POST'])
@check_admin
def edit_question_post(id):
    question=Question.query.get(id)
    if not question:
        flash('Question does not exist')
        return redirect(url_for('admin'))
    statement = request.form.get('statement')
    # Build the updated options list
    option1=request.form.get('option1') or question.option1
    option2=request.form.get('option2') or question.option2
    option3=request.form.get('option3') or question.option3 
    option4=request.form.get('option4') or question.option4
    updated_options = [option1,option2,option3,option4]
    answer_index = request.form.get('correct_option')
    if statement:
        existing_question = Question.query.filter_by(statement=statement).first()
        if existing_question:
            flash('A question with this statement already exists in the quiz')
            return redirect(url_for('edit_question', id=id))
        question.statement=statement
    # Update the correct answer based on the new options
    if answer_index:
        try:
            answer = updated_options[int(answer_index) - 1]  # Map index to the correct option
            question.answer = answer
        except (IndexError, ValueError):
            flash('Invalid correct option selected')
            return redirect(url_for('edit_question', id=id))

    # Update options only if provided
    if request.form.get('option1'):
        question.option1 = request.form.get('option1')
    if request.form.get('option2'):
        question.option2 = request.form.get('option2')
    if request.form.get('option3'):
        question.option3 = request.form.get('option3')
    if request.form.get('option4'):
        question.option4 = request.form.get('option4')
    db.session.commit()
    flash('Question updated successfully')
    return redirect(url_for('admin'))

#user routes

@app.route('/')
@check_auth
def index():
    user=User.query.get(session['user_id'])
    if user.admin:
        return redirect(url_for('admin'))
    subjects=Subject.query.all()
    parameters = request.args.get('parameter')
    query = request.args.get('query')
    if parameters=='subject':
        subjects=Subject.query.filter(Subject.name.ilike(f'%{query}%')).all() 
    elif parameters=='chapter':
        filtered_subjects = []
        for subject in subjects:
            subject.chapters=[chapter for chapter in subject.chapters if query.lower() in chapter.name.lower()]
            if subject.chapters:
                filtered_subjects.append(subject)
        subjects=filtered_subjects
    return render_template('index.html',subjects=subjects,user=user)

@app.route('/gotochapter/<int:id>')
@check_auth
def gotochapter(id):
    user = User.query.get(session.get('user_id'))
    chapter=Chapter.query.get(id)
    if not chapter:
        flash('Chapter does not exist')
        return redirect(url_for('index'))
    return render_template('gotochapter.html',chapter=chapter,user=user)

@app.route('/viewquiz/<int:id>')
@check_auth
def viewquiz(id):
    user = User.query.get(session.get('user_id'))
    quiz=Quiz.query.get(id)
    if not quiz:
        flash('Quiz does not exist')
        return redirect(url_for('index'))
    return render_template('viewquiz.html',quiz=quiz,user=user)



@app.route('/startquiz/<int:quiz_id>', methods=['GET', 'POST'])
@check_auth
def startquiz(quiz_id):
    user = User.query.get(session.get('user_id'))
    quiz = Quiz.query.get_or_404(quiz_id)

    # Check if the quiz has questions
    if not quiz.questions:
        flash("This quiz has no questions!", "danger")
        return redirect(url_for('index'))

    if request.method == 'POST':
        user_answers = request.form  
        score = 0

        # Check answers and calculate score
        for question in quiz.questions:
            user_answer = user_answers.get(f'q{question.id}')
            if user_answer and user_answer == question.answer:
                score += 1

        # Save score in the database
        user_id = session.get('user_id')

        start_time = session.get('start_time', datetime.now().isoformat())
        elapsed_time = datetime.now() - datetime.fromisoformat(start_time)

        new_score = Scores(
            user_id=user_id,
            quiz_id=quiz_id,
            total_time=(datetime.min + elapsed_time).time(),  # Convert timedelta to time
            score=score,
            date_of_attempt=date.today()
        )
        db.session.add(new_score)
        db.session.commit()

        # Clear the session variables
        session.pop('start_time', None)

        flash(f'You successfully scored {score}/{len(quiz.questions)}!')
        return redirect(url_for('index'))

    # Record the start time of the quiz
    session['start_time'] = datetime.now().isoformat()

    return render_template('startquiz.html', quiz=quiz, user=user)

@app.route('/scores/<int:id>')
@check_auth
def scores(id):
    user = User.query.get(session.get('user_id'))
    user_id = session.get('user_id')
    scores = Scores.query.filter_by(user_id=user_id).all()
    if user_id != id:
        flash('You are not authorized to view this page')
        return redirect(url_for('index'))
    return render_template('scores.html', scores=scores, user=user)

@app.route('/export_csv')
@check_auth
def export_csv():
    user = User.query.get(session.get('user_id'))
    user_id = session.get('user_id')
    scores = Scores.query.filter_by(user_id=user_id).all()
    filename=uuid4().hex+'.csv'
    url='static/csv/'+filename
    with open(url,'w',newline='') as file:
        writer=csv.writer(file)
        writer.writerow(['Quiz','Score','Total Time','Date of Attempt'])
        for score in scores:
            writer.writerow([score.quiz.chapter.name,score.score,score.total_time,score.date_of_attempt])
    return redirect(url_for('static',filename='csv/'+filename))

@app.route('/summary_admin')
@check_admin
def summary_admin():
    user = User.query.get(session.get('user_id'))

    subjects = Subject.query.all()
    
    subject_scores = []

    for subject in subjects:
        chapters = subject.chapters  
        
        quizzes = [quiz for chapter in chapters for quiz in chapter.quizzes]


        scores = [score.score for quiz in quizzes for score in quiz.scores]
        max_score = max(scores) if scores else 0  # Handle empty scores

        # Add the subject name and max score to the list
        subject_scores.append({
            "subject_name": subject.name,
            "max_score": max_score
        })

    # Prepare data for Chart.js
    subjects_list = [item["subject_name"] for item in subject_scores]
    max_scores_list = [item["max_score"] for item in subject_scores]


    return render_template(
        'summary_admin.html',
        user=user,
        subjects=subjects_list,
        top_scores=max_scores_list
    )

@app.route('/summary_user')
@check_auth
def summary_user():
    user = User.query.get(session.get('user_id'))  

    subjects = Subject.query.all()


    subject_attempts = []
    for subject in subjects:
        
        chapters = subject.chapters

      
        quizzes = [quiz for chapter in chapters for quiz in chapter.quizzes]

        
        attempts = sum(
            1 for quiz in quizzes for score in quiz.scores if score.user_id == user.id
        )
        
        subject_attempts.append({
            "subject_name": subject.name,
            "attempts": attempts
        })
    # Prepare data for Chart.js
    subjects_list = [item["subject_name"] for item in subject_attempts]
    attempts_list = [item["attempts"] for item in subject_attempts]

    return render_template(
        'summary_user.html',
        user=user,
        subjects=subjects_list,
        attempts=attempts_list,
    )