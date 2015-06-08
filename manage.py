#!/usr/bin/env python
import os
from app import create_app, db
from flask.ext.script import Server, Manager, prompt_bool
from flask.ext.socketio import SocketIO, emit, join_room, leave_room, \
    close_room, disconnect

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
# manager = Manager(app)
# manager.add_command('runserver', Server(host='0.0.0.0', port=3000))
socketio = SocketIO(app)

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
