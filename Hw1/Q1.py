from Kalman import *
import math
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm

x = np.arange(-10, 20, 0.001)
fig, axs = plt.subplots(1,2)

SV=1   # variance of wind
A=np.array([[1,1],[0,1]]) # the state transition matrix
G=np.array([[1/2,1]]) # relation between the acc and position and velocity (noise and states)
onlyPredict=Kalman(A=A,SV=SV,G=G) #initializing object on Kalman with only A, SV and G, no measurement and control

for i in range(5): # running the code for 5 time steps
	s,se=onlyPredict.predict()
	onlyPredict.display() #Displays the State and Covariance matrix on each timestep
	pos=s[0]
	posvar= se[0][0]
	possig=math.sqrt(posvar)

	vel=s[1]
	velvar=se[1][1]
	velsig=math.sqrt(velvar)

	
	axs[0].plot(x, norm.pdf(x, pos, possig), label='time: %d, position: %d, σ: %0.2f'%(i,pos,possig))
	axs[0].legend()
	axs[1].plot(x, norm.pdf(x, vel, velsig), label='time: %d, velocity: %d, σ: %0.2f'%(i,vel,velsig))
	axs[1].legend()

plt.show()