from Simulation import *
from imageProcessing import *
import numpy as np
import matplotlib.pyplot as plt
import cv2
import time


bins=50
path="/Users/mdahal01/Documents/Probabilistic Robotics/hw2/3Dmap.png"
MapImage=cv2.imread(path)
#self.uneditedImage=cv2.imread(self.path)

Aperture = 20
#worldimage.display("Image")

world=Map(path)
xminWorld,yminWorld,xmaxWorld,ymaxWorld= world.boundary() #set the boundary of the world

xmaxImage,ymaxImage = world.dimension()

drone=Drone(world) #Create a drone in the world
#droneImage= overlay(MapImage,drone.pos(),text="Drone") # add  the drone on the image
#display(droneImage, "Map with Drone")
obsImage=cropImage(MapImage, drone.pos(),  xmaxImage, ymaxImage, m=Aperture) #create an observation image for drone
obsImage=addGaussianNoise(obsImage,m=Aperture) #add noise to the observation image from drone
#display(obsImage, "Drone")
# worldimage.displayCrop(refImage,"Gaussian") #show what drone is seeing

'''
for i in range(10):

	tx=int(np.random.uniform(100,300))
	ty=int(np.random.uniform(100,300))
	print(tx,ty)
	refImage=worldimage.cropImage((tx,ty))
	worldimage.displayCrop(refImage,"cropped")
'''

N=1000
particles=[None] * N
refImage=[None] * N
#generating particles
for i in range(N):
	particles[i]= Particles(world)
	#print(particles[i].pos())
i=0
# while we find a localization point 
#ParticleImage=MapImage.copy()
'''
for particle in particles:
	ParticleImage= overlay(ParticleImage, particle.pos(),thickness=1, radius2=0,color=(0,250,100),text=str(i)) #drawing the particles
	refImage[i]= cropImage(MapImage, particle.pos(),xmaxImage,ymaxImage ,m=Aperture)
	i+=1
	#crop image for each particles
	#compare the cropped image of each particle with the image from drone
'''
#Move Drone

#display(ParticleImage,"particle image")


def resamplingFuntion( dx, dy): #kind of roulette wheel implementation
	#generate a random number between 0 and 1
	# compare with the cummulative weight of weights until cum_weight < random number
	# take the i and find the x and y for that particle
	#set the x and y for the new partcle based on the x and y of the ith particle with noise
	# repeat for N times
	x=[0]*N
	y=[0]*N
	for iteration in range(N):
		randVal= np.random.uniform(low = 0, high = 1)
		i=0
		cumm_weight=0
		while cumm_weight < randVal:
			cumm_weight += particles[i].showWeight()
			i+=1
		x[iteration],y[iteration]=particles[i-1].worldPos()


	for i in range(N):

		#oldx,oldy=particles[i].worldPos()

		#generating noise for movement
		randVal=np.random.uniform(0,2*math.pi)
		noiseNx=round(math.cos(randVal), 4) * 0.1
		noiseNy=round(math.sin(randVal), 4) * 0.1

		nx= max(min(x[i] + dx +  noiseNx,xmaxWorld),xminWorld)
		ny= max(min(y[i] + dy +  noiseNy,ymaxWorld),yminWorld)


		particles[i].moveParticle(nx,ny)

for i in range(100):
	metric_val=[0]*N
	dx, dy= drone.moveStep()
	obsImage=cropImage(MapImage, drone.pos(),xmaxImage,ymaxImage,m=Aperture) #create an observation image for drone
	obsImage=addGaussianNoise(obsImage) #add noise to the observation image from drone
	obsHist = cv2.calcHist([obsImage], [0, 1, 2], None, [bins, bins, bins], [0, 256, 0, 256, 0, 256]) #Histogram of observation image
	cv2.normalize(obsHist, obsHist, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX)
	#display(obsImage, "Observation from Drone")

	ParticleImage=MapImage.copy()
	for i in range (N):
		try:
			ParticleImage = overlay(ParticleImage, particles[i].pos(),thickness=1 , radius2=7,color=(0,0,255)) #drawing the particles	
			refImage[i]=cropImage(MapImage, particles[i].pos(), xmaxImage,ymaxImage,m=Aperture )
			tempImage=refImage[i].copy()
			refHist = cv2.calcHist([refImage[i]], [0, 1, 2], None, [bins, bins, bins], [0, 256, 0, 256, 0, 256])
			cv2.normalize(refHist, refHist, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX)
			tempMetric=cv2.compareHist(obsHist, refHist, cv2.HISTCMP_CORREL) ** 2
			if (tempMetric < 0.05):	
				metric_val[i]=0.001
			else:
				metric_val[i]= cv2.compareHist(obsHist, refHist, cv2.HISTCMP_CORREL) ** 2
		except:
			print("err",i)
		#display(refImage[i],"ref Image")

	sumofweights=sum(metric_val)
	#normalize the metric_val to 1 and set that as weight
	for i in range (N):
		particles[i].reweigh(metric_val[i]/sumofweights)

	resamplingFuntion(dx,dy) #RESAMPLE	the particles and move them according to the movement of the drone

	droneImage= overlay(ParticleImage,drone.pos(),text="Drone") # add  the drone on the image
	display(droneImage, "Drone")


