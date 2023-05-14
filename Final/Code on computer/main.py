
from talktomiro import *
import time




story_widget_id = "3458764553815394100"  # Replace with the shape widget ID you want to update
start_text = '''
Hi there!
I Need your help finding my friend Mater
Chick Hicks has put a blindfold on him ...
... and put him inside the racetrack
Mater has impeccable hearing ability ...
... so he can find how far he is...
... from the objects around him.
Let's get started!
Drag the green "start" box onto the orang box'''  # Replace with your multiline text
interval = 0.2  # Time interval between updates in seconds


start_reading_text = '''Good Job!
Now, Mater is Scanning his surrounding...
...and we are now recieving his data'''



after_reading_text = '''Now, we will be...
first, assign random positions in the map
then getting the distances from all these points'''



comparing_text = '''Now, we compare the values we got from Mater...
.. with all the values we got from the points...
...to try to guess where Mater is'''

#

iterations_text = '''It looks like we have many similar distances points
We will do the same thing agian to narrow down our options'''








##########
#Define all the constants

#wait for dragging to run the code
start_box_id ="3458764553811483147"
input_frame_id="3458764553811482967"


n_points=20
widget_id = "3458764553802833089"
walltext = "<p>wall</p>"
robottext = "<p>robot</p>"
frame_title="Builds resources"
api_key = "eyJtaXJvLm9yaWdpbiI6ImV1MDEifQ_OTJW-3yJ4-iZroCFRBZrTttZzb0" #api key
board_id = "uXjVMTM_70Y%3D"
broker='10.245.144.196'
#broker ='10.0.0.141'
import pfmqtt #library with all MQTT related functions
Robot_object=pfmqtt.MQ(broker,'milan')  #creates an MQTT object


Robot_object.send('4') 
time.sleep(0.5)

speed=0
#generate frameid and frame from the constants
frame_id, frame = giveframeid( api_key, board_id,frame_title )
Robot_object.send('3') 
time.sleep(0.5)
Robot_object.send('4') 
time.sleep(0.5)

#******************************************************************************************#
update_text_widget(board_id, widget_id, api_key, "Setting up ... ")

#find the walls and robot positions
wall_rectangles = find_rectangles_with_text_in_titled_frame(api_key, board_id, walltext, frame_title)
robot_rectangle = find_rectangle_with_text(api_key, board_id, robottext)

Robot_object.send('3') 
time.sleep(0.5)
Robot_object.send('4') 
time.sleep(0.5)


robot_width = 10
robot_height = 15


update_widget_text_multiline(board_id, story_widget_id, start_text, interval, api_key)
#while(not monitor_box_position(board_id, api_key, start_box_id, input_frame_id)):
#    pass
input()
update_widget_text_multiline(board_id, story_widget_id, after_reading_text, interval, api_key)
#******************************************************************************************#
update_text_widget(board_id, widget_id, api_key, "Initializing particles ... ")
positions = get_random_positions(wall_rectangles, frame, robot_width, robot_height, n_points)
all_distances =[]  #all_distances format = [[id, x, y,[N,E,S,W],...]]

for position in positions:
    temp=create_robot_position_circle(board_id, frame["id"], position, 20,'#FFFF00' , api_key)
    distances = get_robot_distances_mt(board_id, frame_id,api_key,position, frame, robot_rectangle, wall_rectangles,False)
    all_distances.append([temp,distances])

Robot_object.send('3') 
time.sleep(0.5)
Robot_object.send('4') 
time.sleep(0.5)

print(all_distances)
#******************************************************************************************#
update_text_widget(board_id, widget_id, api_key, "Setting up MQTT on ROBOT ... ")
   


#******************************************************************************************#
                                         #wait for keyboard input

#while(not monitor_box_position(board_id, api_key, start_box_id, input_frame_id)):
getch= input() 


update_widget_text_multiline(board_id, story_widget_id, start_reading_text, interval, api_key)

Robot_object.send('2')                                 #ask the robot to move
datafromrobot=Robot_object.robot_distances()           #read the message and load it as a json string

def calculate_probability(datafromrobot,dist):
    global speed
    particle_id=dist[0][0]
    particle_x=dist[0][1]
    particle_y=dist[0][2]

    robot_north=datafromrobot["N"]*10
    robot_east=datafromrobot["E"]*10
    robot_south=datafromrobot["S"]*10
    robot_west=datafromrobot["W"]*10
    speed=datafromrobot["v"]*10

    particle_north=dist[1][0]
    particle_east=dist[1][1]
    particle_south=dist[1][2]
    particle_west=dist[1][3]

    
    
    comp= abs((robot_north-particle_north)+(robot_east-particle_east)+(robot_south-particle_south)+(robot_west-particle_west))
    print("prob",comp)
    return([comp,particle_id,particle_x,particle_y])

def resamplingFunction(N, particle_prob): #kind of roulette wheel implementation
    #generate a random number between 0 and 1
    # compare with the cummulative weight of weights until cum_weight < random number
    # take the i and find the x and y for that particle
    #set the x and y for the new partcle based on the x and y of the ith particle with noise
    # repeat for N times
    update_text_widget(board_id, widget_id, api_key, "Resampling the probabilities")
    update_widget_text_multiline(board_id, story_widget_id, comparing_text, interval, api_key)
    temp=particle_prob
    x=[0]*N
    y=[0]*N
    prob=[0]*N

    for iteration in range(N):
        randVal= np.random.uniform(low = 0, high = 1)
        i=0
        cumm_weight=0
        while cumm_weight < randVal:
            cumm_weight += temp[i][0]
            i+=1
        randomposition=random.uniform(-30,30)
        x[iteration],y[iteration],prob[iteration]=temp[i-1][2]+speed+randomposition,temp[i-1][3],temp[i-1][0]


    for i in range(len(particle_prob)):
        particle_prob[i][0]=prob[i]
        particle_prob[i][2]=x[i]
        particle_prob[i][3]=y[i]

    return particle_prob


while True:
    #### finding probablity of each particle
    particle_prob=[]
    for dist in all_distances:
        particle_prob.append(calculate_probability(datafromrobot,dist))

    robot_north=datafromrobot["N"]*10
    robot_east=datafromrobot["E"]*10
    robot_south=datafromrobot["S"]*10
    robot_west=datafromrobot["W"]*10
    speed=datafromrobot["v"]*10
    distances_recieved_text = "Mater is "+ str(robot_north) +" mm north, " + str(robot_east)+" mm east, " "  "+str(robot_south)+ " mm south, " +str(robot_west)+ " mm west"
    update_widget_text_multiline(board_id, story_widget_id, distances_recieved_text, interval, api_key)
    ##finding sum of weights for normalizing
    sumofweights=0
    for  i in range (len(particle_prob)):
        sumofweights+=particle_prob[i][0]

    ##### normalizing the probablities of each particle
    for  i in range (len(particle_prob)):
        particle_prob[i][0]=particle_prob[i][0]/sumofweights


    ##resampling the particles based on the probablity
    #[circle_id, circle_x, circle_y, circle_radius]
    particles = resamplingFunction(n_points,particle_prob)

    for particle in particles:
        update_text_widget(board_id, widget_id, api_key, "Moving the particles")
        update_circle_position_and_size(board_id, particle[1], (int(particle[2]),int(particle[3])), 20 , '#0000FF',api_key)

    print("press to continue")

    getch= input()                                         #wait for keyboard input
    Robot_object.send('2')                                 #ask the robot to move
    datafromrobot=Robot_object.robot_distances()           #read the message and load it as a json string
    update_widget_text_multiline(board_id, story_widget_id, iterations_text, interval, api_key)
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