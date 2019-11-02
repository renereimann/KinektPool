import cv2
import numpy as np
from pykinect2 import PyKinectV2
from pykinect2.PyKinectV2 import *
from pykinect2 import PyKinectRuntime
import time
import configparser

class KinectFrame(object):
    def __init__(self, top_cut, bottom_cut, left_cut, right_cut, scale):
        self.cut = [top_cut, bottom_cut, left_cut, right_cut]
        self.scale = scale

    def getGrayFrame(self):
        raise NotImplemented("This is not implemented")

    def getFrame(self):
        gray = self.getGrayFrame()
        gray *= self.scale
        gray = gray[self.cut[0]:-self.cut[1],self.cut[2]:-self.cut[3]]
        gray = gray[::-1]
        # HoughCircles needs uint8 (values 0 to 255) image,
        gray = np.array(gray/16, dtype=np.uint8)
        return gray
        
class InfraredFrame(KinectFrame):
    def __init__(self, top_cut = 60, bottom_cut = 120, left_cut = 40, right_cut = 10, scale = 1):
        KinectFrame.__init__(self, top_cut, bottom_cut, left_cut, right_cut, scale)
        self.kinect = PyKinectRuntime.PyKinectRuntime(PyKinectV2.FrameSourceTypes_Infrared)
        self.dp, self.minDist, self.param1, self.param2, self.minR, self.maxR = 1.2, 6, 50, 24, 5, 10
        
    def getGrayFrame(self):
        frame = self.kinect.get_last_infrared_frame()
        #kinect gives unsigned int16 (values 0 to 65535)
        frame = frame.astype(np.uint16)
        gray = np.reshape(frame, (self.kinect.infrared_frame_desc.Height, self.kinect.infrared_frame_desc.Width))
        return gray
    def hasNewFrame(self):
        return self.kinect.has_new_infrared_frame()

class ColorFrame(KinectFrame):
    def __init__(self, top_cut =145, bottom_cut = 260, left_cut = 375, right_cut = 200, scale = 7):
        KinectFrame.__init__(self, top_cut, bottom_cut, left_cut, right_cut, scale)
        self.kinect = PyKinectRuntime.PyKinectRuntime(PyKinectV2.FrameSourceTypes_Color)
        self.dp, self.minDist, self.param1, self.param2, self.minR, self.maxR = 1.2, 15, 50, 23, 15, 20
        
    def getGrayFrame(self):
        frame = self.kinect.get_last_color_frame()
        #kinect gives unsigned int16 (values 0 to 65535)
        frame = frame.astype(np.uint16)
        frame = np.reshape(frame, (self.kinect.color_frame_desc.Height, self.kinect.color_frame_desc.Width, 4))
        gray = cv2.cvtColor(frame[:,:,:-1], cv2.COLOR_BGR2GRAY)
        return gray
    def hasNewFrame(self):
        return self.kinect.has_new_color_frame()

class Beamer(object):
    def __init__(self, top, bottom, left, right):
        pass

"""
ToDo Liste:

* Farbe der Kugeln erkennen (Halb/Voll)
* Ball Erkennung mit mehrern Frames
* Pocket Erkennung
* Config File lesen und benutzen (Done?)
* Abfragen Auflösungsunabhängig
* Ausgabe Bild
* Punktestand
* Que Erkennung
* Spiele erstellen
* Bildkorrektur wegen Spiegel

"""

kin = InfraredFrame()

cfg = configparser.ConfigParser()
cfg.read("pool.cfg")
print(cfg.getint("SettingsInfraRed", "left"))
dta = [0,0,0,0,0,0]

while True:
    if kin.hasNewFrame():
        gray = kin.getFrame()
        try:
            # Detects circles in an image, gives back tuples of radius and center per circle
            circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, kin.dp, kin.minDist, np.array([]), kin.param1, kin.param2, kin.minR, kin.maxR)
        except AttributeError as e:
            # if not successful, print error message
            circles = None
        beam = gray#np.ones_like(gray)*255
        cv2.rectangle(beam, (0, 225), (20, 250), [255,255,255],1)
        cv2.rectangle(beam, (220, 0), (240, 15), [255,255,255],1)
        cv2.rectangle(beam, (0, 0), (25, 20), [255,255,255],1)
        cv2.rectangle(beam, (220, 230), (240, 250), [255,255,255],0)
        cv2.rectangle(beam, (425, 0), (455, 25), [255,255,255],0)
        cv2.rectangle(beam, (435, 220), (455, 255), [255,255,255],0)
        
        cv2.putText(beam,str(dta[0]), (0,17), cv2.FONT_HERSHEY_SIMPLEX, 0.6, 255)
        cv2.putText(beam,str(dta[1]), (220,11), cv2.FONT_HERSHEY_SIMPLEX, 0.4, 255)
        cv2.putText(beam,str(dta[4]), (430,17), cv2.FONT_HERSHEY_SIMPLEX, 0.6, 255)
        cv2.putText(beam,str(dta[2]), (0,240), cv2.FONT_HERSHEY_SIMPLEX, 0.6, 255)
        cv2.putText(beam,str(dta[3]), (220,240), cv2.FONT_HERSHEY_SIMPLEX, 0.4, 255)
        cv2.putText(beam,str(dta[5]), (440,240), cv2.FONT_HERSHEY_SIMPLEX, 0.6, 255)

        cv2.putText(beam,str(dta), (0,140), cv2.FONT_HERSHEY_SIMPLEX, 0.7, 0)
        if circles is not None and len(circles) > 0:
            circles = np.round(circles[0, :]).astype("int")
            for (x, y, r) in circles:
                # print circles on the image
                if x <= 25  and y <= 20:
                    print("obenlinks")
                    dta[0] += 1
                elif x>=220 and x <= 240 and y <= 15:
                    print("obenmitte")
                    dta[1] += 1
                elif x < 20 and y > 225:
                    print("untenlinks")
                    dta[2] += 1
                elif x >= 220 and y > 230 and x <= 250:
                    print("untenmitte")
                    dta[3] += 1
                elif x > 425 and y < 25:
                    print("obenrechts")
                    dta[4] += 1
                elif x > 435 and y > 220:
                    print("untenrechts")
                    dta[5] += 1
                cv2.circle(beam, (x, y), r, (0, 255, 0), 4)
                cv2.rectangle(gray, (x - 1, y - 1), (x + 1, y + 1), (255, 255, 255), -1)
                
        # for debugging show the image
        cv2.namedWindow("frame", cv2.WND_PROP_FULLSCREEN)
        cv2.setWindowProperty("frame",cv2.WND_PROP_FULLSCREEN,cv2.WINDOW_FULLSCREEN)
        cv2.imshow("frame", beam)
        if cv2.waitKey(1) == ord('q'):
            break
        elif cv2.waitKey(1) == ord('r'):
            obenlinks = 0
cv2.destroyAllWindows()
