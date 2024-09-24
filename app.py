from flask import Flask, render_template, Response
from attendance import Attendance
import cv2

app = Flask(__name__)
camera = Attendance()


@app.route('/')
def index():
    return render_template('attendees_dashboard.html')

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

if __name__ == '__main__':
    app.run(debug=True)
