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