import cv2
import os
import numpy as np
import warnings
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
    # Copy the passed image
    img_copy = np.copy(img) if make_copy else img

    for line in lines:
        for x1, y1, x2, y2 in line:
            cv2.line(img_copy, (x1, y1), (x2, y2), color, thickness)

    return img_copy

def separate_lines(lines, img):
    img_shape = img.shape
    middle_x = img_shape[1] / 2  # gets the midpoint of the image
    maxr = 0
    maxl = 0
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

            slopethresh =1 
            if abs(slope) <= slopethresh:  # if slope is less don't include
                continue

           # if slope < 0 and x1 < middle_x and x2 < middle_x and x1 > maxl:  # determines if it is left lane
            #    left_lines.append([[x1, y1, x2, y2]])
            if   x1 < middle_x and x2 < middle_x and x1 > maxl:  # determines if it is left $
                left_lines.append([[x1, y1, x2, y2]])

            elif x1 >= middle_x and x2 >= middle_x:  # determines if in right lane
                right_lines.append([[x1, y1, x2, y2]])

    return left_lines, right_lines

def fit_lines(left,right):
    if left == None or right == None:
        return 5000, 5000, 5000, 5000
    else:

        xL = [1,1]
        yL = [1,1] #default dummy values
        xr = [1,1]
        yr = [1,1]
        for line in left:
            for x1, y1, x2, y2 in line:

                xL += [x1, x2]
                yL += [y1, y2]

        zL = np.polyfit(xL, yL, 1)  # fit left lin


        for line in right:
            for x1, y1, x2, y2 in line:
                xr += [x1, x2]
                yr += [y1, y2]

        zr = np.polyfit(xr, yr, 1)
    return zL,zr


def color_lanes(img, left_lines, right_lines, left_color=[255, 0, 0], right_color=[0, 0, 255]):
    left_img = draw_lines(img, left_lines, color=left_color, make_copy=True)#makes left line red
    right_img = draw_lines(left_img, right_lines, color=right_color, make_copy=False)#make right line blue over the left image

    return right_img#has both left and right lines

video=cv2.VideoCapture(0)

while True:
    ret, orig_frame = video.read()
    if not ret:
        video = cv2.VideoCapture(0)
        continue
    framecopy=orig_frame
    frame=orig_frame

    mask = np.zeros(frame.shape, dtype=np.uint8)#makes for region of interest
    roi_corners = np.array([[(0, 480),(0,280),(640,280),(640,480)]], dtype=np.int32)#trapazoid with points
    channel_count = frame.shape[2]
    ignore_mask_color = (255,) * channel_count
    cv2.fillPoly(mask, roi_corners, ignore_mask_color)

    masked_image = cv2.bitwise_and(frame, mask)
#    cv2.imshow("Masked",masked_image)
    filterwhite = filter_white(masked_image)#filter white
#    filteryellow = filter_yellow(masked_image)#filter yellow
#    Sum = cv2.addWeighted(filterwhite, 1, filteryellow, 1, 1, 0)#add both images
#    gray = grayscale(Sum)#get grayscale
    gray = grayscale(filterwhite)

    blur = cv2.GaussianBlur(gray, (3, 3), 0)

    edges = cv2.Canny(blur, 60, 150, apertureSize=3)
   # cv2.imshow("edge",edges)
    lines = cv2.HoughLinesP(edges, 2, np.pi / 180, 50, maxLineGap=150)
    if lines is not None:
        leftlane, rightlane = separate_lines(lines, masked_image)
        imagelines = color_lanes(masked_image, leftlane, rightlane)
	cv2.imshow("imagelines",imagelines)
        zL,zr =fit_lines(leftlane,rightlane)
        mL, bL = zL
        mr, br = zr
        if mL != 0.5 and mr != 0.5:
            cv2.line(framecopy, pt1=(int((280 - bL) / mL), 280), pt2=(int((640 - bL) / mL), 640), color=(255, 0, 0),
                     # draw right line
                     thickness=10)
            cv2.line(framecopy, pt1=(int((280 - br) / mr), 280), pt2=(int((640 - br) / mr), 640), color=(0, 0, 255),
                     # draw left line
                     thickness=5)
            midpoint = int((int((250 - br) / mr) + int((250 - bL) / mL)) / 2)
            print(midpoint)
            centerguide = (320, 240)
            cv2.circle(framecopy, centerguide, 12, color=[255, 0, 255], thickness=3)
            cv2.line(framecopy, pt1=(midpoint, 480), pt2=(midpoint, 460), color=(0, 255, 0), thickness=10)
            guideline = cv2.line(framecopy, pt1=(midpoint, 480), pt2=centerguide, color=(255, 255, 0), thickness=10)
#            cv2.imshow("Fitted Lines", framecopy)



    else:
        continue
    key = cv2.waitKey(25)
    if key == 27:
        break
video.release()
cv2.destroyAllWindows()
