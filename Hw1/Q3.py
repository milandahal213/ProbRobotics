from Kalman import *
S=np.array([[5],[1]])
B=np.array([[0],[1]]) 
SV=1   # variance of the wind
A=np.array([[1,1],[0,1]]) # the state transition matrix
G=np.array([[1/2,1]]) # relation between the acc and position and velocity (noise and states)

MV=8
C=np.array([[1,0]])
withControl=Kalman(A=A,B=B,SV=SV,G=G,S=S,MV=8,C=C) #initializing object on Kalman with only A, SV and G, no measurement and control

for i in range(5):
	withControl.predict(u=1)
	withControl.display()