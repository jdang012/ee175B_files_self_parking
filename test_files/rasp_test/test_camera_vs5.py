

import cv2
import numpy as np
import warnings
import time
warnings.filterwarnings("ignore")
#resolution 640x480
import serial
ser = serial.Serial('/dev/ttyACM0',9600)
parkingFlag = 0;

import io
import picamera
import logging
from SocketServer import ThreadingMixIn
from threading import Condition
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler

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
            if dx ==0:
		slope=100  # if there is 0 value, it wont stop program
            else:
             # dy for slope calc
		   dy=y2-y1
	           slope = float(dy) /float( dx)
#	 	   print("dy",dy,"dx",dx,"slope",slope)
            slopethresh = 0.4
           # if abs(slope) <= slopethresh:  # if slope is less don't include
            #    continue

            if slope >=0.4: # and x1 > middle_x and x2 > middle_x :  # determines if it is left lane
                right_lines.append([[x1, y1, x2, y2]])
	#	print("right",right_lines)
            if slope <= -0.4: #   and x1 < middle_x and x2 < middle_x:  # determines if in right lane
                left_lines.append([[x1, y1, x2, y2]])
	#	print("left",left_lines)
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
        cv2.line(framecopy, pt1=(int((240 - bL) / mL), 240), pt2=(int((480 - bL) / mL), 480), color=(255, 0, 0),
                 # draw left line
                 thickness=10)
    if validright:
        cv2.line(framecopy, pt1=(int((240 - br) / mr), 240), pt2=(int((480 - br) / mr), 480), color=(0, 0, 255),
                 # draw right line
                 thickness=10)
    if validright and validleft:
        midpoint = int((int((240 - br) / mr) + int((240 - bL) / mL)) / 2)
        midpoint2= int((int((480 - br) / mr) + int((480 - bL) / mL)) / 2)
        # print(midpoint)
        pt1 = (midpoint - 5, 240)
        pt2 = (midpoint + 5,240)
        pt3 = (midpoint2 - 5,480)
        pt4 = (midpoint2 + 5,480)
        points=np.array([pt1,pt3,pt4,pt2])
       # img=framecopy2
        img2=np.zeros((480,640),np.uint8)
        cv2.fillConvexPoly(img2,points,color=[255,0,0])
        img, contours, hierarchy = cv2.findContours(img2.copy(), cv2.RETR_TREE,
                                                                cv2.CHAIN_APPROX_SIMPLE)
        if len(contours) > 0:
            newbox = cv2.minAreaRect(contours[0])
            (x_min, y_min), (width_min, height_min), angle = newbox
            if angle <-45:
		angle=90+angle
	    if width_min< height_min and angle >0:
		angle =(90-angle)*-1
	    if width_min > height_min and angle <0:
		angle= 90+angle
            midpixel = 320
            error = int(x_min - midpixel)
            angle = int(angle)
            box = cv2.boxPoints(newbox)
	    diff=midpoint-320
            box = np.int0(box)
            cv2.drawContours(framecopy, [box], 0, (0, 0, 255), 3)
           # cv2.putText(framecopy, str(angle), (10, 40), cv2.FONT_HERSHEY_PLAIN, 1, (255, 0, 255), 2)
           # cv2.putText(framecopy, str(error), (10, 320), cv2.FONT_HERSHEY_PLAIN, 1, (0, 255, 0), 2)
	    cv2.line(framecopy, (int(x_min), 200), (int(x_min), 250), (255, 0, 0), 3)
            print(error,angle,diff)

	    if  error >35:
		ser.write("L")
		print("L")
	    elif error <-35:
		ser.write ("R")
		print("R")
	    else:
		ser.write("S")
		print("S")

	centerguide = (320, 240)
       # cv2.circle(framecopy, centerguide, 12, color=[255, 0, 255], thickness=3)
        #cv2.line(framecopy, pt1=(midpoint, 240), pt2=(midpoint2, 480), color=(0, 255, 0), thickness=10)
        #cv2.line(framecopy, pt1=(320, 480), pt2=centerguide, color=(255, 255, 0), thickness=10)
        #cv2.imshow("img",img2)
        cv2.imshow("Fitted Lines", framecopy)

def color_lanes(img, left_lines, right_lines, left_color=[255, 0, 0], right_color=[0, 0, 255]):
    left_img = draw_lines(img, left_lines, color=left_color, make_copy=True)#makes left line red
    right_img = draw_lines(left_img, right_lines, color=right_color, make_copy=False)#make right line blue over the left image

    return right_img#has both left and right lines

video = cv2.VideoCapture(0)
#video= cv2.VideoCapture("video_car.mp4")
while True:
    ret, orig_frame = video.read()
    if not ret:
        video = cv2.VideoCapture(0)
        continue
    orig_frame=cv2.flip(orig_frame,0)
    framecopy=orig_frame
    frame=orig_frame
    framecopy2=orig_frame
#    cv2.imshow("orig",orig_frame)
    masked_image=masking()

    filterwhite = filter_white(masked_image)#filter white
    #filteryellow = filter_yellow(masked_image)#filter yellow
    #Sum = cv2.addWeighted(filterwhite, 1, filteryellow, 1, 1, 0)#add both images
    #gray = grayscale(Sum)#get grayscale
    gray=grayscale(filterwhite)
	
    blur = cv2.GaussianBlur(gray, (3, 3), 0)
    kernel=np.ones((3,3),np.uint8)
   # cv2.imshow("masked",masked_image)
    edges = cv2.Canny(blur, 30, 100)
   # edges = cv2.erode(edges,kernel,1)
    edges=cv2.dilate(edges,kernel,1)

   # edges = cv2.morphologyEx(edges,cv2.MORPH_OPEN,kernel)
   # cv2.imshow("thing",edges)
    lines=cv2.HoughLinesP(edges,2,np.pi/180,100,5,100)
    if lines is not None:
        imagelines2=draw_lines(masked_image,lines,[250,0,0])

       # cv2.imshow("try2",imagelines2)    

        leftlane, rightlane = separate_lines(lines, masked_image)
        imagelines = color_lanes(masked_image, leftlane, rightlane)
        cv2.imshow("imline",imagelines)
        fit_lines(leftlane,rightlane)

       

    else:
        continue
    if (ser.in_waiting >0):
	parkingFlag = ser.readline()
	print(parkingFlag)
    if parkingFlag >99:
#	print ("Parking Found")
	break;
    key = cv2.waitKey(25)
    if key == 27:
        break
print("video stop")
video.release()
cv2.destroyAllWindows()


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
            self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=FRAME')
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

class StreamingServer(ThreadingMixIn, HTTPServer):
    allow_reuse_address = True
    daemon_threads = True

with picamera.PiCamera(resolution='640x480', framerate=24) as camera:
    camera.rotation = 180
    output = StreamingOutput()
    camera.start_recording(output, format='mjpeg')
    try:
        address = ('', 8000)
        server = StreamingServer(address, StreamingHandler)
        server.serve_forever()
    finally:
        camera.stop_recording()
