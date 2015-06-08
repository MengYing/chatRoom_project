#!/usr/bin/python
#coding:utf-8
from werkzeug.security import generate_password_hash, check_password_hash
from flask.ext.login import UserMixin
from . import db, login_manager
import jieba
from datetime import datetime
import unicodedata
import json
import math

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
    chatrooms = db.relationship('Chatroom',secondary = user_chatroom, backref=db.backref('users'))
    msgs = db.relationship('ChatRecord', backref = 'fromWho')

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

    def __init__(self, word, user_id, chatroom_id, retrained=True):
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
        record = ChatRecord.query.get(record_id)
        record.sentimentalVal = new_value
        record.retrained = False
        db.session.commit()


class SentiDictionary(db.Model):
    __tablename__ = 'sentiDic'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    words = db.Column(db.String(100))
    value = db.Column(db.Float)

    @staticmethod
    def get_value(stringParam):
        # value = 0.0
        # words = jieba.cut(stringParam, cut_all=False)
        # for word in words:
        #     if word != '\n':
        #         result = db.session.query(SentiDictionary.value).filter_by(words=word).first()
        #         if (result):
        #             value += result[0]
        # print value
        # return value
        return setSentense(stringParam)


def IDFWeighting(dic, totalNumber):
    for vocabKey, cnt in dic.items():
        cnt = math.log(totalNumber/cnt)
    return dic


def TFIDFWeighting(vec, idf):
    for vocabKey, vocCnt in vec.items():
        if vocabKey in idf:
            vocCnt = vocCnt * idf[vocabKey]
    return vec


def OkapiNormalize(vec):
    b = 0.75
    k = 2
    avgDocLen = 1378
    docLen = 0
    for i in vec:
        docLen += vec[i]
    for i in vec:
        vec[i] = (1+k)*vec[i]/(vec[i]+k*(1-b+b*docLen/avgDocLen))
    return vec


def cosineSimilarity(qry, dic):
    qryDis = 0.
    dicDis = 0.
    vecDot = 0.
    if len(qry) == 0 or len(dic) == 0:
        return 0.
    for vocabKey, cnt in qry.items():
        qryDis += math.pow(cnt, 2)
    qryDis = math.sqrt(qryDis)
    for vocabKey, cnt in dic.items():
        dicDis += math.pow(cnt, 2)
    dicDis = math.sqrt(dicDis)
    for VocabKey, Cnt in qry.items():
        if VocabKey in dic:
            vecDot += Cnt * dic[VocabKey]
    return vecDot/(qryDis*dicDis)


def clearStopWord(dic):
    stopWord = [u'一',u'不',u'之',u'也',u'了',u'了',u'人',u'他',u'你',
                    u'個',u'們',u'在',u'就',u'我',u'是',u'有',u'的',u'而',
                    u'要',u'說',u'這',u'都',u' ']
    noStop = {}
    for i in dic:
        if i not in stopWord:
            noStop[i] = dic[i]
    return noStop


def setSentense(sentence):  
    stopWord = [u'一',u'不',u'之',u'也',u'了',u'了',u'人',u'他',u'你',
                    u'個',u'們',u'在',u'就',u'我',u'是',u'有',u'的',u'而',
                    u'要',u'說',u'這',u'都',u' ']
    corpusDic = []
    with open('./app/Corpus.json','r') as corpus:
        #key = tag, ID, dic
        for line in corpus:
            corpusDic.append(json.loads(line))
    #print len(corpusDic)
    numDoc = 18939.
    idf = {}
    for doc in corpusDic:
        for i in doc['dic']:
            if i in stopWord:
                continue
            if i not in idf:
                idf[i] = doc['dic'][i]
            else:
                idf[i] += doc['dic'][i]
    idf = IDFWeighting(idf, numDoc)

    for doc in corpusDic:
        doc['dic'] = OkapiNormalize(doc['dic'])
        doc['dic'] = TFIDFWeighting(doc['dic'], idf)

    # print sentence
    words = jieba.cut(sentence, cut_all=False)
    qry = {}
    for word in words:
        if word not in qry:
            qry[word] = 1
        else:
            qry[word] += 1
    qry = clearStopWord(qry)
    qry = OkapiNormalize(qry)
    qry = TFIDFWeighting(qry, idf)
    rank={}
    for doc in corpusDic:
        score = cosineSimilarity(qry, doc['dic'])
        ID = doc['ID']
        tag = doc['tag']
        rank[ID] = {'tag':tag, 'score':score}
        if len(rank) > 10 :
            rank.pop(min(rank, key = lambda x: rank.get(x).get('score')))

    label = {'happy':0, 'lucky':0, 'hate':0, 'sad':0,'sorry':0,'none':1}
    #none = 0, sad = 1, sorry = 2, angry = 3, happy,lucky = 4

    for i in range(10):
        ID = max(rank, key = lambda x: rank.get(x).get('score'))
        data = rank.pop(ID)
        if data['score'] >= 0.2:
            if data['tag'] in label:
                label[data['tag']] += 1
        # print str(ID)+'\t'+data['tag']+'\t'+str(data['score'])
    sentiment = max(label, key = lambda x: label.get(x))
    if sentiment == 'none':
        return 0.0
    elif sentiment == 'sad':
        return 1.0
    elif sentiment == 'sorry':
        return 2.0
    elif sentiment == 'hate':
        return 3.0
    elif sentiment == 'happy' or sentiment == 'lucky':
        return 4.0


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
