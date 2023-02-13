from Kalman import *
SV=1   # variance of wind
A=np.array([[1,1],[0,1]]) # the state transition matrix
G=np.array([[1/2,1]]) # relation between the acc and position and velocity (noise and states)
onlyPredict=Kalman(A=A,SV=SV,G=G) #initializing object on Kalman with only A, SV and G, no measurement and control
for i in range(4): # running the code for 4 time steps , since we measure position on t=5
	onlyPredict.predict()

MV=8
C=np.array([[1,0]])
PandM= Kalman(A=A, SV=SV, G=G, MV=8, SE=SE, C=C) # we initialize a new object with the covariance matrix on t=4
PandM.predict() #we run prediciton step
PandM.update(10)
PandM.display()