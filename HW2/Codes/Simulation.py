import cv2
import numpy as np
from worldStates import *
from imageProcessing import *
import math

class Map:
	def __init__(self,path=None,scale=50):
		if path==None:
			imageFolder=os.path.normpath(os.getcwd() + os.sep + os.pardir)
			self.path=imageFolder+"/CityMap.png" #Default Image
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
		yWorld = (-y+self.ycenter)/self.scale
		return ((xWorld,yWorld))

	def boundary(self):
		self.xmin,self.ymin=self.ImagetoWorld((0,self.height))
		self.xmax,self.ymax=self.ImagetoWorld((self.width,0))
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
		yImage=math.floor(self.ycenter - self.scale*self.yWorld)
		return(xImage,yImage, self.weight)

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
		yImage=math.floor(self.ycenter - self.scale*self.yWorld)
		return(xImage,yImage, self.radius)


	def generateCoordinate(self):
		return(np.random.uniform(low = self.xmin, high = self.xmax),np.random.uniform(low = self.ymin, high = self.ymax))

	def moveStep(self):
		speed=0.5
		randVal=np.random.uniform(0,2*math.pi)
		dx=round(math.cos(randVal), 4) * speed
		dy=round(math.sin(randVal), 4) * speed 
		#dx and dy vectors to move
		self.xWorld += dx
		self.yWorld += dy

		while not (self.xWorld>self.xmin and self.xWorld < self.xmax and self.yWorld > self.ymin and self.yWorld < self.ymax):
			randVal=np.random.uniform(0,2*math.pi)
			dx=round(math.cos(randVal), 4) * speed
			dy=round(math.sin(randVal), 4) * speed 
			#dx and dy vectors to move
			self.xWorld += dx
			self.yWorld += dy

		noiseNx = np.random.normal(0,0.05)	#generating noise for movement
		noiseNy= np.random.normal(0,0.05)
		self.xWorld=self.xWorld+dx+noiseNx 
		self.yWorld=self.yWorld+dy+noiseNy

		return dx, dy

	def worldPos(self):
		return(self.xWorld,self.yWorld)

