
from talktomiro import *
#Define all the constants

api_key = "eyJtaXJvLm9yaWdpbiI6ImV1MDEifQ_OTJW-3yJ4-iZroCFRBZrTttZzb0"
board_id = "uXjVMTM_70Y%3D"


frame_title = "milan"
frames = [
    w
    for w in get_all_widgets(api_key, board_id)
    if w["type"] == "frame" and w["data"]["title"] == frame_title
]
if not frames:
    print(f"No frames with the title '{frame_title}' were found.")
    sys.exit()

frame = frames[0]
frame_id=frame['id']
# Add the following code snippet
# Constants
pixels_per_meter = 2000
# Constants
target_height_meters = 1.5

url = f"https://api.miro.com/v2/boards/{board_id}/frames/{frame_id}"

# Set up headers
headers = {
    "accept": "application/json",
    "content-type": "application/json",
    "authorization": f"Bearer {api_key}"
}

# Fetch the current frame dimensions
current_frame_response = requests.get(url, headers=headers)
current_frame = current_frame_response.json()
current_width = current_frame["geometry"]["width"]
current_height = current_frame["geometry"]["height"]

# Calculate the new width based on the new height
new_height_pixels = target_height_meters * pixels_per_meter
new_width_pixels = current_width * (new_height_pixels / current_height)


text_to_find = "<p>wall</p>"
wall_rectangles=find_rectangles_with_text_in_titled_frame(api_key, board_id, text_to_find, frame_title)
print(len(wall_rectangles))
# Find the "robot" rectangle
text_to_find = "<p>robot</p>"
robot_rectangle = find_rectangle_with_text(api_key, board_id, text_to_find)
if not robot_rectangle:
    print(f"No rectangle with the specified text was found.")
    sys.exit()

robot_width = robot_rectangle["geometry"]["width"]
robot_height = robot_rectangle["geometry"]["height"]
step = 100  # You can adjust the step size to your preference
robot_position = (robot_rectangle["position"]["x"], robot_rectangle["position"]["y"])
positions = get_possible_positions(robot_position, wall_rectangles, frame, robot_width, robot_height, step)

# Store the reference distances for each position
reference_distances = {}
len(positions)
for position in positions:
    #print(position)
    distances = get_robot_distances(position, frame, robot_rectangle, wall_rectangles)
    #distances = line_rectangle_intersection(position, position, wall_rectangles)
    reference_distances[position] = distances
    robot_rotation = robot_rectangle["geometry"].get("rotation", 0)  # Default to 0 if rotation is not set
    #create_robot_position(board_id, frame_id, position, robot_width, robot_height, robot_rotation, api_key)

# Example: print the reference distances for each position

robot_position = robot_rectangle["position"]["x"], robot_rectangle["position"]["y"]
robot_width = robot_rectangle["geometry"]["width"]
robot_height = robot_rectangle["geometry"]["height"]
robot_rotation = robot_rectangle["geometry"].get("rotation", 0)

#step = 50
n_points=30
#positions = get_possible_positions(robot_position, wall_rectangles, frame, robot_width, robot_height, step)
positions = get_random_positions(wall_rectangles, frame, robot_width, robot_height, n_points)
print(positions)
all_distances =[]

for position in positions:
    create_robot_position(board_id, frame["id"], position, robot_width, robot_height, robot_rotation, api_key)
    distances = get_robot_distances_mt(position, frame, robot_rectangle, wall_rectangles)
    all_distances.append(distances)
print(all_distances)
    