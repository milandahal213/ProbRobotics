
#setting up miro library
from talktomiro import *

#Define all the constants
n_points=30
walltext = "<p>wall</p>"
robottext = "<p>robot</p>"
frame_title="milan"
api_key = "eyJtaXJvLm9yaWdpbiI6ImV1MDEifQ_OTJW-3yJ4-iZroCFRBZrTttZzb0" #api key
board_id = "uXjVMTM_70Y%3D"

#generate frameid and frame from the constants
frame_id, frame = giveframeid( api_key, board_id,frame_title )

#find the walls and robot positions
wall_rectangles = find_rectangles_with_text_in_titled_frame(api_key, board_id, walltext, frame_title)
robot_rectangle = find_rectangle_with_text(api_key, board_id, robottext)

if not robot_rectangle:
    print(f"No rectangle with the specified text was found.")
    sys.exit()

robot_width = robot_rectangle["geometry"]["width"]
robot_height = robot_rectangle["geometry"]["height"]

positions = get_random_positions(wall_rectangles, frame, robot_width, robot_height, n_points)



#setup mqtt
import pfmqtt #library with all MQTT related functions

A=pfmqtt.MQ('10.245.144.196','milan')  #creates an MQTT object

while True:
	getch= input() 		#wait for keyboard input
	A.send('2') 		#ask the robot to move
	while(A.interimval().find('end')<0): #keep waiting for complete set of messages (with end)
		time.sleep(0.1)
		pass

	datafromrobot=completeval()  		#read the message and load it as a json string
	print(datafromrobot)
	print("E",datafromrobot["E"])
	print("W",datafromrobot["W"])
	print("N",datafromrobot["N"])
	print("S",datafromrobot["S"])



