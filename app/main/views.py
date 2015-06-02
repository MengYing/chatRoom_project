from flask import *
import random
from datetime import datetime
from . import main
from ..auth.forms import LoginForm
from .. import db
from ..models import User
from ..util import *
import jieba


# @main.route('/', methods=['GET', 'POST'])
# def indextest():
#     return redirect(url_for('auth.login'))

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
    full = Chatroom.query.get(session.get('chatroom_id')).full
    print full
    return render_template('index.html',u_id = u_id, room_id = room_id, full = full )

@main.route('/chat/<msg>', methods = ['GET','POST'])
def chat(msg):
    u_id = session.get('id')
    room_id = request.form["room"]
    record = ChatRecord(msg,u_id,room_id)
    score = SentiDictionary.get_value(msg)
    db.session.add(record)
    db.session.commit()
    return jsonify({"success":True,"chat_id":record.id,"score":score})

@main.route('/modify_value/<id>', methods = ['POST'])
def modify_value(id):
    id = int(id)
    val = float(request.form["score"])
    ChatRecord.update_value(id,val)
    return jsonify({"msg":"update success"})
