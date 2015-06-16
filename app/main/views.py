from gevent import monkey
monkey.patch_all()

from flask import *
import random
from datetime import datetime
from . import main
from ..auth.forms import LoginForm
from .. import db
from ..models import User
from ..util import *
import jieba
from flask.ext.socketio import SocketIO, emit, join_room, leave_room, \
    close_room, disconnect
from time import time
import datetime
import app.ECnewer as newl

scoreVectorPrevious = [0, 0, 0, 0]


@main.route('/label', methods=['GET'])
def label():
    print "enter main.label"
    try:
        print "enter main.label try"
        print session.get('id')
        print getpic(session.get('id'))
        pic, idx, ttl, ques = getpic(session.get('id'))
    except IndexError:
        session.clear()
        form = LoginForm()
        print "enter main.label - except"
        return redirect(url_for('auth.login'))

    if pic is None:
        session.clear()
        return render_template('end.html')
    print 'start by', pic
    
    userid = session.get('id')[0]
    user = User.query.filter_by(id=userid)[0]
    quesNum = user.progress / 100 + 1
    question = Questions.query.filter_by(id=quesNum)[0].statement
    return render_template('label.html', pic=pic, idx=idx, ttl=ttl, question=question)


@main.route('/newpic', methods=['GET'])
def newpic():
    pic, idx, ttl, ques = getpic(session.get('id'))
    if pic is None:
        return render_template('end.html')
    print 'new', pic, '##', ques
    return jsonify({'pic': pic, 'idx': idx, 'ttl': ttl, 'ques': ques})


@main.route('/record/<pictureNum>/<duration>/<answer>', methods=['POST'])
def data(pictureNum, duration, answer):
    # session['id'] = random.randint(0, 50)
    print type(pictureNum), len(pictureNum)
    if len(pictureNum) < 13:
        print 'enter here'
        return render_template('end.html')

    now = datetime.now()
    labelTime = now.strftime("%Y%m%d-%H%M")
    
    userid = session.get('id')[0]
    user = User.query.filter_by(id=userid)[0]
    question = user.progress / 100 + 1
    user.progress += 1
    data = Data(labelTime=labelTime, question=question,
                pictureNum=pictureNum, userid=userid, duration=duration, answer=answer)
    db.session.add(data)
    db.session.commit()

    return redirect(url_for('main.newpic'))


@main.route('/basePrediction/<stringParam>', methods=['GET'])
def basePrediction(stringParam):
    value = 0.0
    words = jieba.cut(stringParam, cut_all=False)
    for word in words:
        if word != '\n':
            print word
            if (db.session.query(SentiDictionary.value).filter_by(words=word).first()):
                value += db.session.query(SentiDictionary.value).filter_by(words=word).first()[0]
            
    return render_template('end.html', predict=value)


@main.route('/testpage', methods=['GET'])
def testpage():
    return render_template('auth/test.html')


@main.route('/chatroom', methods=['GET'])
def index():
    u_id = session.get('id')
    room_id = session.get('chatroom_id')
    full = Chatroom.query.get(room_id).full
    name_list = Chatroom.query.get(room_id).users
    name_hash = {}
    for i in name_list:
        name_hash[i.id] = i.username
    return render_template('index.html',u_id = u_id, room_id = room_id, full = full ,name_hash = name_hash)

@main.route('/chat2/<msg>', methods = ['GET','POST'])
def chat2(msg):
    u_id = session.get('id')
    room_id = request.form["room"]
    record = ChatRecord(msg, u_id, room_id)
    # score = SentiDictionary.get_value(msg)
    # print "score: ", score
    db.session.add(record)
    db.session.commit()
    time=ChatRecord.query.filter_by(id=record.id, chatroom_id=room_id, user_id=u_id, word=msg).first()
    print "chat2", record.id, time.created_at, time.timeStr
    print "user_id:",u_id,"chatroom_id", room_id
    # temp = ''
    # temp = str(time.created_at)
    # print "type of temp:", type(temp)
    # d = datetime.datetime.strptime(temp, '%Y-%m-%d %H:%M:%S')
    # d =int(datetime.datetime.now().strftime("%s")) * 1000 
    # time_second = time.mktime(d.timetuple()) + 1e-6 * d.microsecond
    # print d
    return jsonify({"success":True,"chat_id":record.id,"score":0,"timeStamp":time.timeStr})



@main.route('/calculateScore/<msg>/<time>', methods = ['GET','POST'])
def calculateScore(msg, time):
    # previous score Vector
    global scoreVectorPrevious
    print "here time!!", time
    u_id = session.get('id')
    room_id = request.form["room"]
    record = ChatRecord.query.filter_by(chatroom_id=room_id, user_id=u_id, word=msg, timeStr=time).first()
    print u_id, room_id, record.id
    # record = ChatRecord(msg, u_id, room_id)
    score_Brain = []
    score_yai = []
    score_Brain = SentiDictionary.get_value(msg)
    print "score_Brain", score_Brain
    score_yai = SentiDictionary.get_dictionaryValue(msg)
    print "score_yai", score_yai
    tempScore = [x+y for x, y in zip(score_yai, score_Brain)]
    print "max(tempScore)", max(tempScore)
    score = tempScore.index(max(tempScore))
    print score
    SentiDictionary.feedback_adjuster(score)
    # here can calculate the vector and still return a score.
    ##
    ##
    ##
    
    ChatRecord.update_score(record.id,score)
    print "calculateScore"
    print "score: ", score
    # db.session.add(record)
    # db.session.commit()
    return jsonify({"success":True, "chat_id":record.id, "score":score})


    # id = int(id)
    # val = float(request.form["score"])
    # ChatRecord.update_value(id,val)
    
    # print ChatRecord.query.get(id).word
    # return jsonify({"msg":"update success"})

@main.route('/modify_value/<id>', methods=['POST'])
def modify_value(id):
    id = int(id)
    val = int(request.form["score"])
    ChatRecord.update_value(id, val)
    sentenceTemp = ChatRecord.query.get(id).word
    print "sentenceTemp:", sentenceTemp, val
    SentiDictionary.feedback_brian(sentenceTemp, val)
    if(val != 0):
        newl.newLearn(sentenceTemp, val)
    # print ChatRecord.query.get(id).word
    return jsonify({"msg": "update success"})
