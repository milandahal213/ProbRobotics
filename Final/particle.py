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
