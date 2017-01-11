__author__ = 'philippe'
import argparse
from Tkinter import *
from random import randint, choice
master = Tk()

parser = argparse.ArgumentParser()
parser.add_argument('walls', nargs='?', action="store", type=int, default=5)
args = parser.parse_args()
triangle_size = 0.1
cell_score_min = -0.2
cell_score_max = 0.2
Width = 100
(x, y) = (7, 7)
actions = ["up", "down", "left", "right"]

board = Canvas(master, width=x*Width, height=y*Width)
player = (0, y-1)
score = 1
restart = False
walk_reward = -0.04
number_of_walls = args.walls #set number of walls
def make_walls(): #Random walls positions just to make it more... random
    walls = []
    while len(walls) < number_of_walls:
        x = randint(0, (number_of_walls-1))
        y = randint(0, (number_of_walls-1))
        wallCoord = (x,y)
        walls.append(wallCoord)
    return walls

walls = make_walls()
specials = [(4, 1, "red", -1), (4, 0, "green", 1)]
cell_scores = {}
walls_board = []

def create_triangle(i, j, action):
    if action == actions[0]:
        return board.create_polygon((i+0.5-triangle_size)*Width, (j+triangle_size)*Width,
                                    (i+0.5+triangle_size)*Width, (j+triangle_size)*Width,
                                    (i+0.5)*Width, j*Width,
                                    fill="white", width=1)
    elif action == actions[1]:
        return board.create_polygon((i+0.5-triangle_size)*Width, (j+1-triangle_size)*Width,
                                    (i+0.5+triangle_size)*Width, (j+1-triangle_size)*Width,
                                    (i+0.5)*Width, (j+1)*Width,
                                    fill="white", width=1)
    elif action == actions[2]:
        return board.create_polygon((i+triangle_size)*Width, (j+0.5-triangle_size)*Width,
                                    (i+triangle_size)*Width, (j+0.5+triangle_size)*Width,
                                    i*Width, (j+0.5)*Width,
                                    fill="white", width=1)
    elif action == actions[3]:
        return board.create_polygon((i+1-triangle_size)*Width, (j+0.5-triangle_size)*Width,
                                    (i+1-triangle_size)*Width, (j+0.5+triangle_size)*Width,
                                    (i+1)*Width, (j+0.5)*Width,
                                    fill="white", width=1)


def render_grid():
    global specials, walls, Width, x, y, player
    for i in range(x):
        for j in range(y):
            board.create_rectangle(i*Width, j*Width, (i+1)*Width, (j+1)*Width, fill="white", width=1)
            temp = {}
            for action in actions:
                temp[action] = create_triangle(i, j, action)
            cell_scores[(i,j)] = temp
    for (i, j, c, w) in specials:
        board.create_rectangle(i*Width, j*Width, (i+1)*Width, (j+1)*Width, fill=c, width=1)
    for (i, j) in walls:
        render_wall = board.create_rectangle(i*Width, j*Width, (i+1)*Width, (j+1)*Width, fill="black", width=1)
        walls_board.append(render_wall)

render_grid()


def set_cell_score(state, action, val):
    global cell_score_min, cell_score_max
    triangle = cell_scores[state][action]
    green_dec = int(min(255, max(0, (val - cell_score_min) * 255.0 / (cell_score_max - cell_score_min))))
    green = hex(green_dec)[2:]
    red = hex(255-green_dec)[2:]
    if len(red) == 1:
        red += "0"
    if len(green) == 1:
        green += "0"
    color = "#" + red + green + "00"
    board.itemconfigure(triangle, fill=color)

def wall_move():
    global x, walls, walls_board
    random_wall = randint(0,(number_of_walls-1)) #pick a random wall
    random_axis = randint(0,1) # and a random direction
    moving_axis = walls[random_wall][random_axis]
    increment = choice([-1, 1]) #going up or down?
    if (moving_axis + increment > x) or (moving_axis + increment < 0): #the movement is incorrect so move the other way
        moving_axis -= increment
    else: #correct movement
        moving_axis += increment
    new_wall = None
    if random_axis == 1: # moving axis is the y
        other_axis = walls[random_wall][0]
        new_wall = (other_axis, moving_axis)
        board.coords(walls_board[random_wall], other_axis*Width, moving_axis*Width, (other_axis+1)*Width, (moving_axis+1)*Width)
    else:  # moving axis is the x
        other_axis = walls[random_wall][1]
        new_wall = (moving_axis, other_axis)
        board.coords(walls_board[random_wall], moving_axis*Width, other_axis*Width, (moving_axis+1)*Width, (other_axis+1)*Width)
    walls[random_wall] = new_wall


def try_move(dx, dy):
    global player, x, y, score, walk_reward, me, restart, walls
    wall_move()
    if restart == True:
        restart_game()
    new_x = player[0] + dx
    new_y = player[1] + dy
    score += walk_reward
    if (new_x >= 0) and (new_x < x) and (new_y >= 0) and (new_y < y) and not ((new_x, new_y) in walls):
        board.coords(me, new_x*Width+Width*2/10, new_y*Width+Width*2/10, new_x*Width+Width*8/10, new_y*Width+Width*8/10)
        player = (new_x, new_y)
    for (i, j, c, w) in specials:
        if new_x == i and new_y == j:
            score -= walk_reward
            score += w
            if score > 0:
                print "Success! score: ", score
            else:
                print "Fail! score: ", score
            restart = True
            return
    #print "score: ", score


def call_up(event):
    try_move(0, -1)


def call_down(event):
    try_move(0, 1)


def call_left(event):
    try_move(-1, 0)


def call_right(event):
    try_move(1, 0)


def restart_game():
    global player, score, me, restart
    player = (0, y-1)
    score = 1
    restart = False
    board.coords(me, player[0]*Width+Width*2/10, player[1]*Width+Width*2/10, player[0]*Width+Width*8/10, player[1]*Width+Width*8/10)

def has_restarted():
    return restart

master.bind("<Up>", call_up)
master.bind("<Down>", call_down)
master.bind("<Right>", call_right)
master.bind("<Left>", call_left)

me = board.create_rectangle(player[0]*Width+Width*2/10, player[1]*Width+Width*2/10,
                            player[0]*Width+Width*8/10, player[1]*Width+Width*8/10, fill="orange", width=1, tag="me")

board.grid(row=0, column=0)


def start_game():
    master.mainloop()
