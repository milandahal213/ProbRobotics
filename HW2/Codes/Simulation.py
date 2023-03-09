import cv2
import numpy as np
from worldStates import *
from imageProcessing import *
import math

class Map:
	def __init__(self,path=None,scale=50):
		if path==None:
			self.path="/Users/mdahal01/Documents/Probabilistic Robotics/hw2/3Dmap.png"
		else:
			self.path=path

		self.image=cv2.imread(self.path)

		#height width and shape
		self.height = self.image.shape[0]
		self.width = self.image.shape[1]
		self.channels = self.image.shape[2]

		self.xcenter = int((self.width + self.width%2)/2)
		self.ycenter = int((self.height + self.height%2)/2)
		self.scale = scale
		self.xmin=0
		self.xmax=0
		self.ymin=0
		self.ymax=0


	def ImagetoWorld(self,coordinate):
		x,y = coordinate
		xWorld = (x-self.xcenter)/self.scale
		yWorld = (y-self.ycenter)/self.scale
		return ((xWorld,yWorld))

	def boundary(self):
		self.xmin,self.ymin=self.ImagetoWorld((0,0))
		self.xmax,self.ymax=self.ImagetoWorld((self.width,self.height))
		return(self.xmin,self.ymin,self.xmax,self.ymax)
		#creating an object to store World info from Image data

	def dimension(self):
		return(self.width,self.height)


class Particles:
	def __init__(self,obj):
		#boundary from the map
		self.xmin=obj.xmin
		self.xmax=obj.xmax
		self.ymin=obj.ymin
		self.ymax=obj.ymax
		self.scale=obj.scale
		self.radius=10
		self.weight=1

		self.xcenter=obj.xcenter
		self.ycenter=obj.ycenter
		self.xWorld, self.yWorld = self.generateCoordinate()

	def pos(self):
		xImage=math.floor(self.scale*self.xWorld + self.xcenter)
		yImage=math.floor(self.scale*self.yWorld + self.ycenter)
		return(xImage,yImage, self.radius)

	def reweigh(self,metric_val):
		self.weight=metric_val

	def showWeight(self):
		return self.weight

	def generateCoordinate(self):
		return(np.random.uniform(low = self.xmin, high = self.xmax),np.random.uniform(low = self.ymin, high = self.ymax))

	def moveParticle(self,x,y):
		self.xWorld=x
		self.yWorld=y

	def worldPos(self):
		return(self.xWorld,self.yWorld)




class Drone:
	def __init__(self,obj):
		#boundary from the map
		self.xmin=obj.xmin
		self.xmax=obj.xmax
		self.ymin=obj.ymin
		self.ymax=obj.ymax
		self.scale=obj.scale
		self.radius=10
		self.xcenter=obj.xcenter
		self.ycenter=obj.ycenter
		self.xWorld, self.yWorld = self.generateCoordinate()


	def pos(self):
		xImage=math.floor(self.scale*self.xWorld + self.xcenter)
		yImage=math.floor(self.scale*self.yWorld + self.ycenter)
		return(xImage,yImage, self.radius)


	def generateCoordinate(self):
		return(np.random.uniform(low = self.xmin, high = self.xmax),np.random.uniform(low = self.ymin, high = self.ymax))

	def moveStep(self):
		speed=0.3
		randVal=np.random.uniform(0,2*math.pi)
		dx=round(math.cos(randVal), 4) * speed
		dy=round(math.sin(randVal), 4) * speed 
		#dx and dy vectors to move
		self.xWorld += dx
		self.yWorld += dy

		while not (self.xWorld>self.xmin and self.xWorld < self.xmax and self.yWorld > self.ymin and self.yWorld< self.ymax):
			randVal=np.random.uniform(0,2*math.pi)
			dx=round(math.cos(randVal), 4) * speed
			dy=round(math.sin(randVal), 4) * speed 
			#dx and dy vectors to move
			self.xWorld += dx
			self.yWorld += dy

		noiseNx = np.random.normal(0,0.1)	#generating noise for movement
		noiseNy= np.random.normal(0,0.1)
		self.xWorld=self.xWorld+dx+noiseNx 
		self.yWorld=self.yWorld+dy+noiseNy

		return dx, dy



'''

world=World(width,height,scale=50)


#Assignment 1.1
#print  boundaries in world coordinates
xmin, ymin, xmax, ymax = world.boundary()
print("Range in the x,y directions", xmin,ymin,xmax,ymax)

#Assignment 1.2
#randomly assigning the drone position
xdroneWorld= np.random.uniform(low = xmin, high = xmax, size = None)
ydroneWorld= np.random.uniform(low = ymin, high = ymax, size = None)

print("State Vector is : [ %f , %f ]"%(xdroneWorld,ydroneWorld))

drone=points(world,xdroneWorld,ydroneWorld) #defining drone as a point in the world


#Assignment 1.3
#Get the reference image for any point x and y 
x,y=drone.Image() #getting x and y from drones position - these are converted to Image pixel positions
droneImage=cropImage(image,(x,y),50) #getting the observation image of 50x50 
cv2.imshow("Drone Image",droneImage)
noisyImage=addGaussianNoise(droneImage,50) #adding some noise on drone's image , our observation image
cv2.imshow("noisyImage",noisyImage)
cv2.waitKey(0)

#now some random x an y positions for reference Images
Firstpoint=points(world,3,5) #generating a point at (3,5) point in the world
x,y= Firstpoint.Image()		#corresponding position  on the map Image
referenceImage=cropImage(image,(x,y),50) #getting the observation image from the drone
cv2.imshow("referenceImage",referenceImage)
cv2.waitKey(0)


#now some random x an y positions for reference Images
Secondpoint=points(world,5,3) #generating a point at (5,3) point in the world
x,y= Secondpoint.Image()		#corresponding position  on the map Image
referenceImage=cropImage(image,(x,y),50) #getting the observation image from the drone
cv2.imshow("referenceImage",referenceImage)
cv2.waitKey(0)

import random
import math


for i in range(10):
	x,y=drone.Image()
	dronePositionImage=overlay(image,(x,y),thickness=4, color=(255,100,10),text="Drone").copy()
	cv2.imshow("overlaid",dronePositionImage)
	referenceImage=cropImage(image,(x,y),50) #getting the observation image from the drone
	#cv2.imshow("referenceImage",referenceImage)
	noisyImage=addGaussianNoise(referenceImage,50) #adding some noise
	cv2.imshow("noisyImage",noisyImage)
	cv2.waitKey(0)

	dx,dy =drone.movementVector()	#finding movement vecotors
	noiseNx = np.random.normal(0,0.1)	#generating noise for movement
	noiseNy= np.random.normal(0,0.1)
	x=x+dx+noiseNx 
	y=y+dy+noiseNy
'''

