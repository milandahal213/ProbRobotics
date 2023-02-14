
'''
Main file for Kalman Filter Assignment
Code by: Milan Dahal
Feb 13, 2023
'''

import numpy as np
import math


class Kalman:
	def __init__(self,SV=None, S=None ,MV=None, A=None, B=None, C=None, G=None, SE=None):
		self.SV=SV
		self.G=G 
		self.R= self.SV * self.G * self.G.transpose()

		self.A=A
		self.B  = 0 if B is None else B #control  to state
		self.n = self.A.shape[1]
		self.S = np.zeros((self.n,1)) if S is None else S# initial state is all zero with size n x 1
		self.SE = np.zeros((self.n, self.n )) if SE is None else SE  # initial state variance Sigma  n x x 		

		self.C=C
		self.k = 0 if C is None else self.C.shape[0]
		self.H=np.eye((self.k))

		self.MV=MV
		self.Q = self.MV * (self.H.dot(self.H.transpose())) 
		self.I = np.eye(2)

	def predict(self,u=0):
		self.S = np.dot(self.A,self.S) + np.dot(self.B,u)
		self.SE = self.A.dot(self.SE.dot(self.A.transpose())) + self.R
		return self.SE
 
	def update(self, z):
		temp=self.C.dot(self.SE.dot(self.C.transpose())) + self.Q
		Kt = self.SE .dot(self.C.transpose().dot(np.linalg.inv(temp)))
		self.S = self.S + Kt.dot(z-self.C.dot(self.S))
		self.SE=(self.I-Kt.dot(self.C)).dot(self.SE)


	def display(self):
		print("***********")
		print("State Matrix = ",self.S)
		print("Covariance Matrix = ", self.SE)
		print("***********")









