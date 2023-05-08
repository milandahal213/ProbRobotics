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


iteration=0
#wait till status
#if continue 
	#run the loop
# if Done 
	#stop the loop and 
#loop
	iteration+=1
	metric_val=[0]*N		
	
	dx, dy= #new x and y from the robot

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