import math

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


import matplotlib.patches as mpatches
import matplotlib.lines as lines
import numpy as np

# Setup plot
plt.close()
fig2 = plt.figure()
ax = fig2.add_subplot(111)

# Set limits of X and Y axes
lim = 6
ax.set_xlim(-lim, lim)
ax.set_ylim(-lim, lim)
ax.set_aspect('equal', adjustable='datalim')

# Add ellipse
ell2 = mpatches.Ellipse((0,0), math.sqrt(ed2["eigval_major"])*2,
                        math.sqrt(ed2["eigval_minor"])*2, ed2["theta_major"],
                        fill=False, edgecolor="red")
ax.add_patch(ell2)

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
           )

# Add results of Monte Carlo simulation
ax.scatter(np.array(sim2_data.Position),
           np.array(sim2_data.Velocity), marker=".")

# Add titles and Labels
title = ("Robot Position at Time t = 2, 100 Replications\n"
         "covariance ellipse of 1 standard deviation")
plt.title(title)
plt.xlabel("Position")
plt.ylabel("Velocity")

fig2.show()