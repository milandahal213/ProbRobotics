from Kalman import *
SV=1   # variance of wind
A=np.array([[1,1],[0,1]]) # the state transition matrix
G=np.array([[1/2,1]]) # relation between the acc and position and velocity (noise and states)
onlyPredict=Kalman(A=A,SV=SV,G=G) #initializing object on Kalman with only A, SV and G, no measurement and control
for i in range(5): # running the code for 5 time steps
	onlyPredict.predict()
	onlyPredict.display() #Displays the State and Covariance matrix on each timestep
