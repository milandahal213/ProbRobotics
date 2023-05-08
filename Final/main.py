
from talktomiro import *

#Define all the constants
n_points=1
widget_id = "3458764553802833089"
walltext = "<p>wall</p>"
robottext = "<p>robot</p>"
frame_title="milan"
api_key = "eyJtaXJvLm9yaWdpbiI6ImV1MDEifQ_OTJW-3yJ4-iZroCFRBZrTttZzb0" #api key
board_id = "uXjVMTM_70Y%3D"
broker='10.245.144.196'


#generate frameid and frame from the constants
frame_id, frame = giveframeid( api_key, board_id,frame_title )

#******************************************************************************************#
update_text_widget(board_id, widget_id, api_key, "Setting up ... ")

#find the walls and robot positions
wall_rectangles = find_rectangles_with_text_in_titled_frame(api_key, board_id, walltext, frame_title)
robot_rectangle = find_rectangle_with_text(api_key, board_id, robottext)


if not robot_rectangle:
    print(f"No rectangle with the specified text was found.")
    sys.exit()

robot_width = robot_rectangle["geometry"]["width"]
robot_height = robot_rectangle["geometry"]["height"]





#******************************************************************************************#
update_text_widget(board_id, widget_id, api_key, "Initializing particles ... ")
positions = get_random_positions(wall_rectangles, frame, robot_width, robot_height, n_points)
all_distances =[]  #all_distances format = [[id, x, y,[N,E,S,W],...]]

for position in positions:

    temp=create_robot_position_circle(board_id, frame["id"], position, 20, api_key)
    distances = get_robot_distances_mt(board_id, frame_id,api_key,position, frame, robot_rectangle, wall_rectangles,False)
    all_distances.append([temp,distances])


#******************************************************************************************#
update_text_widget(board_id, widget_id, api_key, "Setting up MQTT on ROBOT ... ")
   
import pfmqtt #library with all MQTT related functions

Robot_object=pfmqtt.MQ(broker,'milan')  #creates an MQTT object


#******************************************************************************************#
getch= input()                                         #wait for keyboard input
Robot_object.send('2')                                 #ask the robot to move
datafromrobot=Robot_object.robot_distances()           #read the message and load it as a json string

def calculate_probability(datafromrobot,dist):
    particle_id=dist[0][0]
    particle_x=dist[0][1]
    particle_y=dist[0][2]

    robot_north=datafromrobot["N"]
    robot_east=datafromrobot["E"]
    robot_south=datafromrobot["S"]
    robot_west=datafromrobot["W"]

    particle_north=dist[1][0]
    particle_east=dist[1][1]
    particle_south=dist[1][2]
    particle_west=dist[1][3]
    prob= (robot_north-particle_north)+(robot_east-particle_east)+(robot_south-particle_south)+(robot_west-particle_west)
    return(particle_id,particle_x,particle_y,prob)



particle_prob=[]
for dist in all_distances:
    particle_prob.append(calculate_probability(datafromrobot,dist))

print(particle_prob)


#******************************************************************************************#
#create_robot_position(board_id, frame["id"], position, robot_width, robot_height, api_key) #draws rectangles for distances
#update_text_widget(board_id, widget_id, api_key, "Getting robot's data ... ")
'''
update_text_widget(board_id, widget_id, api_key, "Setting up MQTT ... ")
#setup mqtt
import pfmqtt #library with all MQTT related functions

A=pfmqtt.MQ('10.245.144.196','milan')  #creates an MQTT object

update_text_widget(board_id, widget_id, api_key, "Communicating with the robot ... ")
update_text_widget(board_id, widget_id, api_key, "Moving the robot particles ... ")
#creating circles instead of rectangles 
'''