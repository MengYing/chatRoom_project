#!/usr/bin/python
#coding:utf-8
from werkzeug.security import generate_password_hash, check_password_hash
from flask.ext.login import UserMixin
from . import db, login_manager
import jieba
import datetime

import time
import unicodedata
import json
import math
import urllib

import ECpredictor as preD
import ECtools as tool

user_chatroom = db.Table('user_chatrooms',
        db.Column('user_id', db.Integer, db.ForeignKey('users.id')),
        db.Column('chatroom_id', db.Integer, db.ForeignKey('chatrooms.id')),
    )


para = [0.3, 0.2, 0.2, 0.3, 0.15, 0.15, 0.35, 0.35]    #[C, SC, CX, N, D, P, I, A]
PD = 0.5
S = 0.1
R = 0.1
P1 = [0, 0, 0, 0]
P2 = [0, 0, 0, 0]
labels = [0, 0, 0, 0, 0, 0]

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
    timeStr = db.Column(db.String(256))

    def __init__(self):
        self.created_at = "2015-06-09 12:03:28"
        self.full = False
        self.timeStr = int(datetime.datetime.now().strftime("%s")) * 1000


class ChatRecord(db.Model):
    __tablename__ = 'chat_records'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    chatroom_id = db.Column(db.Integer,db.ForeignKey('chatrooms.id'))
    user_id = db.Column(db.Integer,db.ForeignKey('users.id'))
    word = db.Column(db.String(256))
    sentimentalVal = db.Column(db.Float(10))
    retrained = db.Column(db.Boolean)   
    created_at = db.Column(db.DateTime)
    timeStr = db.Column(db.String(256))

    def __init__(self, word, user_id, chatroom_id, retrained=True):
        self.chatroom_id = chatroom_id
        self.user_id = user_id
        self.word = word
        # self.sentimentalVal = SentiDictionary.get_value(word)
        self.sentimentalVal = 0
        self.retrained = retrained
        self.created_at = "2015-06-09 12:03:28"
        self.timeStr = int(datetime.datetime.now().strftime("%s")) * 1000
    
    def __repr__(self):
        return '<Share %r>' % self.word

    @staticmethod
    def update_value(record_id, new_value):
        record = ChatRecord.query.get(record_id)
        record.sentimentalVal = new_value
        record.retrained = False

        db.session.commit()
    @staticmethod
    def update_score(record_id, new_value):
        record = ChatRecord.query.get(record_id)
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
        return setSentense(stringParam)

    @staticmethod
    def get_dictionaryValue(stringParam):
        return dictionaryBased(stringParam)

    @staticmethod
    def feedback_brian(stringParam, label):
        feedbackToBrian(stringParam, label)

    @staticmethod
    def feedback_adjuster(label):
        adjuster(label)
        

# ########### Brian ###########


def checkStrangeSentence(qry):
    # check if sentence is strange sentence
    strangeProportion = 2./3
    wordNumInQry = float(sum(qry.values()))
    wordIG = {}
    with open('./app/wordList') as wordList:
        for i in wordList:
            wordIG = json.loads(i)
    notInWdList = 0.
    for word in qry:
        if word not in wordIG:
            notInWdList += 1
    if notInWdList/wordNumInQry > strangeProportion: return True
    else: return False


def googleSearchMethod(sentence):
    #using google search service
    emotions = ['開心', '難過', '生氣', '抱歉']
    googleList =[]
    for i in range(5): googleList.append(0.)
    sentence = sentence.encode('utf-8')
    totalCount = 0.
    for emotion in emotions:
        qrySentence = sentence+' '+emotion
        query = urllib.urlencode({'q': qrySentence})
        url = 'http://ajax.googleapis.com/ajax/services/search/web?v=1.0&%s' % query
        search_response = urllib.urlopen(url)
        search_results = search_response.read()
        results = json.loads(search_results)
        data = results['responseData']
        count = int(str(data['cursor']['resultCount']).replace(',', ''))
        if emotion == '開心': googleList[4] = count
        elif emotion == '難過': googleList[1] = count
        elif emotion == '生氣': googleList[3] = count
        elif emotion == '抱歉': googleList[2] = count
        totalCount += count
    for i in range(5):
        print i
        googleList[i] = googleList[i]/totalCount
    googleList[0] = .3
    
    temp = 0.0
    for i in range(5):
        temp += googleList[i]

    for i in range(5):
        googleList[i] /= temp

    return googleList


def informationGainWeight(qry):
    #given a k times weight by information gain
    #parameter
    k = 1.5
    wordIG = {}
    with open('./app/wordList') as wordList:
        for i in wordList:
            wordIG = json.loads(i)
# wordIG  100052
# >0.00001 99621
# >0.0001  14033
# >0.001   932
# >0.01    60
# >0.1     2
    featureSelect = []
    for word in wordIG:
        if wordIG[word] > 0.001:
            featureSelect.append(word)
    for word in qry:
        qry[word] = qry[word]*k
    return qry


def cosineSimilarity(qry, dic):
    # similarity between 2 vectors
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
    # clear stopwords and symbol
    stopWord = [u'一',u'不',u'之',u'也',u'了',u'了',u'人',u'他',u'你',
                u'個',u'們',u'在',u'就',u'我',u'是',u'有',u'的',u'而',
                u'要',u'說',u'這',u'都',u' ',
                u'~', u'!', u'.', u'(', u')', u':', u'～', u'?', u'_', u'=',u'＝',
                u'\"',u'．',u'。',u'-','...',
                u'\u3002', u'\uff1f', u'\uff01', u'\uff0c', u'\u3001',
                u'\uff1b', u'\uff1a', u'\u300c', u'\u300d', u'\u300e', u'\u300f',
                u'\u2018', u'\u2019', u'\u201c', u'\u201d', u'\uff08', u'\uff09',
                u'\u3014', u'\u3015', u'\u3010', u'\u3011', u'\u2014', u'\u2026',
                u'\u2013', u'\uff0e', u'\u300a', u'\u300b', u'\u3008', u'\u3009'
                ]
    noStop = {}
    for i in dic:
        if i not in stopWord:
            noStop[i] = dic[i]
    return noStop


def setSentense(sentence):  
    corpusDic = []
    with open('./app/Corpus.json') as corpus:
        #key = tag, ID, dic
        for line in corpus:
            corpusDic.append(json.loads(line))

    print sentence
    words = jieba.cut(sentence, cut_all=False)
    qry = {}
    for word in words:
        if word not in qry:
            qry[word] = 1
        else:
            qry[word] += 1
    
    
    qry = clearStopWord(qry)
# True: strange sentence so we use google search for clearifying 
    if checkStrangeSentence(qry):
        #print "GoogleSearch Method..."
        googleList = googleSearchMethod(sentence)
        return googleList
# False: Retrieve method    
    else:
        #print "Retrieve Method..."
        qry = informationGainWeight(qry)
        rank={}
        for doc in corpusDic:
            score = cosineSimilarity(qry, doc['dic'])
            ID = doc['ID']
            tag = doc['tag']
            rank[ID] = {'tag':tag, 'score':score}
            if len(rank) > 10 :
                rank.pop(min(rank, key = lambda x: rank.get(x).get('score')))

        retrieveList = []
        for i in range(5): retrieveList.append(0.)
        retrieveList[0] = 1.2
        #none = 0, sad = 1, sorry = 2, angry = 3, happy = 4
        num = 1
        for i in range(10):
            ID = max(rank, key = lambda x: rank.get(x).get('score'))
            data = rank.pop(ID)
            if data['score'] >= 0.3:
                retrieveList[data['tag']] += (1./num)
            #print str(ID)+'\t'+str(data['tag'])+'\t'+str(data['score'])
            num += 1
        temp = 0.0
        for i in range(5):
            temp += retrieveList[i]

        for i in range(5):
            retrieveList[i] /= temp

        return retrieveList

# ########### Brian feedback #########


def feedbackToBrian(sentence, label):
    symbol = [u'~', u'!', u'.', u'(', u')', u':', u'～', u'?', u'_', u'=',u'＝',
              u'\"',u'．',u'。',u'-',u'，',u' ',
              u'\u3002', u'\uff1f', u'\uff01', u'\uff0c', u'\u3001',
              u'\uff1b', u'\uff1a', u'\u300c', u'\u300d', u'\u300e', u'\u300f',
              u'\u2018', u'\u2019', u'\u201c', u'\u201d', u'\uff08', u'\uff09',
              u'\u3014', u'\u3015', u'\u3010', u'\u3011', u'\u2014', u'\u2026',
              u'\u2013', u'\uff0e', u'\u300a', u'\u300b', u'\u3008', u'\u3009',
              ]

    docnum = 0
    with open('./app/Corpus.json') as corpus:
        corpusDic = []
        for line in corpus:
            corpusDic.append(json.loads(line))
        docnum = len(corpusDic)
    jsonFile = open('./app/feedback.json','a')
    words = list(sentence)
    denoise = []
    for j in range(len(words)):
        if words[j] not in symbol:
            denoise.append(words[j])
        elif len(denoise) > 0 and denoise[-1] != ' ':
            denoise.append(' ')
    sentence = ''.join(denoise)
    words = jieba.cut(sentence, cut_all=False)
    d = {}
    for word in words:
        if word not in d:
            d[word] = 1
        else:
            d[word] += 1
    print ' '.join(d)
    dic = {'ID':docnum+1, 'dic':d, 'tag':label}
    jsonFile.write(json.dumps(dic)+"\n")


# ########### yatai ###########
def adjuster(Finlabel):
    global para, PD, R, P1, P2, S, labels
    para = tool.adjuster(para, S, labels, Finlabel)
    print para


def dictionaryBased(sentense):
    # ==== global parameters ====
    print "dictionaryBased"
    global para, PD, R, P1, P2, S, labels
    getList = preD.taiMethod(sentense, para, PD, R, P1, P2)
    emo = getList[:4]
    labels = getList[4:]
    P2 = P1[:]
    P1 = emo[:]    # must to be changed the final prediction
    
    return tool.finalVec(emo, R)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
