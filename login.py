from flask import Flask, render_template, url_for, redirect, Response
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError
from flask_bcrypt import Bcrypt
import sqlite3
import subprocess
from attendance import Attendance
import cv2
import pickle
import numpy as np
import os
from datetime import datetime
from test import FaceCapture

app = Flask(__name__)
camera = Attendance()
camera2=FaceCapture()
bcrypt = Bcrypt(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False 
db = SQLAlchemy(app)
app.config['SECRET_KEY'] = 'secretkey'


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(db.Model, UserMixin):
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=False)
   


    def validate_username(self, username):
        existing_user_username = User.query.filter_by(
            username=username.data).first()
        if existing_user_username:
            raise ValidationError(
                'That username already exists. Please choose a different one.')

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))



class RegisterForm(FlaskForm):
    username = StringField(validators=[
                           InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})

    password = PasswordField(validators=[
                             InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Password"})

    submit = SubmitField('Register')

    def validate_username(self, username):
        existing_user_username = User.query.filter_by(
            username=username.data).first()
        if existing_user_username:
            raise ValidationError(
                'That username already exists. Please choose a different one.')

class LoginForm(FlaskForm):
    username = StringField(validators=[
                           InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})

    password = PasswordField(validators=[
                             InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Password"})

    submit = SubmitField('Login')
@app.route('/')
def home():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user)
                return redirect(url_for('dashboard'))
    return render_template('login.html', form=form)

@app.route('/dashboard', methods=['GET', 'POST'])
#@login_required
def dashboard():
    return render_template('admin_dashboard.html')

@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('admin_dashboard.html'))

@ app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data)
        new_user = User(username=form.username.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))

    return render_template('register.html', form=form)


@ app.route('/attendees_dashboard')
def attendees_dashboard():
   return render_template('attendees_dashboard.html')



@app.route('/')
def index():
     return render_template('admin_dashboard.html')

@app.route('/admin_dashboard', methods=['POST'])
def run_python_script():
     result = subprocess.check_output(['python', 'train.py'], universal_newlines=True)
     return result

def generate_frames():
    while True:
        frame = camera.get_frame()
        ret, jpeg = cv2.imencode('.jpg', frame)
        frame_bytes = jpeg.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n\r\n')

@app.route('/video')
def video():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

def train():
    

    video=cv2.VideoCapture(0)
    facedetect=cv2.CascadeClassifier('data/haarcascade_frontalface_default.xml')

    faces_data=[]

    i=0

    name=input("Enter Your Name: ")

    while True:
        ret,frame=video.read()
        gray=cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces=facedetect.detectMultiScale(gray, 1.3 ,5)
        for (x,y,w,h) in faces:
            crop_img=frame[y:y+h, x:x+w, :]
            resized_img=cv2.resize(crop_img, (50,50))
            if len(faces_data)<=100 and i%10==0:
                faces_data.append(resized_img)
            i=i+1
            cv2.putText(frame, str(len(faces_data)), (50,50), cv2.FONT_HERSHEY_COMPLEX, 1, (50,50,255), 1)
            cv2.rectangle(frame, (x,y), (x+w, y+h), (50,50,255), 1)
        cv2.imshow("Frame",frame)
        k=cv2.waitKey(1)
        if k==ord('q') or len(faces_data)==100:
            break
    video.release()
    cv2.destroyAllWindows()

    faces_data=np.asarray(faces_data)
    faces_data=faces_data.reshape(100, -1)


    if 'names.pkl' not in os.listdir('data/'):
        names=[name]*100
        with open('data/names.pkl', 'wb') as f:
            pickle.dump(names, f)
    else:
        with open('data/names.pkl', 'rb') as f:
            names=pickle.load(f)
        names=names+[name]*100
        with open('data/names.pkl', 'wb') as f:
            pickle.dump(names, f)

    if 'faces_data.pkl' not in os.listdir('data/'):
        with open('data/faces_data.pkl', 'wb') as f:
            pickle.dump(faces_data, f)
    else:
        with open('data/faces_data.pkl', 'rb') as f:
            faces=pickle.load(f)
        faces=np.append(faces, faces_data, axis=0)
        with open('data/faces_data.pkl', 'wb') as f:
            pickle.dump(faces, f)
    return frame
            
def generate_frames_1():
    while True:
        frame =camera2.get_frame()
        ret, jpeg = cv2.imencode('.jpg', frame)
        frame_bytes = jpeg.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n\r\n')

@app.route('/video_train')
def video_train():
    return Response(generate_frames_1(), mimetype='multipart/x-mixed-replace; boundary=frame')



   

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)