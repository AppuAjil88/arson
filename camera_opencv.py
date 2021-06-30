import os
import cv2
from base_camera import BaseCamera
from util.analysis_server import analysis

ana = analysis()
faceCascade = cv2.CascadeClassifier('haarcascade_frontalface_alt.xml')


class Camera(BaseCamera):
    video_source = 0
    ctr=0
    ctr1=0

    def __init__(self):
        if os.environ.get('OPENCV_CAMERA_SOURCE'):
            Camera.set_video_source(int(os.environ['OPENCV_CAMERA_SOURCE']))
        super(Camera, self).__init__()

    @staticmethod
    def set_video_source(source):
        Camera.video_source = source

    @staticmethod
    def frames():
        camera = cv2.VideoCapture(Camera.video_source)
        if not camera.isOpened():
            raise RuntimeError('Could not start camera.')

        while True:
            # read current frame
            _, img = camera.read()
            bm=ana.detect_face(img)
            res=0
            faces=faceCascade.detectMultiScale(img)
            if(len(faces)!= 0):
                if(bm<0.25):
                    Camera.ctr1=Camera.ctr1+1
                    if(Camera.ctr1>360):
                        res=1
                        Camera.ctr1=0
                else:
                    Camera.ctr1=0
            elif(len(faces)==0):
                Camera.ctr=Camera.ctr+1
                if(Camera.ctr>360):
                    res=1
                    Camera.ctr=0
            # encode as a jpeg image and return it
            yield (cv2.imencode('.jpg', img)[1].tobytes(),res)