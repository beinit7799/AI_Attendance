from sklearn.neighbors import KNeighborsClassifier
import cv2
import pickle
import numpy as np
import os
import csv
import time
from datetime import datetime
from win32com.client import Dispatch

class Attendance:
    def __init__(self):
        self.video = cv2.VideoCapture(0) # put 0 for webcam or url for ip camera ( camera app : ip webcam)
        self.facedetect = cv2.CascadeClassifier('data/haarcascade_frontalface_default.xml')
        
        with open('data/names.pkl', 'rb') as w:
            self.LABELS = pickle.load(w)
        with open('data/faces_data.pkl', 'rb') as f:
            self.FACES = pickle.load(f)

        print('Shape of Faces matrix --> ', self.FACES.shape)

        self.knn = KNeighborsClassifier(n_neighbors=5)
        self.knn.fit(self.FACES, self.LABELS)

        self.COL_NAMES = ['NAME', 'TIME']

    def get_frame(self):
        ret, frame = self.video.read()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.facedetect.detectMultiScale(gray, 1.3, 5)
        ts = time.time()
        date = datetime.fromtimestamp(ts).strftime("%d-%m-%Y")
        timestamp = datetime.fromtimestamp(ts).strftime("%H:%M-%S")
        exist = None
        attendance = []
        for (x, y, w, h) in faces:
            crop_img = frame[y:y + h, x:x + w, :]
            resized_img = cv2.resize(crop_img, (50, 50)).flatten().reshape(1, -1)
            output = self.knn.predict(resized_img)
            exist = os.path.isfile("Attendance/Attendance_" + date + ".csv")
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 1)
            cv2.rectangle(frame, (x, y), (x + w, y + h), (50, 50, 255), 2)
            cv2.rectangle(frame, (x, y - 40), (x + w, y), (50, 50, 255), -1)
            cv2.putText(frame, str(output[0]), (x, y - 15), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 1)
            cv2.rectangle(frame, (x, y), (x + w, y + h), (50, 50, 255), 1)
            attendance = [str(output[0]), str(timestamp)]
        
        if exist:
            with open("Attendance/Attendance_" + date + ".csv", "a+") as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(attendance)
            csvfile.close()
        else:
            
            with open("Attendance/Attendance_" + date + ".csv", "a+") as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(self.COL_NAMES)
                writer.writerow(attendance)
            csvfile.close()

        return frame

    def release(self):
        self.video.release()
