from werkzeug.security import generate_password_hash, check_password_hash
from flask.ext.login import UserMixin
from . import db, login_manager


class Data(db.Model):
    __tablename__ = 'data_attribute'
    labelTime = db.Column(db.String(256))
    question = db.Column(db.Integer(10))
    pictureNum = db.Column(db.String(256))
    userid = db.Column(db.Integer(10))
    duration = db.Column(db.Integer(10))
    answer = db.Column(db.String(256))
    id = db.Column(db.Integer(10), primary_key=True, autoincrement=True)

    def __init__(self, labelTime, question, pictureNum, userid, duration, answer):
        self.labelTime = labelTime
        self.question = question
        self.pictureNum = pictureNum
        self.userid = userid
        self.duration = duration
        self.answer = answer

    def __repr__(self):
        return '<Share %r>' % self.labelTime


class Pictures(db.Model):
    __tablename__ = 'pictures_800'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    pic = db.Column(db.String(20))


class Questions(db.Model):
    __tablename__ = 'question'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    statement = db.Column(db.String(256))


class User(UserMixin, db.Model):
    __tablename__ = 'user_attribute'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    # role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    password_hash = db.Column(db.String(128))
    # sessionNum = db.Column(db.Integer(10))
    # picturepool = db.Column(db.String(20000))
    progress = db.Column(db.Integer(11))
    total = db.Column(db.Integer(11))
    start = db.Column(db.Integer(11))
    # question = db.Column(db.Integer(11))

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<User %r>' % self.username


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
