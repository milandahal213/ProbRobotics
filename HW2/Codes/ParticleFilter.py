from Simulation import *
from imageProcessing import *
import numpy as np
import matplotlib.pyplot as plt
import cv2
import time


bins=30 # how many color categories to check the histogram
Aperture = 30 #see how wide the camera aperture is for obs image



import os
imageFolder=os.path.normpath(os.getcwd() + os.sep + os.pardir)
path=imageFolder+"/BayMap.png"  #Change the name of the image file here
MapImage=cv2.imread(path)
dupMapImage=MapImage.copy()


world=Map(path)
xminWorld,yminWorld,xmaxWorld,ymaxWorld= world.boundary() #set the boundary of the world
overlayText(dupMapImage, 400,0, "Left Boundary " + str(xminWorld), radius=0)
overlayText(dupMapImage,400,40, "Top Boundary "+ str(ymaxWorld),radius=0)
overlayText(dupMapImage, 400,80, "Right Boundary "+ str(xmaxWorld),radius=0)
overlayText(dupMapImage, 400,120, "Bottom Boundary "+ str(yminWorld),radius=0)
display(dupMapImage, "With Boundaries")
xmaxImage,ymaxImage = world.dimension()


drone=Drone(world) #Create a drone in the world

Aperture = 30 #Example
InitobsImage=cropImage(MapImage, drone.pos(),  xmaxImage, ymaxImage, m=Aperture) #create an observation image for drone
InitobsImage=addGaussianNoise(InitobsImage,m=Aperture) #add noise to the observation image from drone

droneImage=overlay(MapImage,drone.pos(),text="Drone") # add  the drone on the image
display(droneImage, "Drone on Map")

display(InitobsImage, "Observation image from drone")


#generating movement

for i in range(10):
	dx, dy= drone.moveStep()
	print("velocity in terms of dx and dy :  dx = %f, dy = %f",(dx,dy))
	droneImage=overlay(droneImage,drone.pos(),text=str(i+1)) # add  the drone on the image
	display(droneImage, "Drone's random movement on the Map")



def resamplingFunction(N, particles): #kind of roulette wheel implementation
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

	return x,y # positions of newly sampled particles


def movingFunction(N,x,y, dx, dy, particles):
	for i in range(N):
		#generating noise for movement
		randVal=np.random.uniform(0,2*math.pi)
		noiseNx=round(math.cos(randVal), 4) * 0.1
		noiseNy=round(math.sin(randVal), 4) * 0.1

		nx= max(min(x[i] + dx +  noiseNx,xmaxWorld),xminWorld)
		ny= max(min(y[i] + dy +  noiseNy,ymaxWorld),yminWorld)

		particles[i].moveParticle(nx,ny)


def ErrorUsingCentroidPosition(N,particleCoor):
	mean_particle = np.mean(particleCoor, axis=0)
	#find distance from each particle to the mean of the particles
	CentroidDistance=[]
	for i in range(N):
		CentroidDistance.append(math.sqrt((mean_particle[0] - particleCoor[i][0])**2 + (mean_particle[1] - particleCoor[i][1])**2))
	CentroidDistance=np.sort(CentroidDistance)
	CentroidDistance=CentroidDistance[:-50]
	CentroidDistanceVar = np.var(CentroidDistance)
	return CentroidDistanceVar , mean_particle
	
def ErrorUsingDronePosition(N,particleCoor, drone):
	
	DroneDistance=[]
	for i in range(N):
		DroneDistance.append(math.sqrt((drone.worldPos()[0] - particleCoor[i][0])**2 + (drone.worldPos()[1] - particleCoor[i][1])**2))

	DroneDistanceVar =	np.var(DroneDistance)

	return DroneDistanceVar


def DistancebetweenCentroidandDrone(x, y,centroid):
	return (math.sqrt((x-centroid[0])**2 + (y - centroid[1])**2))


#Particle filter loop 
# Run till the condition is satisfied
# Calculate mean and variance of the particles
#if the variance of the particles get below 0.1 (for example ) stop the filter and print the position



def run( bins, Aperture):
		
	drone=Drone(world) #Create a drone in the world
	N=1000
	particles=[None] * N
	refImage=[None] * N

	#generating particles
	for i in range(N):
		particles[i]= Particles(world)

	CentroidDistanceVar = 1
	CentroidDroneVar=0
	AllActualDistance=[]
	meanPosition=[]
	varCentroid=[]
	varDrone=[]
	iteration=0


	while not (CentroidDistanceVar < 0.1):
		iteration+=1
		metric_val=[0]*N		
		dx, dy= drone.moveStep()

		obsImage=cropImage(MapImage, drone.pos(),xmaxImage, ymaxImage, m=Aperture) #create an observation image for drone
		obsImage=addGaussianNoise(obsImage,m=Aperture) #add noise to the observation image from drone

		obsHist = cv2.calcHist([obsImage], [0, 1, 2], None, [bins, bins, bins], [0, 256, 0, 256, 0, 256]) #Histogram of observation image
		cv2.normalize(obsHist, obsHist, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX)
		#display(obsImage, "Observation from Drone")

		ParticleImage=MapImage.copy()
		particleCoor=[] #to save positions of all particles
		for i in range (N):
			
			#	try:
			particle_x, particle_y = particles[i].worldPos()
			particleCoor.append((particle_x,particle_y))
		
			refImage[i]=cropImage(MapImage, particles[i].pos(), xmaxImage,ymaxImage,m=Aperture )
			tempImage=refImage[i].copy()
			refHist = cv2.calcHist([refImage[i]], [0, 1, 2], None, [bins, bins, bins], [0, 256, 0, 256, 0, 256])
			cv2.normalize(refHist, refHist, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX)
			tempMetric=(cv2.compareHist(obsHist, refHist, cv2.HISTCMP_CORREL))
			if tempMetric >0.0005:
				metric_val[i]= tempMetric
			else:
				metric_val[i]= 0.0001
			
			#	except:
			#		print("err",i)

		sumofweights=sum(metric_val)

		#normalize the metric_val to 1 and set that as weight
		t=[]
		for i in range (N):

			particles[i].reweigh(metric_val[i]/sumofweights)
			t.append(metric_val[i]/sumofweights)
			#print("i",i,",", particles[i].pos(), metric_val[i])
			ParticleImage = overlay(ParticleImage, particles[i].pos() ,thickness=1 ,color=(0,255,255)) #drawing the particles

		x,y= resamplingFunction(N,particles) #RESAMPLE	the particles that returns new positions for resampled particles
		movingFunction(N,x,y,dx,dy,particles)# move them according to the movement of the drone

		droneImage= overlay(ParticleImage,drone.pos(),text="Drone") # add  the drone on the image
		display(droneImage, "Drone")

		CentroidDistanceVar, mean_particle = ErrorUsingCentroidPosition(N,particleCoor)
		varCentroid.append(CentroidDistanceVar)

		DroneDistanceVar = ErrorUsingDronePosition(N,particleCoor, drone)
		varDrone.append(DroneDistanceVar)

		ActualDistance = DistancebetweenCentroidandDrone(drone.worldPos()[0], drone.worldPos()[1],mean_particle)
		AllActualDistance.append(ActualDistance)


	
	#print("variances", varianceX, varianceY)
	print("drone position", drone.worldPos())
	print("mean of particles,", mean_particle)
	display(droneImage, "Drone")


	ErrorinPosition= math.sqrt(((mean_particle[0]-drone.worldPos()[0])/(xmaxWorld-xminWorld)) **2 + ((mean_particle[1]-drone.worldPos()[1])/(ymaxWorld-yminWorld))**2)
	print("Error in localization with %d bins and %d aperture is %0.2f"%(bins,Aperture, ErrorinPosition), "units")

	plt.plot(varCentroid, color='r', label='Variance of distance between particles and the centroid of particle cluster')
	plt.plot(varDrone, color='b', label='Variance of distance between particles and the actual drone position')
	plt.plot(AllActualDistance, color='g', label='Distance between drone and centroid of the particles')
	plt.legend()
	plt.title("Variance in distances to the particles with %d bins and aperture size %d"%(bins,Aperture))
	plt.ylabel('Error')
	plt.xlabel('Iterations')
	plt.show()
	return ErrorinPosition, iteration

Error=[]
Iterations=[]
'''
for i in range(1,3):
	#run(bins, Aperture)
	err, iterationNum=run(i*50,50)
	Error.append(err)
	Iterations.append(iterationNum)

plt.plot(Error, color='b', label='Error  with different bins in histogram apertures on drone')
plt.plot(Iterations, color='r', label='Number of iterations required to localize drone')
plt.legend()
plt.ylabel('Error')
plt.axhline(linewidth=4, color='r')
plt.show()

'''
apert=[]
for i in range(1,10):
	#run(bins, Aperture)
	err, iterationNum=run(100,i*20)
	Error.append(err)
	Iterations.append(iterationNum)
	apert.append(i*20)


plt.plot(Iterations, color='r', label='Number of iterations required to localize drone')
plt.legend()
plt.ylabel('Number of iterations')
plt.axhline(linewidth=4, color='r')
plt.show()

plt.plot(apert,Error, color='b', label='Error  with different lens apertures on drone')
plt.legend()
plt.ylabel('Error')
plt.ylabel('Number of pixel width and height in ref image')
plt.axhline(linewidth=4, color='r')
plt.show()


