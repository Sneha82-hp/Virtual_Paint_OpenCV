import numpy as np
import cv2
# used to store points for drawing efficiently
from collections import deque  

#trackbar function x stores the current trackbar position 
# OpenCV automatically calls this function whenever the trackbar moves
def setValues(x):
    print("")

# This window is used to display images, videos, or trackbars.
# Think of it like opening an empty frame on screen.
cv2.namedWindow("Colour detectors")    

# A trackbar is basically a slider.It lets the user change values interactively.
# cv2.createTrackbar(trackbarName, windowName, value, count, callbackFunction)
cv2.createTrackbar("Upper Hue","Colour detectors", 153,180,setValues)
cv2.createTrackbar("Upper Saturation","Colour detectors", 255,255,setValues)
cv2.createTrackbar("Upper Value","Colour detectors", 255,255,setValues)
#these are setting higher and lower value for hsv
cv2.createTrackbar("Lower Hue","Colour detectors", 64,180,setValues)
cv2.createTrackbar("Lower Saturation","Colour detectors", 72,255,setValues)
cv2.createTrackbar("Lower Value","Colour detectors", 49,255,setValues)

#deque comes from python and stores values efficiently value updates ans stores in points till 1024 while moving and new deque is created if line breaks
bpoints=[deque(maxlen=1024)]
gpoints=[deque(maxlen=1024)]
rpoints=[deque(maxlen=1024)]
ypoints=[deque(maxlen=1024)]

blue_index=0
green_index=0
red_index=0
yellow_index=0

#kernel is used to Remove small noise dots.
kernel = np.ones((5,5),np.uint8)

#create canvas and colours
colours=[(255,0,0),(0,255,0),(0,0,255),(0,255,255)]
paintWindow = np.zeros((471,636,3))+ 255

paintWindow=cv2.rectangle(paintWindow,(40,1),(140,65),(0,0,0),2)                       
paintWindow=cv2.rectangle(paintWindow,(160,1),(255,65),colours[0],-1)                       
paintWindow=cv2.rectangle(paintWindow,(275,1),(370,65),colours[1],-1)                       
paintWindow=cv2.rectangle(paintWindow,(390,1),(485,65),colours[2],-1)                       
paintWindow=cv2.rectangle(paintWindow,(505,1),(600,65),colours[3],-1)                       
                      
cv2.putText(paintWindow,"CLEAR",(49,33),cv2.FONT_HERSHEY_SIMPLEX,0.5,(0,0,0),2,cv2.LINE_AA)

#cv2.namedWindow('Paint',cv2.WINDOW_AUTOSIZE)

colorIndex = 0
#cap is a camera object used to : capture frames,read video continuously
cap=cv2.VideoCapture(0)
while True:
    Success,frame = cap.read()
    #keeps frame horizontal (1 means horizontal flip) and flip to make left right
    frame= cv2.flip(frame,1) 
    hsv = cv2.cvtColor(frame,cv2.COLOR_BGR2HSV)

    u_hue= cv2.getTrackbarPos("Upper Hue","Colour detectors")
    u_saturation= cv2.getTrackbarPos("Upper Saturation","Colour detectors")
    u_value= cv2.getTrackbarPos("Upper Value","Colour detectors")

    l_hue= cv2.getTrackbarPos("Lower Hue","Colour detectors")
    l_saturation= cv2.getTrackbarPos("Lower Saturation","Colour detectors")
    l_value= cv2.getTrackbarPos("Lower Value","Colour detectors")

     #These define detectable color range and create a array
    Upper_hsv = np.array([u_hue,u_saturation,u_value])
    Lower_hsv = np.array([l_hue,l_saturation,l_value])

    frame=cv2.rectangle(frame,(40,1),(140,65),(0,0,0),2)                       
    frame=cv2.rectangle(frame,(275,1),(370,65),colours[1],-1)                       
    frame=cv2.rectangle(frame,(390,1),(485,65),colours[2],-1)                       
    frame=cv2.rectangle(frame,(505,1),(600,65),colours[3],-1)  
    frame=cv2.rectangle(frame,(160,1),(255,65),colours[0],-1)  
    cv2.putText(frame,"CLEAR",(49,33),cv2.FONT_HERSHEY_SIMPLEX,0.5,(),2,cv2.LINE_AA)

    # a mask is a black-and-white image used to isolate or select specific parts of an image, the mask stores only the colors lying inside the HSV range
    #shows desired area, hides unwanted area
    mask = cv2.inRange(hsv,Lower_hsv,Upper_hsv)   
    #removes tiny white noise dots from the mask
    mask = cv2.erode(mask,kernel,iterations=1)   
    #reamoves all small noise
    mask = cv2.morphologyEx(mask,cv2.MORPH_OPEN,kernel)      
    #used to expand/thicken the white regions in the mask. as erode sometime shrinks the object so to regain the size this is used, dilation is an image processing operation
    mask=cv2.dilate(mask,kernel,iterations=1)  



#contours are curvers joining all continuous points along the boundary of obj having same intensity
#here we find the larget contour and draw a circle around it
    cnts, z= cv2.findContours(mask.copy(),cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    center =None
    if len(cnts)>0:
        cnts = sorted(cnts,key=cv2.contourArea, reverse=True)[0]
        ((x,y),radius) = cv2.minEnclosingCircle(cnts)
        cv2.circle(frame,(int(x),int(y)),int(radius),(0,255,255),2)
        M=cv2.moments(cnts)
        #extract x and y coordinates
        center= (int(M['m10']/M['m00']),int(M['m01']/M['m00']))
        
        if center[1]<=65:
            if 40<= center[0] <=140:
                bpoints=[deque(maxlen=512)]
                gpoints=[deque(maxlen=512)]
                rpoints=[deque(maxlen=512)]
                ypoints=[deque(maxlen=512)]

                blue_index=0
                green_index=0
                red_index=0
                yellow_index=0

                paintWindow[67:,:,:]=255
            elif 160<= center[0] <=255:
                colorIndex =0 #blue
            elif 275<= center[0] <=370:
                colorIndex =1 #green
            elif 390<= center[0] <=485:
                colorIndex =2 #red
            elif 505<= center[0] <=600:
                colorIndex =3 #yellow
        else:
            if colorIndex ==0:
                bpoints[blue_index].appendleft(center) 
            elif colorIndex ==1:
                gpoints[green_index].appendleft(center) 
            elif colorIndex ==2:
                rpoints[red_index].appendleft(center) 
            elif colorIndex ==3:
                ypoints[yellow_index].appendleft(center) 
    else:
        bpoints.append(deque(maxlen=512))
        blue_index +=1
        gpoints.append(deque(maxlen=512))
        green_index +=1
        rpoints.append(deque(maxlen=512))
        red_index +=1
        ypoints.append(deque(maxlen=512))
        yellow_index +=1

    points=[bpoints,gpoints,rpoints,ypoints]
    for i in range(len(points)):
        for j in range(len(points[i])):
            for k in range(1,len(points[i][j])):
                if points[i][j][k-1] is None or points[i][j][k] is None:
                    continue
                cv2.line(frame,points[i][j][k-1], points[i][j][k], colours[i],2)
                cv2.line(paintWindow,points[i][j][k-1], points[i][j][k], colours[i],2)
    cv2.imshow("live drawing",frame)            
    cv2.imshow("paint drawing",paintWindow)            
    cv2.imshow("mask drawing",mask)            

    #Checks keyboard every 1 millisecond. if user presses q cam stopes
    if cv2.waitKey(1) & 0xff == ord('q'):
        break
#closes camera properly    
cap.release()
#closes all opencv windows
cv2.destroyAllWindows()                   