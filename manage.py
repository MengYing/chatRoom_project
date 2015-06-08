#!/usr/bin/env python
import os
from app import create_app, db
from flask.ext.script import Server, Manager, prompt_bool
from flask.ext.socketio import SocketIO, emit, join_room, leave_room, \
    close_room, disconnect
from flask import request
import time
from threading import Thread
app = create_app(os.getenv('FLASK_CONFIG') or 'default')
# manager = Manager(app)
# manager.add_command('runserver', Server(host='0.0.0.0', port=3000))
socketio = SocketIO(app)

# @main.route('/', methods=['GET', 'POST'])
# def indextest():
#     return redirect(url_for('auth.login'))

thread = None
user_id = []
room_num = 0
sender_id = 0


@socketio.on('join room')
def test_getroom(message):
    print "join room"
    print message
    join_room(message['room'])
    emit('set room',{ 'room':message['room'],'sender':message['u_id'] })


@socketio.on('set msg')
def test_setmsg(data):
    print "set msg"
    print data
    emit('set msg',{'sender': data['sender'], 'chat_id': data['chat_id'], 'msg':data['msg'], 'score':data['score']}, room = data['room'])


@socketio.on('update color')
def test_updatecolor(data):
    print "update color"
    print data
    emit('update color',{'sender': data['sender'], 'chat_id': data['chat_id'], 'score': data['score']}, room = data['room'])


@socketio.on('start chat')
def test_startchat(data):
    print "start chat"
    print data
    emit('start chat',{'name_hash':data["name_hash"]},room = data["room"])


@socketio.on('disconnect')
def test_disconnect():
    room = list(request.namespace.rooms)[0]
    emit('quit room',{},room = room)
    print room
    print('Client disconnected')


# @manager.command
# def initdb():
#     '''Creates all database tables.'''
#     db.create_all()


# @manager.command
# def dropdb():
#     '''Drops all database tables.'''
#     if prompt_bool('Are you sure to drop your databse?'):
#         db.drop_all()

if __name__ == '__main__':
    # manager.run()
    socketio.run(app, host='0.0.0.0', port=3000)
