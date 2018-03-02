import pylab
from pylab import *
import cv2
import numpy as np
import time

# Initalize camera
cap = cv2.VideoCapture(0)

# define range of purple color in HSV
lower_purple = np.array([60,50,90])
upper_purple = np.array([180,255,255])

# Create empty points array to store the location of the object
# Note, the upper right corner is the Origin 
points = []

for i in range (0, 100):
	points.append([1, i])

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

xs = [p[0] for p in points]
ys = [p[1] for p in points]
x = np.array(xs)
y = np.array(ys)

# Callback function to draw the subplots
def RealtimePloter(arg):
	global points, x, y
	
	# Update x-axes for subplots
	now = time.time() - then
	print now
	
	# Update x and y arrays
	xs = [p[0] for p in points]
	ys = [p[1] for p in points]
	x = np.array(xs)
	y = np.array(ys)
	CurrentXAxis=pylab.arange(now-100,now,1)
	CurrentYAxis=pylab.arange(now-100,now,1)
	
	# print x.size
	line1[0].set_data(CurrentXAxis,pylab.array(x[-100:]))
	ax.axis([CurrentXAxis.min(),CurrentXAxis.max(),0,1000])
	#manager.canvas.draw()
	#manager.show()
	
	# pinrt y.size
	line2[0].set_data(CurrentYAxis,pylab.array(y[-100:]))
	ay.axis([CurrentYAxis.min(),CurrentXAxis.max(),0,1000])
	manager.canvas.draw()

timer = fig.canvas.new_timer(interval=20)
timer.add_callback(RealtimePloter, ())
# timer2 = fig.canvas.new_timer(interval=20)
# timer2.add_callback(AcquireXY, ())
timer.start()
# timer2.start()

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
    center =   int(Height/2), int(Width/2)

    if len(contours) > 0:
        
        # Get the largest contour and its center 
        c = max(contours, key=cv2.contourArea)
        (x, y), radius = cv2.minEnclosingCircle(c)
        M = cv2.moments(c)
        try:
            center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))

        except:
            center =   int(Height/2), int(Width/2)

        # Allow only countors that have a larger than 15 pixel radius
        if radius > 25:
            
            # Draw cirlce and leave the last center creating a trail
            cv2.circle(frame, (int(x), int(y)), int(radius),(0, 0, 255), 2)
            cv2.circle(frame, center, 5, (0, 255, 0), -1)
            
    # Log center points 
    points.append(center)
    
    # loop over the set of tracked points
    if radius > 25:
        for i in range(1, len(points)):
            try:
                cv2.line(frame, points[i - 1], points[i], (0, 255, 0), 2)
                # print(points[i])
            except:
                pass
            
        # Make frame count zero
		frame_count = 0
		
	else:
		# Count frames 
		frame_count += 1
        
        # If we count 10 frames without object lets delete our trail
		if frame_count == 10:
			points = []
			print len(points)
			# when frame_count reaches 20 let's clear our trail 
			frame_count = 0
				
    # Display our object tracker
    frame = cv2.flip(frame, 1)
    cv2.imshow("Object Tracker", frame)

    if cv2.waitKey(1) == 13: #13 is the Enter Key
        break
	
# Release camera and close any open windows
cap.release()
cv2.destroyAllWindows()

# Note, if it ever shows error message like "radius not defined", change "if radius > 25" to "if True", restart and run,
# then change it back, restart and run. This will fix the error. WEIRD ISN'T IT??!!!