import cv2
import numpy as np
import random
import math
def generate_points(image, N):
    h, w, _ = image.shape
    points = []
    for i in range(N):
        x = random.randint(0, w-1)
        y = random.randint(0, h-1)
        points.append((x, y))
    return points

def draw_particles(image, points, radius, color):
    output = image.copy()
    for point in points:
        cv2.circle(output, point, radius, color, -1)
    return output

def generate_histograms(image, points, w):
    histograms = []
    for point in points:
        x, y = point
        subimage = image[y-w//2:y+w//2+1, x-w//2:x+w//2+1]
        histogram = cv2.calcHist([subimage], [0], None, [256], [0,256])
        histograms.append(histogram)
    return histograms

def generate_drone_point(image):
    height, width, _ = image.shape
    x, y = np.random.randint(width), np.random.randint(height)
    return (x, y)

def generate_histogram(image, drone, w=100):

    # Define the coordinates of the subimage
    x, y = drone
    x1 = max(x - w//2, 0)
    x2 = min(x1 + w, image.shape[1])
    y1 = max(y - w//2, 0)
    y2 = min(y1 + w, image.shape[0])

    # Extract the subimage from the original image
    subimage = image[y1:y2, x1:x2]

    # Convert the subimage to grayscale
    gray = cv2.cvtColor(subimage, cv2.COLOR_BGR2GRAY)

    # Calculate the histogram of the subimage
    hist = cv2.calcHist([gray], [0], None, [256], [0, 256])

    # Normalize the histogram
    hist = cv2.normalize(hist, hist).flatten()

    return hist

def compare_histograms(histogram1, histogram2, method=cv2.HISTCMP_CORREL):
    """
    Compares two histograms using the specified method and returns their correlation value.
    """
    return cv2.compareHist(histogram1, histogram2, method)


def draw_drone(image, drone_pos):
    # create copy of image to avoid modifying original image
    image = np.copy(image)

    # set circle properties
    color = (0, 0, 255) # red
    thickness = 3
    radius = 10

    # draw circle at drone position
    cv2.circle(image, drone_pos, radius, color, thickness)

    return image

def generate_particle_map(image,points, drone):
    output = draw_particles(image, points, 5, (0, 255, 0))
    output=draw_drone(output,drone)
    return output


def move_drone(image, drone_pos):
    # generate random unit vector
    x = random.uniform(-1, 1)
    y = random.uniform(-1, 1)
    norm = (x**2 + y**2)**0.5
    x /= norm
    y /= norm

    # calculate new position with step size of 50 pixels
    new_x = drone_pos[0] + 20*x
    new_y = drone_pos[1] + 20*y
    
    # ensure the new position is within bounds of the image
    image_height, image_width = image.shape[:2]
    new_x = max(0, min(image_width - 1, new_x))
    new_y = max(0, min(image_height - 1, new_y))

    # if drone goes beyond the boundary, change the sign of the corresponding unit vector
    if new_x == 0 or new_x == image_width - 1:
        x *= -1
    if new_y == 0 or new_y == image_height - 1:
        y *= -1
    
    # return new position and unit vectors
    return (int(new_x), int(new_y)), (x, y)



def compare_histograms(image, points, drone_pos):

    # Calculate the subimage histograms for each point
    subimage_histograms = []
    for point in points:
        histogram = generate_histogram(image, point)
        subimage_histograms.append(histogram)

    print(subimage_histograms)
    # Calculate the histogram for the drone position
    drone_histogram = generate_histogram(image, drone_pos)

    # Calculate the correlation coefficient between each point and the drone position
    correlations = []
    for i, histogram in enumerate(subimage_histograms):
        correlation = cv2.compareHist(histogram, drone_histogram, cv2.HISTCMP_CORREL)
        correlations.append((points[i], correlation))
    sorted_correlations = sorted(correlations, key=lambda x: x[1])
    return sorted_correlations


def resample(image, points, noise_std=1.0):
    # Calculate weights based on correlation
    weights = [corr for point, corr in points]
    total_weight = sum(weights)
    normalized_weights = [weight / total_weight for weight in weights]

    # Resample points based on weights
    resampled_points = []
    while len(resampled_points) < len(points):
        random_index = random.choices(range(len(points)), weights=normalized_weights)[0]
        point = points[random_index][0]
        noisy_point = [int(np.round(p + random.gauss(0, noise_std))) for p in point]
        # ensure point is within bounds of the image
        noisy_point[0] = max(0, min(image.shape[1] - 1, noisy_point[0]))
        noisy_point[1] = max(0, min(image.shape[0] - 1, noisy_point[1]))
        resampled_points.append(tuple(noisy_point))

    return resampled_points

def move_and_noise_points(points, vector, std_dev=0.1):
    # Move the points by x and y distances
    x,y=vector
    moved_points = [(point[0] + 20*x, point[1] + 20*y) for point in points]
    
    # Add Gaussian noise to the new positions of the points
    noisy_points = [(int(np.round(point[0] + random.gauss(0, std_dev))), 
                     int(np.round(point[1] + random.gauss(0, std_dev)))) 
                    for point in moved_points]
    
    return noisy_points


def distance(point1, point2):
    return ((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)**0.5



def average_point(points):
    """
    Calculates the average point from an array of tuples or points
    
    Args:
    - points (list of tuples): List of tuples representing points with x and y coordinates
    
    Returns:
    - tuple: Tuple representing the average point with x and y coordinates
    """
    x_sum = 0
    y_sum = 0
    count = len(points)
    
    # Loop through each point and add its x and y coordinates to the sums
    for point in points:
        x_sum += point[0]
        y_sum += point[1]
    
    # Calculate the average x and y coordinates
    avg_x = x_sum / count
    avg_y = y_sum / count
    
    # Return the average point as a tuple
    return (avg_x, avg_y)

image_path = "/Users/mdahal01/Documents/GitHub/ProbRobotics/ChatGPT generated HW2/CityMap.png"
N = 1000
image = cv2.imread(image_path)
h, w, _ = image.shape
points=generate_points(image,N)
drone=generate_drone_point(image)

max_iterations = 100
threshold = 0.8 * len(points)  # majority threshold

for iteration in range(max_iterations):
    particle_map = generate_particle_map(image, points, drone)
    correlation = compare_histograms(image, points, drone)
    cv2.imshow("Particle Map", particle_map)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    
    # check if majority of particles are within 100px radius
    num_within_radius = sum([distance(point, drone) < 50 for point in points])
    if num_within_radius >= threshold:
        break
    
    drone, vector = move_drone(image, drone)
    points = resample(image, correlation)
    points = move_and_noise_points(points, vector)
    
print("Finished after {} iterations".format(iteration + 1))

centroid=average_point(points)
print("centroid= ",centroid)
print("drone= ",drone)
cv2.imshow("Particle Map", particle_map)
cv2.waitKey(0)
cv2.destroyAllWindows()
'''
for i in range(30):
	#print(drone)
	particle_map = generate_particle_map(image,points,drone)
	correlation = compare_histograms(image,points, drone)
	cv2.imshow("Particle Map", particle_map)
	cv2.waitKey(0)
	cv2.destroyAllWindows()
	drone,vector=move_drone(image, drone)
	points=resample(correlation)
	points= move_and_noise_points(points,vector)
'''