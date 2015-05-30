from werkzeug.security import generate_password_hash, check_password_hash
from flask.ext.login import UserMixin
from . import db, login_manager


user_chatroom = db.Table('user_chatrooms',
        db.Column('user_id', db.Integer, db.ForeignKey('users.id')),
        db.Column('chatroom_id', db.Integer, db.ForeignKey('chatrooms.id')),
    )

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    status = db.Column(db.Integer(10))
    # role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    # sessionNum = db.Column(db.Integer(10))
    # picturepool = db.Column(db.String(20000))
    # question = db.Column(db.Integer(11))
    chatrooms = db.relationship('Chatroom',secondary = user_chatroom, 
        backref=db.backref('users', lazy = 'dynamic'))
    msgs = db.relationship('ChatRecord', backref = 'fromWho', lazy = 'dynamic')

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

# record chatroom's memeber
class Chatroom(db.Model):
    __tablename__ = 'chatrooms'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    created_at = db.Column(db.DateTime)

    def __init__(self, created_at):
        self.created_at = created_at

class ChatRecord(db.Model):
    __tablename__ = 'chat_records'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    chatroom_id = db.Column(db.Integer,db.ForeignKey('chatrooms.id'))
    user_id = db.Column(db.Integer,db.ForeignKey('users.id'))
    word = db.Column(db.String(256))
    sentimentalVal = db.Column(db.Float(10))
    retrain = db.Column(db.Boolean)   
    created_at = db.Column(db.DateTime)

    def __init__(self, word, time, fromWho, sentimentalVal, retrain=True):
        self.word = word
        self.time = time
        self.fromWho = fromWho
        self.sentimentalVal = sentimentalVal
        self.retrain = retrain
       
    def __repr__(self):
        return '<Share %r>' % self.word

class sentiDictionary(db.Model):
    __tablename__ = 'sentiDic'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    words = db.Column(db.String(100))
    value = db.Column(db.Float)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
