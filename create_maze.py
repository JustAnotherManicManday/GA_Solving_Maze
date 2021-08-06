# Maze generator -- Randomized Prim Algorithm

# This is Orestis Zekai's implementation of the Randomized Prim Algorithm. I have changed a couple
# of things to make it work in my program, but it's pretty much identical. Here is Orestis's github,
# https://github.com/OrWestSide/python-scripts/blob/master/maze.py. Thanks Orestis!

## Imports
import random
import numpy as np


## Functions

# Find number of surrounding cells
def surroundingCells(maze, rand_wall):
    s_cells = 0
    if (maze[rand_wall[0] - 1][rand_wall[1]] == 'c'):
        s_cells += 1
    if (maze[rand_wall[0] + 1][rand_wall[1]] == 'c'):
        s_cells += 1
    if (maze[rand_wall[0]][rand_wall[1] - 1] == 'c'):
        s_cells += 1
    if (maze[rand_wall[0]][rand_wall[1] + 1] == 'c'):
        s_cells += 1

    return s_cells

def pick_terminal_spots(maze, spot, width, height, type="spawn"):

    if spot == "top_right":
        for i in range(width):
            if maze[1][i] == 'c':
                location = [1, i]

    elif spot == "top_left":
        for i in range(width-1, 0, -1):
            if maze[1][i] == 'c':
               location = [1, i]

    elif spot == "bottom_right":
        for i in range(width):
            if (maze[height - 2][i] == 'c'):
                location = [height-2, i]

    elif spot == "bottom_left":
        for i in range(width - 1, 0, -1):
            if (maze[height - 2][i] == 'c'):
                location = [height-2, i]
    else:
        print("Unknown spot, idk what happened bud")
        return

    if type == "spawn":
        return location

    elif type == "goal":
        if location[0]==1:
            location[0] = location[0]-1

        else:
            location[0] = location[0]+1

        return location



## Main code
def make_maze(width, height):
    wall = 'w'
    cell = 'c'
    unvisited = 'u'
    # height = 11
    # width = 27
    maze = []
    # Denote all cells as unvisited
    for i in range(0, height):
        line = []
        for j in range(0, width):
            line.append(unvisited)
        maze.append(line)

    # Randomize starting point and set it a cell
    starting_height = int(random.random() * height)
    starting_width = int(random.random() * width)
    if (starting_height == 0):
        starting_height += 1
    if (starting_height == height - 1):
        starting_height -= 1
    if (starting_width == 0):
        starting_width += 1
    if (starting_width == width - 1):
        starting_width -= 1

    # Mark it as cell and add surrounding walls to the list
    maze[starting_height][starting_width] = cell
    walls = []
    walls.append([starting_height - 1, starting_width])
    walls.append([starting_height, starting_width - 1])
    walls.append([starting_height, starting_width + 1])
    walls.append([starting_height + 1, starting_width])

    # Denote walls in maze
    maze[starting_height - 1][starting_width] = 'w'
    maze[starting_height][starting_width - 1] = 'w'
    maze[starting_height][starting_width + 1] = 'w'
    maze[starting_height + 1][starting_width] = 'w'

    while (walls):
        # Pick a random wall
        rand_wall = walls[int(random.random() * len(walls)) - 1]

        # Check if it is a left wall
        if (rand_wall[1] != 0):
            if (maze[rand_wall[0]][rand_wall[1] - 1] == 'u' and maze[rand_wall[0]][rand_wall[1] + 1] == 'c'):
                # Find the number of surrounding cells
                s_cells = surroundingCells(maze, rand_wall)

                if (s_cells < 2):
                    # Denote the new path
                    maze[rand_wall[0]][rand_wall[1]] = 'c'

                    # Mark the new walls
                    # Upper cell
                    if (rand_wall[0] != 0):
                        if (maze[rand_wall[0] - 1][rand_wall[1]] != 'c'):
                            maze[rand_wall[0] - 1][rand_wall[1]] = 'w'
                        if ([rand_wall[0] - 1, rand_wall[1]] not in walls):
                            walls.append([rand_wall[0] - 1, rand_wall[1]])

                    # Bottom cell
                    if (rand_wall[0] != height - 1):
                        if (maze[rand_wall[0] + 1][rand_wall[1]] != 'c'):
                            maze[rand_wall[0] + 1][rand_wall[1]] = 'w'
                        if ([rand_wall[0] + 1, rand_wall[1]] not in walls):
                            walls.append([rand_wall[0] + 1, rand_wall[1]])

                    # Leftmost cell
                    if (rand_wall[1] != 0):
                        if (maze[rand_wall[0]][rand_wall[1] - 1] != 'c'):
                            maze[rand_wall[0]][rand_wall[1] - 1] = 'w'
                        if ([rand_wall[0], rand_wall[1] - 1] not in walls):
                            walls.append([rand_wall[0], rand_wall[1] - 1])

                # Delete wall
                for wall in walls:
                    if (wall[0] == rand_wall[0] and wall[1] == rand_wall[1]):
                        walls.remove(wall)

                continue

        # Check if it is an upper wall
        if (rand_wall[0] != 0):
            if (maze[rand_wall[0] - 1][rand_wall[1]] == 'u' and maze[rand_wall[0] + 1][rand_wall[1]] == 'c'):

                s_cells = surroundingCells(maze, rand_wall)
                if (s_cells < 2):
                    # Denote the new path
                    maze[rand_wall[0]][rand_wall[1]] = 'c'

                    # Mark the new walls
                    # Upper cell
                    if (rand_wall[0] != 0):
                        if (maze[rand_wall[0] - 1][rand_wall[1]] != 'c'):
                            maze[rand_wall[0] - 1][rand_wall[1]] = 'w'
                        if ([rand_wall[0] - 1, rand_wall[1]] not in walls):
                            walls.append([rand_wall[0] - 1, rand_wall[1]])

                    # Leftmost cell
                    if (rand_wall[1] != 0):
                        if (maze[rand_wall[0]][rand_wall[1] - 1] != 'c'):
                            maze[rand_wall[0]][rand_wall[1] - 1] = 'w'
                        if ([rand_wall[0], rand_wall[1] - 1] not in walls):
                            walls.append([rand_wall[0], rand_wall[1] - 1])

                    # Rightmost cell
                    if (rand_wall[1] != width - 1):
                        if (maze[rand_wall[0]][rand_wall[1] + 1] != 'c'):
                            maze[rand_wall[0]][rand_wall[1] + 1] = 'w'
                        if ([rand_wall[0], rand_wall[1] + 1] not in walls):
                            walls.append([rand_wall[0], rand_wall[1] + 1])

                # Delete wall
                for wall in walls:
                    if (wall[0] == rand_wall[0] and wall[1] == rand_wall[1]):
                        walls.remove(wall)

                continue

        # Check the bottom wall
        if (rand_wall[0] != height - 1):
            if (maze[rand_wall[0] + 1][rand_wall[1]] == 'u' and maze[rand_wall[0] - 1][rand_wall[1]] == 'c'):

                s_cells = surroundingCells(maze, rand_wall)
                if (s_cells < 2):
                    # Denote the new path
                    maze[rand_wall[0]][rand_wall[1]] = 'c'

                    # Mark the new walls
                    if (rand_wall[0] != height - 1):
                        if (maze[rand_wall[0] + 1][rand_wall[1]] != 'c'):
                            maze[rand_wall[0] + 1][rand_wall[1]] = 'w'
                        if ([rand_wall[0] + 1, rand_wall[1]] not in walls):
                            walls.append([rand_wall[0] + 1, rand_wall[1]])
                    if (rand_wall[1] != 0):
                        if (maze[rand_wall[0]][rand_wall[1] - 1] != 'c'):
                            maze[rand_wall[0]][rand_wall[1] - 1] = 'w'
                        if ([rand_wall[0], rand_wall[1] - 1] not in walls):
                            walls.append([rand_wall[0], rand_wall[1] - 1])
                    if (rand_wall[1] != width - 1):
                        if (maze[rand_wall[0]][rand_wall[1] + 1] != 'c'):
                            maze[rand_wall[0]][rand_wall[1] + 1] = 'w'
                        if ([rand_wall[0], rand_wall[1] + 1] not in walls):
                            walls.append([rand_wall[0], rand_wall[1] + 1])

                # Delete wall
                for wall in walls:
                    if (wall[0] == rand_wall[0] and wall[1] == rand_wall[1]):
                        walls.remove(wall)

                continue

        # Check the right wall
        if (rand_wall[1] != width - 1):
            if (maze[rand_wall[0]][rand_wall[1] + 1] == 'u' and maze[rand_wall[0]][rand_wall[1] - 1] == 'c'):

                s_cells = surroundingCells(maze, rand_wall)
                if (s_cells < 2):
                    # Denote the new path
                    maze[rand_wall[0]][rand_wall[1]] = 'c'

                    # Mark the new walls
                    if (rand_wall[1] != width - 1):
                        if (maze[rand_wall[0]][rand_wall[1] + 1] != 'c'):
                            maze[rand_wall[0]][rand_wall[1] + 1] = 'w'
                        if ([rand_wall[0], rand_wall[1] + 1] not in walls):
                            walls.append([rand_wall[0], rand_wall[1] + 1])
                    if (rand_wall[0] != height - 1):
                        if (maze[rand_wall[0] + 1][rand_wall[1]] != 'c'):
                            maze[rand_wall[0] + 1][rand_wall[1]] = 'w'
                        if ([rand_wall[0] + 1, rand_wall[1]] not in walls):
                            walls.append([rand_wall[0] + 1, rand_wall[1]])
                    if (rand_wall[0] != 0):
                        if (maze[rand_wall[0] - 1][rand_wall[1]] != 'c'):
                            maze[rand_wall[0] - 1][rand_wall[1]] = 'w'
                        if ([rand_wall[0] - 1, rand_wall[1]] not in walls):
                            walls.append([rand_wall[0] - 1, rand_wall[1]])

                # Delete wall
                for wall in walls:
                    if (wall[0] == rand_wall[0] and wall[1] == rand_wall[1]):
                        walls.remove(wall)

                continue

        # Delete the wall from the list anyway
        for wall in walls:
            if (wall[0] == rand_wall[0] and wall[1] == rand_wall[1]):
                walls.remove(wall)

    # Mark the remaining unvisited cells as walls
    for i in range(0, height):
        for j in range(0, width):
            if (maze[i][j] == 'u'):
                maze[i][j] = 'w'

    # Set entrance and exit

    options = ['top_left', 'top_right', 'bottom_left', 'bottom_right']

    start_pos = random.choice(options)
    start_pos_coord = pick_terminal_spots(maze, spot = start_pos, width=width, height=height, type="spawn")
    maze[start_pos_coord[0]][start_pos_coord[1]] = 3

    if start_pos == "top_left":
        end_pos = "bottom_right"

    elif start_pos == "top_right":
        end_pos = 'bottom_left'

    elif start_pos == 'bottom_right':
        end_pos = "top_left"
    elif start_pos == "bottom_left":
        end_pos = "top_right"

    else:
        print("I DONT KNOW WHAT HAPPENED, line 286ish")
        return

    end_pos_coord = pick_terminal_spots(maze, spot=end_pos, width=width, height=height, type="goal")

    maze[end_pos_coord[0]][end_pos_coord[1]] = 2

    for i in range(height):
        for j in range(width):
            if maze[i][j] == "c":
                maze[i][j] = 0
            elif maze[i][j] == "w":
                maze[i][j] = 1
            else:
                continue

    maze = np.array(maze)
    new_shape = (1, width*height)
    maze = maze.reshape(new_shape)[0]
    return maze

