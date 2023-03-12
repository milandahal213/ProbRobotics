# How to use
1. Download the entire folder to your computer
2. Run the ParticleFilter.py from the Codes folder
3. You may need to install Matplotlib, OpenCV and Numpy libraries on your computer
  Follow the steps from https://matplotlib.org/stable/users/installing/index.html, https://pypi.org/project/opencv-python/ and https://numpy.org/install/ 

4. ParticleFilter.py uses two other python files i.e. imageProcessing.py  and Simulation,py. So make sure to keep them in the same folder. 



# How does it work? 
First thing the code does is opens the image file . You can choose the file you want to open and run. 
Then it creates an object with class Map. The class Map has functions that can find the boundaries, convert world coordinates to image coordinates, etc. 

After getting the world boundaries, a drone is created using Drone class within the World class. The Drone class has functions that can find the position of the drone, move the drone as well as convert the position of drone from and to world and image coordinates. 


