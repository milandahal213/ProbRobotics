from Kalman import *
import math
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm

x = np.arange(-10, 50, 0.001)
fig, axs = plt.subplots(1,2)

S=np.array([[5],[1]])
B=np.array([[0],[1]]) 
SV=1   # variance of the wind
A=np.array([[1,1],[0,1]]) # the state transition matrix
G=np.array([[1/2,1]]) # relation between the acc and position and velocity (noise and states)

MV=8
C=np.array([[1,0]])
withControl=Kalman(A=A,B=B,SV=SV,G=G,S=S,MV=8,C=C) #initializing object on Kalman with only A, SV and G, no measurement and control

for i in range(5):
	s,se = withControl.predict(u=1)
	withControl.display()
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