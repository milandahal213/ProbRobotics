from Kalman import *
import math
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm

x = np.arange(-10, 20, 0.001)


SV=1   # variance of the wind
A=np.array([[1,1],[0,1]]) # the state transition matrix
G=np.array([[1/2,1]]) # relation between the acc and position and velocity (noise and states)
onlyPredict=Kalman(A=A,SV=SV,G=G) #initializing object on Kalman with only A, SV and G, no measurement and control
for i in range(4): # running the code for 4 time steps , since we measure position on t=5
	s,se= onlyPredict.predict()

MV=8
C=np.array([[1,0]])
PandM= Kalman(A=A, SV=SV, G=G, MV=8, SE=se, C=C) # we initialize a new object with the covariance matrix on t=4

PandM.predict() #we run prediciton step

pos=s[0]
posvar= se[0][0]
possig=math.sqrt(posvar)

vel=s[1]
velvar=se[1][1]
velsig=math.sqrt(velvar)

#plotting previous estimated states
plt.plot(x, norm.pdf(x, pos, possig), label='position: %d, σ: %0.2f'%(pos,possig))
plt.legend()


#plotting the measurement
plt.plot(x, norm.pdf(x, 10, 8), label='position: %d, σ: %0.2f'%(10,8))
plt.legend()


s,se=PandM.update(10)

#plotting after the update
pos=s[0]
posvar= se[0][0]
possig=math.sqrt(posvar)

vel=s[1]
velvar=se[1][1]
velsig=math.sqrt(velvar)


plt.plot(x, norm.pdf(x, pos, possig), label='position: %d, σ: %0.2f'%(pos,possig))
plt.legend()


PandM.display()

plt.show()