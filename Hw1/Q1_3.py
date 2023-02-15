from Kalman import *
SE=[]
SV=1   # variance of wind
A=np.array([[1,1],[0,1]]) # the state transition matrix
G=np.array([[1/2,1]]) # relation between the acc and position and velocity (noise and states)
onlyPredict=Kalman(A=A,SV=SV,G=G) #initializing object on Kalman with only A, SV and G, no measurement and control
for i in range(5): # running the code for 5 time steps
	SE.append(onlyPredict.predict())
	onlyPredict.display() #Displays the State and Covariance matrix on each timestep


import matplotlib.patches as mpatches
import matplotlib.lines as lines
import numpy as np
import matplotlib.pyplot as plt

for s,se in SE:
	#print(se)
	e_val, e_vec = np.linalg.eig(se)
	if(e_val[0]>eval[1]):
		idx_max=0
		idx_min=1
	else:
		idx_min=0
		idx_max=1



	print("eigen vectors",e_vec)
	print("eigen values",e_val)
	print("!!!!!")
	print(e_vec[0])  #eigen vectors 1
	print(e_vec[1])	#eigen vectors 2
	print("******")


'''


def get_eigen_data(eigenvects):
    if eigenvects[0][0] > eigenvects[1][0]:
        idx_max = 0
        idx_min = 1
    else:
        idx_max = 1
        idx_min = 0
        
    return {"eigvec_major": list(eigenvects[idx_max][2][0]),
            "eigvec_minor": list(eigenvects[idx_min][2][0]),
            "eigval_major": eigenvects[idx_max][0],
            "eigval_minor": eigenvects[idx_min][0],
            "theta_major": math.atan(eigenvects[idx_max][2][0][1]/
                               eigenvects[idx_max][2][0][0])*180/math.pi,
            "theta_minor": math.atan(eigenvects[idx_min][2][0][1]/
                               eigenvects[idx_min][2][0][0])*180/math.pi,
           }


ed2 = get_eigen_data(eigen2)
ed2
	# Set limits of X and Y axes

	# Add ellipse
	ell2 = mpatches.Ellipse((0,0), math.sqrt(ed2["eigval_major"])*2,
	                        math.sqrt(ed2["eigval_minor"])*2, ed2["theta_major"],
	                        fill=False, edgecolor="red")



plt.show()
# Add lines showing major and minor axes
ax_major_hor = [0 - ed2["eigvec_major"][0]*4, 0 + ed2["eigvec_major"][0]*4]
ax_major_ver = [0 - ed2["eigvec_major"][1]*4, 0 + ed2["eigvec_major"][1]*4]
ax_minor_hor = [0 - ed2["eigvec_minor"][0]*2, 0 + ed2["eigvec_minor"][0]*2]
ax_minor_ver = [0 - ed2["eigvec_minor"][1]*2, 0 + ed2["eigvec_minor"][1]*2]
plt.plot(ax_major_hor, ax_major_ver, color="grey")
plt.plot(ax_minor_hor, ax_minor_ver, color="silver")
ax.annotate("Major Axis",
            xy=(ed2["eigvec_major"][0]*3, ed2["eigvec_major"][1]*3),
            xytext=(0.6, 0.9), textcoords="axes fraction",
            xycoords="data",
            arrowprops=dict(facecolor='grey', shrink=0.05)
           )
ax.annotate("Minor Axis",
            xy=(ed2["eigvec_minor"][0], ed2["eigvec_minor"][1]),
            xytext=(0.15, 0.6), textcoords="axes fraction",
            xycoords="data",
            arrowprops=dict(facecolor='silver', shrink=0.05)
           )'''
