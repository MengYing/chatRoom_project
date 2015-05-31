from werkzeug.security import generate_password_hash, check_password_hash
from flask.ext.login import UserMixin
from . import db, login_manager
import jieba
from datetime import datetime


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

    # add user_chat: (user, room)
    def join_room(self,room_id):
        room = Chatroom.query.get(room_id)
        if room == None:
            return None
        else:
            self.chatrooms.append(room)
            db.session.commit()
        return self

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
    full = db.Column(db.Boolean)

    def __init__(self):
        self.created_at = datetime.utcnow()
        self.full = False

class ChatRecord(db.Model):
    __tablename__ = 'chat_records'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    chatroom_id = db.Column(db.Integer,db.ForeignKey('chatrooms.id'))
    user_id = db.Column(db.Integer,db.ForeignKey('users.id'))
    word = db.Column(db.String(256))
    sentimentalVal = db.Column(db.Float(10))
    retrained = db.Column(db.Boolean)   
    created_at = db.Column(db.DateTime)

    def __init__(self, word, user_id, chatroom_id, retrained=False):
        self.chatroom_id = chatroom_id
        self.user_id = user_id
        self.word = word
        self.sentimentalVal = SentiDictionary.get_value(word)
        self.retrained = retrained
        self.created_at = datetime.utcnow()

    def __repr__(self):
        return '<Share %r>' % self.word

    @staticmethod
    def update_value(record_id, new_value):
        record = db.query(ChatRecord.sentimentalVal,ChatRecord.retrained).get(record_id)
        record.sentimentalVal = new_value
        record.retrained = True
        db.session.commit()


class SentiDictionary(db.Model):
    __tablename__ = 'sentiDic'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    words = db.Column(db.String(100))
    value = db.Column(db.Float)

    @staticmethod
    def get_value(stringParam):
        value = 0.0
        words = jieba.cut(stringParam, cut_all=False)
        for word in words:
            if word != '\n':
                result = db.session.query(SentiDictionary.value).filter_by(words=word).first()
                if (result):
                    value += result[0]
        return value

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
