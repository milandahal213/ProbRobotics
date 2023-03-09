from Simulation import *
from imageProcessing import *
import numpy as np
import matplotlib.pyplot as plt
import cv2
import time


bins=50 # how many color categories to check the histogram
Aperture = 20 #see how wide the camera aperture is for obs image


import os
imageFolder=os.path.normpath(os.getcwd() + os.sep + os.pardir)
path=imageFolder+"/MarioMap.png"  #Change the name of the image file here
print(path)
MapImage=cv2.imread(path)


world=Map(path)
xminWorld,yminWorld,xmaxWorld,ymaxWorld= world.boundary() #set the boundary of the world

xmaxImage,ymaxImage = world.dimension()

drone=Drone(world) #Create a drone in the world

obsImage=cropImage(MapImage, drone.pos(),  xmaxImage, ymaxImage, m=Aperture) #create an observation image for drone
obsImage=addGaussianNoise(obsImage,m=Aperture) #add noise to the observation image from drone

N=1000
particles=[None] * N
refImage=[None] * N

#generating particles
for i in range(N):
	particles[i]= Particles(world)

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
		#generating noise for movement
		randVal=np.random.uniform(0,2*math.pi)
		noiseNx=round(math.cos(randVal), 4) * 0.1
		noiseNy=round(math.sin(randVal), 4) * 0.1

		nx= max(min(x[i] + dx +  noiseNx,xmaxWorld),xminWorld)
		ny= max(min(y[i] + dy +  noiseNy,ymaxWorld),yminWorld)

		particles[i].moveParticle(nx,ny)


#Particle filter loop 
# Run till the condition is satisfied
# Calculate mean and variance of the particles
#if the variance of the particles get below 0.1 (for example ) stop the filter and print the position


IterationCounter=0
CentroidDistanceVar = 10000
CentroidDroneVar=0
meanPosition=[]
varCentroid=[]
varDrone=[]
while not (CentroidDistanceVar < 0.4):
	IterationCounter+=1
	metric_val=[0]*N
	
	particleX=[]
	particleY=[]

	dx, dy= drone.moveStep()
	obsImage=cropImage(MapImage, drone.pos(),xmaxImage,ymaxImage,m=Aperture) #create an observation image for drone
	obsImage=addGaussianNoise(obsImage) #add noise to the observation image from drone
	obsHist = cv2.calcHist([obsImage], [0, 1, 2], None, [bins, bins, bins], [0, 256, 0, 256, 0, 256]) #Histogram of observation image
	cv2.normalize(obsHist, obsHist, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX)
	#display(obsImage, "Observation from Drone")

	ParticleImage=MapImage.copy()
	particleCoor=[]
	for i in range (N):
		#	try:

		particle_x, particle_y = particles[i].worldPos()
		ParticleImage = overlay(ParticleImage, particles[i].pos(),thickness=1 , radius2=7,color=(0,0,255)) #drawing the particles	
		particleCoor.append((particle_x,particle_y))

		refImage[i]=cropImage(MapImage, particles[i].pos(), xmaxImage,ymaxImage,m=Aperture )
		tempImage=refImage[i].copy()
		refHist = cv2.calcHist([refImage[i]], [0, 1, 2], None, [bins, bins, bins], [0, 256, 0, 256, 0, 256])
		cv2.normalize(refHist, refHist, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX)
		tempMetric=cv2.compareHist(obsHist, refHist, cv2.HISTCMP_CORREL) ** 2
		metric_val[i]= cv2.compareHist(obsHist, refHist, cv2.HISTCMP_CORREL) ** 2
		#	except:
		#		print("err",i)

	sumofweights=sum(metric_val)

	mean_particle = np.mean(particleCoor, axis=0)
	#find distance from each particle to the mean of the particles
	CentroidDistance=[]
	for i in range(N):
		CentroidDistance.append(math.sqrt((mean_particle[0] - particleCoor[i][0])**2 + (mean_particle[1] - particleCoor[i][1])**2))

	CentroidDistanceVar =np.var(CentroidDistance)
	varCentroid.append(CentroidDistanceVar)



	DroneDistance=[]

	for i in range(N):
		DroneDistance.append(math.sqrt((drone.worldPos()[0] - particleCoor[i][0])**2 + (drone.worldPos()[1] - particleCoor[i][1])**2))

	DroneDistanceVar =	np.var(DroneDistance)
	varDrone.append(DroneDistanceVar)
	#normalize the metric_val to 1 and set that as weight
	for i in range (N):
		particles[i].reweigh(metric_val[i]/sumofweights)

	resamplingFuntion(dx,dy) #RESAMPLE	the particles and move them according to the movement of the drone

	droneImage= overlay(ParticleImage,drone.pos(),text="Drone") # add  the drone on the image
	display(droneImage, "Drone")

print(IterationCounter)
#print("variances", varianceX, varianceY)
print("drone position", drone.worldPos())
print("mean of particles,", mean_particle)
display(droneImage, "Drone")
plt.plot(varCentroid, color='r', label='Variance of distance between particles and the centroid of particle cluster')
plt.plot(varDrone, color='b', label='Variance of distance between particles and the actual drone position')
plt.legend()
plt.ylabel('Error')
plt.show()
