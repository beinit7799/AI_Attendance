import cv2
import os
import pickle
import numpy as np


class FaceCapture:
    def __init__(self, cascade_path='data/haarcascade_frontalface_default.xml'):
        self.video = cv2.VideoCapture(0)
        self.face_cascade = cv2.CascadeClassifier(cascade_path)
        self.faces_data = []
        self.i = 0

    def get_frame(self):
        while True:
            ret, frame = self.video.read()
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
            for (x, y, w, h) in faces:
                crop_img = frame[y:y+h, x:x+w,:]
                resized_img = cv2.resize(crop_img, (50, 50))
                if len(self.faces_data) <= 100 and self.i % 10 == 0:
                    self.faces_data.append(resized_img)
                self.i += 1
                cv2.putText(frame, str(len(self.faces_data)), (50, 50), cv2.FONT_HERSHEY_COMPLEX, 1, (50, 50, 255), 1)
                cv2.rectangle(frame, (x, y), (x+w, y+h), (50, 50, 255), 1)
            return frame
        
    def save_data(self):
        if 'names.pkl' not in os.listdir('data/'):
            names = [self.name] * 100
            with open('data/names.pkl', 'wb') as f:
                pickle.dump(names, f)
        else:
            with open('data/names.pkl', 'rb') as f:
                names = pickle.load(f)
            names = names + [self.name] * 100
            with open('data/names.pkl', 'wb') as f:
                pickle.dump(names, f)

        if 'faces_data.pkl' not in os.listdir('data/'):
            with open('data/faces_data.pkl', 'wb') as f:
                pickle.dump(self.faces_data, f)
        else:
            with open('data/faces_data.pkl', 'rb') as f:
                faces = pickle.load(f)
            faces = np.append(faces, self.faces_data, axis=0)
            with open('data/faces_data.pkl', 'wb') as f:
                pickle.dump(faces, f)

  