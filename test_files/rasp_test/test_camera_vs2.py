import cv2
import os
import sys
import numpy as np
import time
import warnings
warnings.filterwarnings("ignore")

import io
import picamera
import logging
from SocketServer import ThreadingMixIn
from threading import Condition
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler

import serial
ser = serial.Serial('/dev/ttyACM0',9600)
import socket
#resolution 640x480

parkFlag = 0 #parking flag

warnings.filterwarnings("ignore")
#resolution 640x480
def grayscale(img):  #returns grayscale of image
    return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

def filter_white(img):#filter's white
    lower = np.array([200, 200,200])#lower bound for white filter
    upper = np.array([255, 255, 255])#upper bound for white filter
    mask = cv2.inRange(img, lower, upper)#mask so it keeps those in range of two
    white = cv2.bitwise_and(img, img, mask=mask)#and the mask and frame to get white
    return white

def filter_yellow(img):
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)#same as white but uses hsv for yellow filtering
    lower = np.array([20, 100, 100])
    upper = np.array([40, 255, 255])
    mask = cv2.inRange(hsv, lower, upper)
    yellow = cv2.bitwise_and(img, img, mask=mask)
    return yellow

def draw_lines(img, lines, color=[255, 0, 0], thickness=3, make_copy=True):
    # Copy the pasted image
    img_copy = np.copy(img) if make_copy else img

    for line in lines:
        for x1, y1, x2, y2 in line:
            cv2.line(img_copy, (x1, y1), (x2, y2), color, thickness)

    return img_copy

def separate_lines(lines, img):
    img_shape = img.shape
    middle_x = img_shape[1] / 2  # gets the midpoint of the image

    left_lines = []
    right_lines = []
    for line in lines:
        for x1, y1, x2, y2 in line:
            dx = x2 - x1  # dx for slope calculation
            if dx == 0:  # if there is 0 value, it wont stop program
                continue
            dy = y2 - y1  # dy for slope calc

            if dy == 0:  # if there is 0 value, it wont stop program
                continue

            slope = dy / dx

            slopethresh = 1
            if abs(slope) <= slopethresh:  # if slope is less don't include
                continue

            if slope > 0 and x1 > middle_x and x2 > middle_x and x1 >80 :  # determines if it is left lane
                right_lines.append([[x1, y1, x2, y2]])
            elif slope < 0 and x1 < middle_x and x2 < middle_x and x2<540:  # determines if in right lane
                left_lines.append([[x1, y1, x2, y2]])

    return left_lines, right_lines
def masking():
    mask = np.zeros(frame.shape, dtype=np.uint8)#makes for region of interest
    roi_corners = np.array([[(0, 480), (0, 240), (640, 240), (640, 480)]], dtype=np.int32)  # trapazoid with points
    channel_count = frame.shape[2]
    ignore_mask_color = (255,) * channel_count
    cv2.fillPoly(mask, roi_corners, ignore_mask_color)

    masked_image = cv2.bitwise_and(frame, mask)
    return masked_image

def fit_lines(left,right):
    validright=True
    validleft=True
    xL = []
    yL = []  # default dummy values
    xr = []
    yr = []
    for line in left:
        for x1, y1, x2, y2 in line:
            xL += [x1, x2]
            yL += [y1, y2]

    for line in right:
        for x1, y1, x2, y2 in line:
            xr += [x1, x2]
            yr += [y1, y2]

    if len(xL) > 0:
        mL, bL = np.polyfit(xL, yL, 1)
    else:
        mL, mL= 1, 1
        validleft = False#makes it so it wont poly fit if no value is read
    if len(xr) > 0:
        mr, br = np.polyfit(xr, yr, 1)
    else:
        mr, mr= 1, 1
        validright = False#makes it so it wont poly fit if no value is read

    if validleft:#if it passes everything, will draw a line
        cv2.line(framecopy, pt1=(int((250 - bL) / mL), 250), pt2=(int((480 - bL) / mL), 480), color=(255, 0, 0),
                 # draw left line
                 thickness=10)
    if validright:
        cv2.line(framecopy, pt1=(int((250 - br) / mr), 250), pt2=(int((480 - br) / mr), 480), color=(0, 0, 255),
                 # draw right line
                 thickness=10)
    if validright and validleft:
        midpoint = int((int((250 - br) / mr) + int((250 - bL) / mL)) / 2)
        # print(midpoint)
        centerguide = (320, 240)
        cv2.circle(framecopy, centerguide, 12, color=[255, 0, 255], thickness=3)
        cv2.line(framecopy, pt1=(midpoint, 480), pt2=(midpoint, 460), color=(0, 255, 0), thickness=10)
        cv2.line(framecopy, pt1=(midpoint, 480), pt2=centerguide, color=(255, 255, 0), thickness=10)
        cv2.imshow("Fitted Lines", framecopy)
	return midpoint

def color_lanes(img, left_lines, right_lines, left_color=[255, 0, 0], right_color=[0, 0, 255]):
    left_img = draw_lines(img, left_lines, color=left_color, make_copy=True)#makes left line red
    right_img = draw_lines(left_img, right_lines, color=right_color, make_copy=False)#make right line blue over the left image

    return right_img#has both left and right lines

video = cv2.VideoCapture(0)

while True:
    ret, orig_frame = video.read()
    if not ret:
        video = cv2.VideoCapture(0)
        continue
    framecopy=orig_frame
    frame=orig_frame

    masked_image=masking()

    filterwhite = filter_white(masked_image)#filter white
    #filteryellow = filter_yellow(masked_image)#filter yellow
    #Sum = cv2.addWeighted(filterwhite, 1, filteryellow, 1, 1, 0)#add both images
    #gray = grayscale(Sum)#get grayscale
    gray=filterwhite

    blur = cv2.GaussianBlur(gray, (3, 3), 0)

    edges = cv2.Canny(blur, 60, 150, apertureSize=3)

    lines = cv2.HoughLinesP(edges, 2, np.pi / 180, 50, maxLineGap=150)
    if lines is not None:
        leftlane, rightlane = separate_lines(lines, masked_image)
        imagelines = color_lanes(masked_image, leftlane, rightlane)
        cv2.imshow("imline",imagelines)
        midpoint=fit_lines(leftlane,rightlane)
	if midpoint!= None:
		difference=midpoint-320
		print(difference)
		if difference > 20:
			ser.write('R')
                	time.sleep(4)
		elif difference <-20:
			ser.write('L')
			time.sleep(4)
		else:
			ser.write('S')
    else:
        continue
#arduino send signal to rpi
#    if ser.in_waiting>0: #if arduino send sth
#        parkFlag = ser.readline()
#    if parkFlag >39: # if parking found
#        break
    key = cv2.waitKey(25)
    if key == 27:
        break
print("parking found")
video.release()
cv2.destroyAllWindows()

#streaming code
PAGE="""\
<html>
<head>
<title>Dash Camera</title>
</head>
<body>
<h1>Dash Camera</h1>
<img src="stream.mjpg" width="640" height="480" />
</body>
</html>
"""

class StreamingOutput(object):
    def __init__(self):
        self.frame = None
        self.buffer = io.BytesIO()
        self.condition = Condition()

    def write(self, buf):
        if buf.startswith(b'\xff\xd8'):
            # New frame, copy the existing buffer's content and notify all
            # clients it's available
            self.buffer.truncate()
            with self.condition:
                self.frame = self.buffer.getvalue()
                self.condition.notify_all()
            self.buffer.seek(0)
        return self.buffer.write(buf)

class StreamingHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(301)
            self.send_header('Location', '/index.html')
            self.end_headers()
        elif self.path == '/index.html':
            content = PAGE.encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.send_header('Content-Length', len(content))
            self.end_headers()
            self.wfile.write(content)
        elif self.path == '/stream.mjpg':
            self.send_response(200)
            self.send_header('Age', 0)
            self.send_header('Cache-Control', 'no-cache, private')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary = FRAME')
            self.end_headers()
            try:
                while True:
                    with output.condition:
                        output.condition.wait()
                        frame = output.frame
                    self.wfile.write(b'--FRAME\r\n')
                    self.send_header('Content-Type', 'image/jpeg')
                    self.send_header('Content-Length', len(frame))
                    self.end_headers()
                    self.wfile.write(frame)
                    self.wfile.write(b'\r\n')
            except Exception as e:
                logging.warning(
                    'Removed streaming client %s: %s',
                    self.client_address, str(e))
        else:
            self.send_error(404)
            self.end_headers()

class StreamingServer(ThreadingMixIn,HTTPServer):
    allow_reuse_address = True
    daemon_threads = True

with picamera.PiCamera(resolution='640x480', framerate=24) as camera:
    output = StreamingOutput()
    camera.start_recording(output, format='mjpeg')
    try:
        address = ('', 8000)
        server = StreamingServer(address, StreamingHandler)
        server.serve_forever()
    finally:
        camera.stop_recording()


