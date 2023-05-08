
from talktomiro import *

#Define all the constants
n_points=5
widget_id = "3458764553802833089"
walltext = "<p>wall</p>"
robottext = "<p>robot</p>"
frame_title="milan"
api_key = "eyJtaXJvLm9yaWdpbiI6ImV1MDEifQ_OTJW-3yJ4-iZroCFRBZrTttZzb0" #api key
board_id = "uXjVMTM_70Y%3D"

#generate frameid and frame from the constants
frame_id, frame = giveframeid( api_key, board_id,frame_title )
update_text_widget(board_id, widget_id, api_key, "Setting up ... ")

#find the walls and robot positions
wall_rectangles = find_rectangles_with_text_in_titled_frame(api_key, board_id, walltext, frame_title)
robot_rectangle = find_rectangle_with_text(api_key, board_id, robottext)

print("wall", wall_rectangles,"end")
if not robot_rectangle:
    print(f"No rectangle with the specified text was found.")
    sys.exit()

robot_width = robot_rectangle["geometry"]["width"]
robot_height = robot_rectangle["geometry"]["height"]
update_text_widget(board_id, widget_id, api_key, "Getting robot's data ... ")
positions = get_random_positions(wall_rectangles, frame, robot_width, robot_height, n_points)


#initialize the particle filter
update_text_widget(board_id, widget_id, api_key, "Initializing particles ... ")
all_distances =[]
ids=[]
for position in positions:
    #create_robot_position(board_id, frame["id"], position, robot_width, robot_height, api_key)
    temp=create_robot_position_circle(board_id, frame["id"], position, 10, api_key)
    distances = get_robot_distances_mt(board_id, frame_id,api_key,position, frame, robot_rectangle, wall_rectangles,False)
    all_distances.append([temp,distances])

print(all_distances)    


update_text_widget(board_id, widget_id, api_key, "Setting up MQTT ... ")
#setup mqtt
import pfmqtt #library with all MQTT related functions

A=pfmqtt.MQ('10.245.144.196','milan')  #creates an MQTT object

update_text_widget(board_id, widget_id, api_key, "Communicating with the robot ... ")
update_text_widget(board_id, widget_id, api_key, "Moving the robot particles ... ")
#creating circles instead of rectangles 