from datetime import date

from flask import Flask, render_template, redirect, request, url_for, flash, session
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

#database-config
app.config["SQLALCHEMY_DATABASE_URI"] = 'postgresql+psycopg2://svuppalanchu:D7B4855F@db-postgresql-is-5600-22-do-user-12767037-0.b.db.ondigitalocean.com:25060/svuppalanchu'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.debug = True

db = SQLAlchemy(app)
db.init_app(app)

# session config
app.config["SESSION_TYPE"] = "filesystem"
app.config["SESSION_PERMANENT"] = False
Session(app)

with app.app_context():
    db.create_all()
    db.session.commit()

#Models for database
class Users(db.Model):
    __tablename__ = "Users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), nullable=False, unique=True)
    password = db.Column(db.String(256), nullable=False, unique=False)

class Tasks(db.Model):
    __tablename__ = "Tasks"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer,db.ForeignKey('Users.id'))
    task = db.Column(db.String(256) ,nullable=False,unique=False)
    # 0 = Did not start || 1 = In progress || 2 = Done!
    status = db.Column(db.Integer ,default = 0)

class Meetings(db.Model):
    __tablename__ = "Meetings"
    meeting_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer,db.ForeignKey('Users.id'))
    meeting_desc = db.Column(db.String(256) ,nullable=False,unique=False)
    date = db.Column(db.Date,nullable=False)
    time = db.Column(db.String(256),nullable=False)

#login method
@app.route('/',methods=["GET", "POST"])
@app.route('/login',methods=["GET", "POST"])
def login():

    if request.method == "GET":
        session.clear()
        return render_template("login.html")

    if request.method == "POST":
        uname = request.form['username']
        password = request.form['password']

        # check username and password
        user = Users.query.filter_by(username=uname).first()
        if not user:
            flash("Invalid username and password")
            return render_template("login.html")

        if user.username != uname:
            flash("invalid username")
            return render_template("login.html")

        if not check_password_hash(user.password, password):
            flash("Invalid password")
            return render_template("login.html")

        # add user id in db to user session
        session["user_id"] = user.id
        return render_template("Home.html")

    else:
        return render_template("login.html")

#User Registration
@app.route('/register',methods=["GET", "POST"])
def register():
    if request.method == "POST":
        uname = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        #check if both passwords are same
        if password!=confirm_password:
            flash("Passwords do not match!")
            return render_template("Register.html")

        # check if user is not duplicate
        user_check = Users.query.filter_by(username=uname).first()
        if user_check:
            flash("Username already exists")
            return render_template("Register.html")

        registers = Users(username=uname, password=generate_password_hash(password))
        db.session.add(registers)
        db.session.commit()
        flash("Successfully registered")
        return redirect(url_for("home"))
    return render_template("Register.html")

#Display the tasks
@app.route('/task_home',methods=["GET", "POST"])
def task_home():
    if request.method=='GET':
        user_db_data = Tasks.query.filter_by(user_id=(session['user_id'])).all()
        todo_list = []
        #append the details in a dictionary
        for result in user_db_data:
            item = {
                "id": result.id,
                "task": result.task,
                "status": result.status
            }
            todo_list.append(item)
        return render_template("To-Do_Home.html",items=todo_list,user_id=session['user_id'])

#Insert a meeting to the database
@app.route('/add_meeting',methods=["GET", "POST"])
def add_meeting():
    meeting = request.form['meeting_desc']
    date = request.form['date']
    time=request.form['time']
    meetings = Meetings(user_id=session['user_id'], meeting_desc=meeting, date=date,time=time)
    db.session.add(meetings)
    db.session.commit()
    return redirect(url_for("meeting_home"))

#Insert a task to the database
@app.route('/add_task',methods=["GET", "POST"])
def add_task():
    task = request.form['task']
    status = request.form.get('status_select')
    if status == 'todo':
        status_flag = 0
    elif status == 'in_progress':
        status_flag = 1
    else:
        status_flag = 2
    tasks = Tasks(user_id=session['user_id'],task=task,status=status_flag)
    db.session.add(tasks)
    db.session.commit()
    return redirect(url_for("task_home"))

#Edit the task status
@app.route('/edit_status',methods=["GET", "POST"])
def edit_status():
    id=request.form['task_id']
    status = request.form.get('status_select')
    edit_task = Tasks.query.filter_by(id=id).first()
    if status == 'todo':
        status_flag = 0
    elif status == 'in_progress':
        status_flag = 1
    else:
        status_flag = 2
    edit_task.status = status_flag
    db.session.commit()
    return redirect(url_for("task_home"))

#Update the meeting details
@app.route('/update_meeting',methods=["GET", "POST"])
def update_meeting():
    id=request.form['meeting_id']
    meeting_desc = request.form['meeting_desc']
    date=request.form['date']
    time=request.form['time']
    edit_meeting = Meetings.query.filter_by(meeting_id=id).first()
    edit_meeting.meeting_desc = meeting_desc
    edit_meeting.date = date
    edit_meeting.time = time
    db.session.commit()
    return redirect(url_for("meeting_home"))

#delete the task details
@app.route('/delete_task',methods=["GET", "POST"])
def delete_task():
    if request.method == "GET":
        return render_template("To-Do_Home.html")
    if request.method == "POST":
        id = request.form['action']
        delete_task = Tasks.query.filter_by(id=id,user_id=session["user_id"]).first()
        if delete_task == None:
            return redirect(url_for("task_home"))
        db.session.delete(delete_task)
        db.session.commit()
    return redirect(url_for("task_home"))

#Delete the meeting
@app.route('/delete_meeting',methods=["GET", "POST"])
def delete_meeting():
    if request.method == "GET":
        return render_template("Meetings_Home.html")
    if request.method == "POST":
        id = request.form['action']
        delete_meeting = Meetings.query.filter_by(meeting_id=id,user_id=session["user_id"]).first()
        if delete_meeting == None:
            return redirect(url_for("meeting_home"))
        db.session.delete(delete_meeting)
        db.session.commit()
    return redirect(url_for("meeting_home"))
    return render_template("To-Do_Home.html")

#Meeting Home Page
@app.route('/meeting_home',methods=["GET", "POST"])
def meeting_home():
    today=date.today()
    if request.method=='GET':
        user_db_data = Meetings.query.filter_by(user_id=(session['user_id']),date=today).all()
        meeting_list = []
        for result in user_db_data:
            item = {
                "id": result.meeting_id,
                "meeting_desc": result.meeting_desc,
                "time": result.time
            }
            meeting_list.append(item)
        return render_template("Meetings_Home.html",items=meeting_list,user_id=session['user_id'])

#Display meetings of all time
@app.route('/meeting_home_all',methods=["GET", "POST"])
def meeting_home_all():
    if request.method=='GET':
        user_db_data = Meetings.query.filter_by(user_id=(session['user_id'])).all()
        meeting_list = []
        for result in user_db_data:
            item = {
                "id": result.meeting_id,
                "meeting_desc": result.meeting_desc,
                "time": result.time
            }
            meeting_list.append(item)
        return render_template("Meetings_Home.html",items=meeting_list,user_id=session['user_id'])

#Home page to direct tasks and meetings
@app.route('/home',methods=["GET", "POST"])
def home():
    return render_template("Home.html")

@app.route('/logout')
def logout():
    session.clear()
    return render_template("Login.html")

if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)

