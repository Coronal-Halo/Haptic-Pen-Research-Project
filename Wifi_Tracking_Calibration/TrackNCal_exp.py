from pylab import *
from collections import deque
import pylab
import cv2
import numpy as np
import math as m
import time
import serial
# import telnetlib
import threading
import os

from calibration import calibrator
from Telnet import TelnetWorkers

def readData(TelnetWorkers, dataList):
	while True:
		# threadLock.acquire()
		# print("Inside 1st While")
		arduinoData = TelnetWorkers.getMoreData()
		# Get data from BNO055 sensor
		myData = (arduinoData.strip())
		dataReceive = myData.split('/')
		
		for x in range(0, 3):
			dataList[x] = dataReceive[x]
			
		# threadLock.release()
		
		print("Inside readData")
		print dataList
		
def calculatePos(lengthPen, pixelsPerMetric, dataList):
	global deltaX, deltaY
	
	while True: 
		# threadLock.acquire()

		# Data for angles from BNO055 
		if(dataList is not None):
			X_Degree = float(dataList[0])
			Y_Degree = float(dataList[1])
			Z_Degree = float(dataList[2])
		# threadLock.release()
			
		# Calculations for Trignometry from BNO055 data
		tanY = m.tan(m.radians(Y_Degree))
		cosZ = m.cos(m.radians(- (90 + Z_Degree)))
		cosX = m.cos(m.radians(X_Degree))
		
		pixelPen = lengthPen * pixelsPerMetric
		abs_deltaX = m.sqrt(2 * m.pow(pixelPen, 2) / ((m.pow(tanY, 2) / m.pow(cosZ, 2)) + (1 / m.pow(cosX, 2)) + m.pow(tanY, 2) + 1))
		cos_verticalPAngle = m.sqrt( m.pow(abs_deltaX, 2) + m.pow(abs_deltaX * tanY, 2)) / pixelPen
		
		# Calibrate the right and left direction in terms of the North/South poles of the Earth
		# Need a better automated approach for calibration
		if(X_Degree < 140 or X_Degree > 320):
			deltaX = - pixelPen * cos_verticalPAngle * m.cos(m.radians(Y_Degree))
		else:
			deltaX = pixelPen * cos_verticalPAngle * m.cos(m.radians(Y_Degree))
			
		deltaY = pixelPen * cos_verticalPAngle * m.sin(m.radians(-Y_Degree))
		

################################################Main Thread Below##################################

# Start calibration for pixelsPerMetric
pixelsPerMetric = calibrator(42)

# Initialize reading from Arduino
# arduinoData = serial.Serial('com3', 115200)
telnet = TelnetWorkers('192.168.0.103', '23')

# define range of purple color in HSV
lower_blue = np.array([85,50,150])
upper_blue = np.array([110,200,255])

# Create empty deque array to store object locations for trajectory drawing
# Note, the upper right corner is the Origin 
points_draw_original = deque(maxlen=4)
points_draw_cal = deque(maxlen=4)

# Create empty array list to store object locations for plotting
points_plot = []

# length of the haptic pen, unit is cm
lengthPen = 18

# Initialize relevant variables in case Python gives 'name not defined' error
radius = 0
center_plot = 0, 0

deltaX = deltaY = 0
dataList = [1, 1, 1]


for i in range (0, 100):
	points_plot.append([0, 0])

# Initalize camera
cap = cv2.VideoCapture(0)

# Get default camera window size
ret, frame = cap.read()
Height, Width = frame.shape[:2]
frame_count = 0

####################################DONE INITIALIZATION###############################

# Creating threads
thread_readData = threading.Thread(target = readData, args = (telnet, dataList), name="t_data")
thread_calculatePos = threading.Thread(target = calculatePos, args = (lengthPen, pixelsPerMetric, dataList), name="t_calc")

# starting threads
thread_readData.start()
thread_calculatePos.start()

threadLock = threading.Lock()

while True:
	
	# Capture webcame frame
	ret, frame = cap.read()
	hsv_img = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

	# Threshold the HSV image to get only blue colors
	mask_blue = cv2.inRange(hsv_img, lower_blue, upper_blue)
	cv2.imshow('mask_blue', cv2.flip(mask_blue,1))
	#mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)

	# Find contours, OpenCV 3.X users use this line instead
	_, contours, _ = cv2.findContours(mask_blue.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

	# Create empty centre array to store centroid center of mass
	center_draw_original = None
	center_draw_cal = None
	
	# Use a "buffer" to lower the sensitivity of the plot when detecting (0, 0)
	# in case the object detector is not able to detect accurately sometimes
	if radius > 5:
		frame_count = 0
	else:
		frame_count += 1
		
		if frame_count == 30:
			center_plot = 0,0
			frame_count = 0
			
	radius_blue = radius_yellow = radius_red = 0
	
	if len(contours) > 0:
		
		# Get the largest contour and its center 
		c = max(contours, key=cv2.contourArea)
		(x, y), radius = cv2.minEnclosingCircle(c)
		M = cv2.moments(c)
		
	# Allow only countors that have a larger than 25 pixel radius
	# if radius > 25:
		if radius > 5:
			
			try:
				center_draw_original = center_plot = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
				center_draw_cal = (center_draw_original[0] + deltaX, center_draw_original[1] + deltaY)
				
			except:
				center_plot = 0, 0
			
			# Draw minEnclosingCircle cirlce and leave the last center creating a trail
			cv2.circle(frame, (int(x), int(y)), int(radius),(0, 0, 255), 2)
			# Draw a circle at center of mass
			cv2.circle(frame, center_plot, 5, (0, 255, 0), 1)
			
	# Log center points 
	points_draw_original.appendleft(center_draw_original)
	points_draw_cal.appendleft(center_draw_cal)
	
	points_plot.append(center_plot)
	
	# loop over the set of tracked points
	# if radius > 25:
	for i in range(1, len(points_draw_original)):
		if points_draw_original[i - 1] is None or points_draw_original[i] is None or points_draw_cal[i - 1] is None or points_draw_cal[i] is None:
			continue
			
		if(i == 1):
			points_draw_cal[0] = (int(points_draw_cal[0][0]), int(points_draw_cal[0][1])) 
		
		points_draw_cal[i] = (int(points_draw_cal[i][0]), int(points_draw_cal[i][1]))
			
		thickness = 8 #int(np.sqrt(64 / float(i + 1)) * 2.5)
		# Original is green
		cv2.line(frame, points_draw_original[i - 1], points_draw_original[i], (0, 255, 0), thickness/4)
		# Real tip is blue
		cv2.line(frame, points_draw_cal[i - 1], points_draw_cal[i], (255, 0, 0), thickness)
		# print(points[i])
				
	# Display our object tracker
	frame = cv2.flip(frame, 1)
	cv2.imshow("Object Tracker", frame)

	if cv2.waitKey(1) == 13: #13 is the Enter Key
		break
	
# Release camera and close any open windows
cap.release()
cv2.destroyAllWindows()