from pylab import *
from collections import deque
import pylab
import cv2
import numpy as np
import time

# Initalize camera
cap = cv2.VideoCapture(1)

# define range of purple color in HSV
lower_purple = np.array([165,50,120])
upper_purple = np.array([240,255,255])

# Create empty deque array to store object locations for trajectory drawing
# Note, the upper right corner is the Origin 
points_draw = deque(maxlen=32)
# Create empty array list to store object locations for plotting
points_plot = []

# Initialize relevant variables in case Python gives 'name not defined' error
radius = 0
center_plot = 0, 0

for i in range (0, 100):
	points_plot.append([0, 0])

# Get default camera window size
ret, frame = cap.read()
Height, Width = frame.shape[:2]
frame_count = 0

# Initialize time varaible
then = time.time()

#####################################Plot Start#######################################
# Initialize plot parameters
xAchse=pylab.arange(0,100,1)
yAchse=pylab.array([0]*100)

fig = pylab.figure(1)
ax = fig.add_subplot(121)
ay = fig.add_subplot(122)

ax.grid(True)
ay.grid(True)
ax.set_title("X vs Time")
ay.set_title("Y vs Time")
ax.set_xlabel("Time")
ax.set_ylabel("X Value")
ay.set_xlabel("Time")
ay.set_ylabel("Y Value")
ax.axis([0,100,-1000,1000])
ay.axis([0,100,-1000,1000])

line1=ax.plot(xAchse,yAchse,'b-')
line2=ay.plot(xAchse,yAchse,'r-')

manager = pylab.get_current_fig_manager()

# Get x and y coordinates from the points_plot list and convert them to np arrayss
xs = [p[0] for p in points_plot]
ys = [p[1] for p in points_plot]
x = np.array(xs)
y = np.array(ys)

# Callback function to draw the subplots
def RealtimePloter(arg):
	global points_plot, x, y
	
	# Update x-axes for subplots
	now = time.time() - then
	
	# Update x and y arrays
	xs = [p[0] for p in points_plot]
	ys = [p[1] for p in points_plot]
	x = np.array(xs)
	y = np.array(ys)
	CurrentXAxis=pylab.arange(now-100,now,1)
	CurrentYAxis=pylab.arange(now-100,now,1)
	
	# Draw the first plot for X and t
	line1[0].set_data(CurrentXAxis,pylab.array(x[-100:]))
	ax.axis([CurrentXAxis.min(),CurrentXAxis.max(),0,1000])
	#manager.show()
	
	# Draw the secondt plot for Y and t
	line2[0].set_data(CurrentYAxis,pylab.array(y[-100:]))
	ay.axis([CurrentYAxis.min(),CurrentYAxis.max(),0,1000])
	manager.canvas.draw()

# Initialize the timer, callback every 20ms
timer = fig.canvas.new_timer(interval=20)
timer.add_callback(RealtimePloter, ())

timer.start()

pylab.show(block = False)

##################################Plot End############################################

while True:

	# Capture webcame frame
	ret, frame = cap.read()
	hsv_img = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

	# Threshold the HSV image to get only blue colors
	mask = cv2.inRange(hsv_img, lower_purple, upper_purple)
	#mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)

	# Find contours, OpenCV 3.X users use this line instead
	_, contours, _ = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
	# contours, _ = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

	# Create empty centre array to store centroid center of mass
	center_draw = None
	
	# Use a "buffer" to lower the sensitivity of the plot when detecting (0, 0)
	# in case the object detector is not able to detect accurately sometimes
	if radius > 5:
		frame_count = 0
	else:
		frame_count += 1
		
		if frame_count == 30:
			center_plot = 0,0
			frame_count = 0
	
	if len(contours) > 0:
        
		# Get the largest contour and its center 
		c = max(contours, key=cv2.contourArea)
		(x, y), radius = cv2.minEnclosingCircle(c)
		M = cv2.moments(c)
		
		# Allow only countors that have a larger than 25 pixel radius
		# if radius > 25:
		if radius > 5:
			try:
				center_draw = center_plot = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))

			except:
				center_plot = 0, 0
				
			# Draw minEnclosingCircle cirlce and leave the last center creating a trail
			cv2.circle(frame, (int(x), int(y)), int(radius),(0, 0, 255), 2)
			# Draw a circle at center of mass
			cv2.circle(frame, center_plot, 5, (0, 255, 0), 1)
            
    # Log center points 
	points_draw.appendleft(center_draw)
	points_plot.append(center_plot)
	
    # loop over the set of tracked points
	# if radius > 25:
	for i in range(1, len(points_draw)):
		if points_draw[i - 1] is None or points_draw[i] is None:
			continue
			
		thickness = int(np.sqrt(64 / float(i + 1)) * 2.5)
		cv2.line(frame, points_draw[i - 1], points_draw[i], (0, 255, 0), thickness)
		# print(points[i])
				
    # Display our object tracker
	frame = cv2.flip(frame, 1)
	cv2.imshow("Object Tracker", frame)

	if cv2.waitKey(1) == 13: #13 is the Enter Key
		break
	
# Release camera and close any open windows
cap.release()
cv2.destroyAllWindows()