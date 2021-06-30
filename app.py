from importlib import import_module
import os
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask import Flask, render_template, Response, request, stream_with_context, url_for, redirect
from flask_socketio import SocketIO, send, emit, join_room, leave_room
from pymongo.errors import DuplicateKeyError

from db import get_teacher, save_teacher
# import camera drivern0-
if os.environ.get('CAMERA'):
    Camera = import_module('camera_' + os.environ['CAMERA']).Camera
else:
    from camera_opencv import Camera

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)
login_manager = LoginManager()
login_manager.init_app(app)

ret = 0


@app.route('/')
def home():
    """Home page"""
    return render_template("home.html")


@app.route('/teacher_login', methods=['GET', 'POST'])
def teacher_login():
    if current_user.is_authenticated:
        return redirect(url_for('teacher'))
    message = ''
    if request.method == 'POST':
        username = request.form.get('username')
        password_input = request.form.get('password')
        teacher = get_teacher(username)

        if teacher and teacher.check_password(password_input):
            login_user(teacher)
            return redirect(url_for('teacher'))
        else:
            message = 'Failed to login'

    return render_template('teacher_login.html', message=message)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('teacher_login'))


@app.route('/signup', methods=['GET', 'POST'])
def teacher_signup():
    if current_user.is_authenticated:
        return redirect(url_for('teacher'))
    message = ''
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        try:
            save_teacher(username, email, password)
            return redirect(url_for('teacher_login'))
        except DuplicateKeyError:
            message = 'User already exist!'

    return render_template('teacher_signup.html', message=message)


@app.route('/teacher')
@login_required
def teacher():
    return render_template('teacher.html')


@app.route('/student_home')
def student_home():

    return render_template('student_home.html')


@app.route('/student')
def student():
    """Video streaming home page."""
    username = request.args.get('username')
    room = request.args.get('room')
    if username and room:
        return render_template('student.html', username=username, room=room)

    return render_template("student.html")


@socketio.on('join_room')
def handle_join_room_event(data):
    app.logger.info("{} has joined the room {}".format(data['username'], data['room']))
    join_room(data['room'])
    socketio.emit('join_room_announcement', data, room=data['room'])


@socketio.on('leave_room')
def handle_leave_room_event(data):
    app.logger.info("{} has left the room {}".format(data['username'], data['room']))
    leave_room(data['room'])
    socketio.emit('leave_room_announcement', data, room=data['room'])


def alert():
    socketio.emit('alert')


# handle_send_message_event
@socketio.on('send_message')
def send_message_event(data):
    app.logger.info("{} {} in room {}".format(data['username'], data['message'], data['room']))
    socketio.emit('receive_message', data, room=data['room'])


def gen(camera):
    """Video streaming generator function."""
    while True:

        frame, ret = camera.get_frame()
        if ret == 1:
            print('disengaged')
            alert()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@app.route('/video_feed')
def video_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(gen(Camera()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@login_manager.user_loader
def load_user(username):
    return get_teacher(username)


if __name__ == '__main__':
    socketio.run(app, debug=True)
    # app.run(debug=True)
