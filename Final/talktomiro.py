
import requests
import random
import time
from math import floor
import math
import keyboard
import itertools
from typing import List, Tuple, Dict, Any
import sys
import numpy as np
from scipy.stats import norm



def get_all_widgets(api_key, board_id):
    url = f"https://api.miro.com/v2/boards/{board_id}/items?limit=50"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Accept": "application/json"
    }
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        return response.json()["data"]

    else:
        print(f"Error: Unable to retrieve widgets. Status code {response.status_code}")
        return []


def giveframeid(api_key,board_id,frame_title):
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
	return frame_id , frame




def get_all_items_within_frame(api_key, board_id, frame_id):
    url = "https://api.miro.com/v2/boards/"+board_id+"/items?parent_item_id="+frame_id+"&limit=50"
    print(url)
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Accept": "application/json"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()["data"]
    else:
        print(f"Error: Unable to retrieve widgets. Status code {response.status_code}")
        return []    


def find_rectangle_with_text(api_key, board_id, text):
    widgets = get_all_widgets(api_key, board_id)
    rectangles = [w for w in widgets if w["type"] == "shape" and w["data"]["shape"] == "rectangle"]

    for rect in rectangles:
        for widget in widgets:
            if widget["type"] == "shape" and text in widget["data"]["content"]:
                if abs(widget["position"]["x"] - rect["position"]["x"]) < rect["geometry"]["width"] / 2 and abs(widget["position"]["y"] - rect["position"]["y"]) < rect["geometry"]["height"] / 2:
                    return rect
    return None    

def find_rectangles_with_text_in_titled_frame(api_key, board_id, text, frame_title):
    widgets = get_all_widgets(api_key, board_id)
    
    frames = [w for w in widgets if w["type"] == "frame" and w["data"]["title"] == frame_title]
    
    if not frames:
        print(f"No frames with the title '{frame_title}' were found.")
        return []

    target_frame = frames
    print(f"Targeted Frame : {target_frame[0]}")
    frame_id = target_frame[0]['id']

    frame_items = get_all_items_within_frame(api_key, board_id, frame_id)

    rectangles = [f for f in frame_items if 'shape' in f["type"] and text in f["data"]["content"]]
   
    return rectangles



def move_widget(api_key, board_id, widget_id, new_position):
    url = f"https://api.miro.com/v2/boards/{board_id}/shapes/{widget_id}"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    payload = {
        "data": {"shape": "rectangle"},
        "position": new_position
    }
    response = requests.patch(url, json=payload, headers=headers)

    if response.status_code != 200:
        print(f"Error: Unable to move widget. Status code {response.status_code}")



def create_connector(api_key, board_id, start_position, end_position, rec_id):
    url = f"https://api.miro.com/v2/boards/{board_id}/widgets"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    payload = {
        "shape": "straight",
        "id": rec_id,
        "startItem": start_position,
        "endItem": end_position
    }
    response = requests.post(url, json=payload, headers=headers)

    if response.status_code == 201:
        return response.json()
    else:
        print(f"Error: Unable to create connector. Status code {response.status_code}")
        return None


def convert_pixels_to_mm(pixels):
    dpi = 96  # dots per inch
    inches = pixels / dpi
    mm = inches * 25.4
    return mm

def distance(point1, point2):
    return ((point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2) ** 0.5



def move_randomly_within_range(api_key, board_id, widget_id, x_range, y_range):
    widgets = get_all_widgets(api_key, board_id)
    widget = next(w for w in widgets if w["id"] == widget_id)

    current_position = widget["position"]

    new_x = random.uniform(current_position["x"] - x_range, current_position["x"] + x_range)
    new_y = random.uniform(current_position["y"] - y_range, current_position["y"] + y_range)

    new_position = {"x": round(new_x), "y": round(new_y)}
    move_widget(api_key, board_id, widget_id, new_position)

def get_distance_to_closest_wall(robot_position, robot_orientation, walls):
    min_distance = float('inf')
    closest_wall = None

    for wall in walls:
        # Calculate the intersection between the robot's line of sight and the wall
        intersection_point = intersection(wall, robot_position, robot_orientation)
        
        if intersection_point:
            distance_to_wall = distance(robot_position, intersection_point)
            if distance_to_wall < min_distance:
                min_distance = distance_to_wall
                closest_wall = wall

    return min_distance


def is_overlapping(robot_position, robot_width, robot_height, wall_position, wall_width, wall_height):
    x_dist = abs(robot_position[0] - wall_position[0])
    y_dist = abs(robot_position[1] - wall_position[1])

    combined_width = (robot_width + wall_width) / 2
    combined_height = (robot_height + wall_height) / 2

    return x_dist < combined_width and y_dist < combined_height

def measure_distance(position, direction, wall_rectangles):
    min_distance = float("inf")
    target_point = position[0] + direction[0] * 2000, position[1] + direction[1] * 2000
    for wall_rectangle in wall_rectangles:
        wall_rect = get_wall_rectangle(wall_rectangle)
        clipped_line = cohen_sutherland_line_clip((position, target_point), wall_rect)
        print(f"clipped_line: {clipped_line}")
        if clipped_line is None:
            continue
        clipped_end = (clipped_line[2], clipped_line[3])
        distance = math.sqrt((position[0] - clipped_end[0]) ** 2 + (position[1] - clipped_end[1]) ** 2)
        if distance < min_distance:
            min_distance = distance
    return min_distance


def get_wall_rectangle(rectangle):
    x_min = rectangle["position"]["x"] - rectangle["geometry"]["width"] / 2
    y_min = rectangle["position"]["y"] - rectangle["geometry"]["height"] / 2
    x_max = rectangle["position"]["x"] + rectangle["geometry"]["width"] / 2
    y_max = rectangle["position"]["y"] + rectangle["geometry"]["height"] / 2
    return ((x_min, y_min), rectangle["geometry"]["width"], rectangle["geometry"]["height"])


def cohen_sutherland_line_clip(line, rect):
    # Define the constants for the outcodes
    INSIDE, LEFT, RIGHT, BOTTOM, TOP = 0b0000, 0b0001, 0b0010, 0b0100, 0b1000
    #print(f"Line: {line}, Rect: {rect}")
    def compute_outcode(x, y):
        outcode = INSIDE
        if x < x_min:
            outcode |= LEFT
        elif x > x_max:
            outcode |= RIGHT
        if y < y_min:
            outcode |= BOTTOM
        elif y > y_max:
            outcode |= TOP
        return outcode

    x_min, y_min = rect[0][0] - rect[1] / 2, rect[0][1] - rect[2] / 2
    x_max, y_max = rect[0][0] + rect[1] / 2, rect[0][1] + rect[2] / 2

    x0, y0 = line[0]
    x1, y1 = line[1]

    outcode0 = compute_outcode(x0, y0)
    outcode1 = compute_outcode(x1, y1)

    #print(f"Outcodes: {outcode0}, {outcode1}")

    while True:
        if not (outcode0 | outcode1):
            return x0, y0, x1, y1
        elif outcode0 & outcode1:
            return None
        else:
            outcode_out = outcode0 or outcode1
            if outcode_out & TOP:
                x = x0 + (x1 - x0) * (y_max - y0) / (y1 - y0)
                y = y_max
            elif outcode_out & BOTTOM:
                x = x0 + (x1 - x0) * (y_min - y0) / (y1 - y0)
                y = y_min
            elif outcode_out & RIGHT:
                y = y0 + (y1 - y0) * (x_max - x0) / (x1 - x0)
                x = x_max
            elif outcode_out & LEFT:
                y = y0 + (y1 - y0) * (x_min - x0) / (x1 - x0)
                x = x_min
            else:
                raise RuntimeError("Unexpected case in Cohen-Sutherland line clipping algorithm")

            if outcode_out == outcode0:
                x0, y0 = x, y
                outcode0 = compute_outcode(x0, y0)
            else:
                x1, y1 = x, y
                outcode1 = compute_outcode(x1, y1)
            #print(f"New coordinates: ({x0}, {y0}), ({x1}, {y1})")
            #create_thin_rectangle(board_id, frame_id, (x0, y0), (x1, y1), api_key)




def measure_distance(position, direction, walls):
    """
    Measure the distance between the current position and the nearest wall in a given direction.
    
    :param position: The current position of the robot as a tuple (x, y).
    :param direction: The direction to measure the distance in as a tuple (dx, dy).
    :param walls: A list of wall rectangles as dictionaries with "geometry" and "position" keys.
    :return: The distance to the nearest wall in the given direction.
    """
    min_distance = float('inf')
    for wall in walls:
        intersection = line_rectangle_intersection(position, direction, wall)
        if intersection:
            distance = math.sqrt((intersection[0] - position[0]) ** 2 + (intersection[1] - position[1]) ** 2)
            min_distance = min(min_distance, distance)
    return min_distance

def get_random_positions(wall_rectangles, frame, robot_width, robot_height, n_points):
	positions = []
	
	frame_x_min, frame_y_min = 0, 0
	frame_x_max, frame_y_max = frame['geometry']['width'], frame['geometry']['height']
	for n in range(n_points):
		temp=True
		while temp:
			x=random.randrange(int(frame_x_min + robot_width / 2), int(frame_x_max - robot_width / 2))
			y=random.randrange(int(frame_y_min + robot_height / 2), int(frame_y_max - robot_height / 2))
			position = (x, y)
			temp=any(rectangle_collision(position, robot_width, robot_height, wall_rect) for wall_rect in wall_rectangles)
	
		positions.append(position)

	return positions


def get_possible_positions(robot_position, wall_rectangles, frame, robot_width, robot_height, step):
    positions = []

    frame_x_min, frame_y_min = 0, 0
    frame_x_max, frame_y_max = frame['geometry']['width'], frame['geometry']['height']

    num_x_steps = int((frame_x_max - frame_x_min - robot_width) / step) + 1
    num_y_steps = int((frame_y_max - frame_y_min - robot_height) / step) + 1

    for x in np.linspace(frame_x_min + robot_width / 2, frame_x_max - robot_width / 2, num_x_steps):
        for y in np.linspace(frame_y_min + robot_height / 2, frame_y_max - robot_height / 2, num_y_steps):
            position = (x, y)

            if not any(rectangle_collision(position, robot_width, robot_height, wall_rect) for wall_rect in wall_rectangles):
                positions.append(position)

    return positions





def rectangle_collision(position, robot_width, robot_height, wall_rectangle):
    robot_center = position
    wall_center = (wall_rectangle["position"]["x"], wall_rectangle["position"]["y"])
    wall_width = wall_rectangle["geometry"]["width"]
    wall_height = wall_rectangle["geometry"]["height"]

    x_distance = abs(robot_center[0] - wall_center[0])
    y_distance = abs(robot_center[1] - wall_center[1])

    total_width = (robot_width + wall_width) / 2
    total_height = (robot_height + wall_height) / 2

    return x_distance < total_width and y_distance < total_height



def rectangle_contains_point(point, wall_rectangle):
    x, y = point
    rect_center = (wall_rectangle["position"]["x"], wall_rectangle["position"]["y"])
    rect_width = wall_rectangle["geometry"]["width"]
    rect_height = wall_rectangle["geometry"]["height"]

    x_min = rect_center[0] - rect_width / 2
    x_max = rect_center[0] + rect_width / 2
    y_min = rect_center[1] - rect_height / 2
    y_max = rect_center[1] + rect_height / 2

    return x_min <= x <= x_max and y_min <= y <= y_max




def is_position_inside_walls(position, robot_width, robot_height, walls):
    robot_rect = {
        "left": position[0] - robot_width / 2,
        "right": position[0] + robot_width / 2,
        "top": position[1] - robot_height / 2,
        "bottom": position[1] + robot_height / 2,
    }

    for wall in walls:
        wall_rect = {
            "left": wall["position"]["x"] - wall["geometry"]["width"] / 2,
            "right": wall["position"]["x"] + wall["geometry"]["width"] / 2,
            "top": wall["position"]["y"] - wall["geometry"]["height"] / 2,
            "bottom": wall["position"]["y"] + wall["geometry"]["height"] / 2,
        }

        if (
            robot_rect["left"] < wall_rect["right"]
            and robot_rect["right"] > wall_rect["left"]
            and robot_rect["top"] < wall_rect["bottom"]
            and robot_rect["bottom"] > wall_rect["top"]
        ):
            return True  # This line was changed from "return False"

    return False  # This line was changed from "return True"


def point_to_line_distance(point, line):
    x0, y0 = point
    x1, y1 = line[0]
    x2, y2 = line[1]
    p1=(x1,y1)
    p2=(x2,y2)
    p0=(x0,y0)
    p0 = np.asarray(p0)
    p1 = np.asarray(p1)
    p2 = np.asarray(p2)

    num = abs((y2 - y1) * x0 - (x2 - x1) * y0 + x2 * y1 - y2 * x1)
    den = math.sqrt((y2 - y1) ** 2 + (x2 - x1) ** 2)
    #d = norm(np.cross(p2-p1, p1-p0))/norm(p2-p1)
    #return d
    return num / den

def get_robot_distances(position, frame, robot_rectangle, wall_rectangles):
    distances = {"front": float(100000), "left": float(100000), "right": float(100000)}
    directions = {"front": (0, -1), "left": (-1, 0), "right": (1, 0)}

    for direction, vector in directions.items():
        start_point = position
        end_point = (position[0] + vector[0] * 100000, position[1] + vector[1] * 100000)
        #print(end_point)
        line = (start_point, end_point)

        for wall_rectangle in wall_rectangles:
            wall_center = (wall_rectangle["position"]["x"], wall_rectangle["position"]["y"])
            wall_width = wall_rectangle["geometry"]["width"]
            wall_height = wall_rectangle["geometry"]["height"]

            x_min = wall_center[0] - wall_width / 2
            x_max = wall_center[0] + wall_width / 2
            y_min = wall_center[1] - wall_height / 2
            y_max = wall_center[1] + wall_height / 2

            wall_lines = [
                ((x_min, y_min), (x_min, y_max)),
                ((x_min, y_max), (x_max, y_max)),
                ((x_max, y_max), (x_max, y_min)),
                ((x_max, y_min), (x_min, y_min))
            ]

            for wall_line in wall_lines:
                intersection = line_intersection(line, wall_line)
                if intersection:
                    distance = math.sqrt((intersection[0] - position[0]) ** 2 + (intersection[1] - position[1]) ** 2)
                    #print(distance)
                    if distance < distances[direction]:
                        distances[direction] = distance
                #else:
                    #print('no intersection')
    #for direction, distance in distances.items():
        #if math.isinf(distance) or math.isnan(distance):
            #print(f"Invalid distance ({distance}) for direction: {direction}")

    return distances

def get_robot_distances_mt(board_id, frame_id,api_key,position, frame, robot_rectangle, wall_rectangles, create):
    #distances = {"north": float("inf"),"south": float("inf"), "left": float("inf"), "right": float("inf")}
    distances = [0,0,0,0]
    directions = {"front": (0, -1),"back": (0, 1), "left": (-1, 0), "right": (1, 0)}
    orientations = (0,90,180,270) # 0 back, 90 right, 180 front, 270 left
    x_r=position[0]
    y_r=position[1]
    d_n=[10000]
    d_e=[10000]
    d_s=[10000]
    d_w=[10000]
    intersect = False
    for orientation in orientations:
        for wall_rectangle in wall_rectangles:
            wall_center = (wall_rectangle["position"]["x"], wall_rectangle["position"]["y"])
            wall_width = wall_rectangle["geometry"]["width"]
            wall_height = wall_rectangle["geometry"]["height"]

            x_min = wall_center[0] - wall_width / 2
            x_max = wall_center[0] + wall_width / 2
            y_min = wall_center[1] - wall_height / 2
            y_max = wall_center[1] + wall_height / 2

            x_tl=x_min
            x_tr=x_max
            x_bl=x_min
            x_br=x_max
            y_tr=y_max
            y_tl=y_max
            y_br=y_min
            y_bl=y_min
            
            wall_lines = [
                ((x_min, y_min), (x_min, y_max)),
                ((x_min, y_max), (x_max, y_max)),
                ((x_max, y_max), (x_max, y_min)),
                ((x_max, y_min), (x_min, y_min))
            ]
            #print(orientation)
            #print(y_r,y_bl)
            if orientation == 0: #north
                #print('im here')
                #print(y_r , y_tr , x_r , x_tl , x_r , y_tr)
                #print(y_r,y_bl)
                if (y_r > y_bl) and (x_r > x_bl and x_r < x_br):
                    #print(y_r,y_bl)
                    d_n.append(abs(y_r-y_tl))
                    intersect = True
            
            elif orientation == 90: #east
                #print(x_r,x_tl, y_r,y_tl, y_r ,y_bl)
                if (x_r <x_tl) and (y_r < y_tl and y_r > y_bl):
                    d_e.append(abs(x_tl-x_r))
                    intersect = True
            
            elif orientation == 180: #south
            	if (y_r < y_bl) and (x_r > x_bl and x_r < x_br):
 
            		d_s.append(abs(y_bl-y_r))
            		intersect = True

            elif orientation == 270: #west
                #print(x_r , x_tr , y_r , y_tl , y_r , y_bl)
                if (x_r > x_tr) and (y_r < y_tl and y_r > y_bl):
                    #print('im not here')
                    d_w.append(abs(x_r-x_tr))
                    intersect = True
    #print(d_n)
    #north:
    distances[0]= min(d_n)
    #east:
    distances[1]= min(d_e)
    #south:
    distances[2]= min(d_s)
    #west:
    distances[3]= min(d_w)
    #print(distances, position, len(d_s))

    if(create):
	    create_thin_rectangle(board_id, frame_id, position, (position[0], position[1]-distances[0]), api_key)
	    create_thin_rectangle(board_id, frame_id, position, (position[0]+distances[1],position[1]), api_key)
	    create_thin_rectangle(board_id, frame_id, position, (position[0],position[1]+distances[2]), api_key)
	    create_thin_rectangle(board_id, frame_id, position, (position[0]-distances[3],position[1]), api_key)

    return distances



def line_intersection(line1, line2):
    x1, y1 = line1[0]
    x2, y2 = line1[1]
    x3, y3 = line2[0]
    x4, y4 = line2[1]

    den = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
    if den == 0:
        #print('den is zero')
        return None

    px = ((x1 * y2 - y1 * x2) * (x3 - x4) - (x1 - x2) * (x3 * y4 - y3 * x4)) / den
    py = ((x1 * y2 - y1 * x2) * (y3 - y4) - (y1 - y2) * (x3 * y4 - y3 * x4)) / den

    if px >= min(x1, x2) and px <= max(x1, x2) and py >= min(y1, y2) and py <= max(y1, y2) and \
       px >= min(x3, x4) and px <= max(x3, x4) and py >= min(y3, y4) and py <= max(y3, y4):
        return px, py
    else:
        return None







def line_rectangle_intersection(p1, p2, rect):
    x1, y1 = p1
    x2, y2 = p2
    x, y = rect["position"]["x"], rect["position"]["y"]
    width, height = rect["geometry"]["width"], rect["geometry"]["height"]

    left = x - width / 2
    right = x + width / 2
    top = y - height / 2
    bottom = y + height / 2

    if x1 == x2:  # vertical line
        if left <= x1 <= right:
            if y1 <= top and top <= y2:
                return x1, top
            elif y1 >= bottom and bottom >= y2:
                return x1, bottom
    elif y1 == y2:  # horizontal line
        if top <= y1 <= bottom:
            if x1 <= left and left <= x2:
                return left, y1
            elif x1 >= right and right >= x2:
                return right, y1
    else:
        m = (y2 - y1) / (x2 - x1)
        b = y1 - m * x1

        y_at_left = m * left + b
        y_at_right = m * right + b
        x_at_top = (top - b) / m
        x_at_bottom = (bottom - b) / m

        if top <= y_at_left <= bottom:
            return left, y_at_left
        elif top <= y_at_right <= bottom:
            return right, y_at_right
        elif left <= x_at_top <= right:
            return x_at_top, top
        elif left <= x_at_bottom <= right:
            return x_at_bottom, bottom

    return None

def create_thin_rectangle(board_id, frame_id, start_point, end_point, api_key):
    url = f"https://api.miro.com/v2/boards/{board_id}/shapes"

    x1, y1 = start_point
    x2, y2 = end_point
    #print(x1, y1)
    #print(x2, y2)
    width = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
    angle = math.degrees(math.atan2(y2 - y1, x2 - x1))

    payload = {
        "data": {
            "shape": "rectangle"
        },
        "geometry": {
                "rotation": angle,
                "width": width,
                "height": 8  # Set the height of the rectangle to a small value to make it look like a line
            },
        "position": {
            "origin": "center",
            "x": (x1 + x2) / 2,
            "y": (y1 + y2) / 2
        },
        "parent": {"id": frame_id}
    }
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "authorization": f"Bearer {api_key}"
    }

    response = requests.post(url, json=payload, headers=headers)
    return response.text



def create_robot_position(board_id, frame_id, position, width, height, api_key):
    url = f"https://api.miro.com/v2/boards/{board_id}/shapes"
    #print(position[0],position[1])
    payload = {
        "data": {
            "shape": "rectangle",
        },
        "geometry": {
            "width": width,
            "height": height,
            "rotation": 0
        },
        "position": {
            "origin": "center",
            "x": position[0],
            "y": position[1]
        },
        "parent": {"id": frame_id}
        
    }
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "authorization": f"Bearer {api_key}"
    }

    response = requests.post(url, json=payload, headers=headers)
    return response.text



def update_circle_position_and_size(board_id, circle_widget_id, new_position, new_diameter, api_key):
    url = f"https://api.miro.com/v1/boards/{board_id}/widgets/{circle_widget_id}"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "position": {"x": new_position[0], "y": new_position[1]},
        "geometry": {"radius": new_diameter / 2}
    }

    response = requests.patch(url, headers=headers, json=data)

    if response.status_code == 200:
        return True
    else:
        return False


def update_text_widget(board_id: str, widget_id: str, api_key: str, new_text: str,) -> bool:
    update_data = {
        "text": new_text
    }
    response = requests.patch(
        f"https://api.miro.com/v1/boards/{board_id}/widgets/{widget_id}",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        },
        json=update_data
    )

    if response.status_code == 200:
        return True
    else:
        print(f"Error updating text widget: {response.status_code} - {response.text}")
        return False


def create_robot_position_circle(board_id, frame_id, position,radius, api_key):
    url = f"https://api.miro.com/v2/boards/{board_id}/shapes"
    #print(position[0],position[1])
    payload = {
        "data": {
            "shape": "circle",
        },
        "style":{"fillColor":"#0000FF"},
        "geometry": {
            "height": radius,
            "width": radius,
        },
        "position": {
            "origin": "center",
            "x": position[0],
            "y": position[1]
        },
        "parent": {"id": frame_id}
        
    }
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "authorization": f"Bearer {api_key}"
    }

    response = requests.post(url, json=payload, headers=headers)

    return response.json()["id"],response.json()["position"]["x"],response.json()["position"]["y"]
