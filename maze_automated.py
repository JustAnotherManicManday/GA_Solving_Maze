from pygame.locals import *
import pygame
from time import sleep
from math import sqrt
import random
import numpy as np
import os
import create_maze

# Most of the pygame, maze-related code comes from https://pythonspot.com/maze-in-pygame/

# ********************************************************************
# Constants
MAZE_WIDTH = 25
MAZE_HEIGHT = 20
NUM_MOVES = 200
WINDOW_X = MAZE_WIDTH * 44
WINDOW_Y = MAZE_HEIGHT * 44 + 40
WHITE = (255, 255, 255)
TEXT_Y = WINDOW_Y - 30#WINDOW_Y * 23/24
TEXT_X = 110 #WINDOW_X/8
TEXT_SIZE = 16
FIT_FUNC = "distance" # "unique" or "distance"
NUM_PLAYERS = 900
MUTATION_RATE = 0.2
SELECTION_CUTOFF = 0.1
PLAYER_SPEED = 44 #num of pixels the player moves, leave it at 44
MOVE_OPTIONS = np.array(["right", "left", "up", "down"])
DEAD_END_PENALTY = 200
MADEIT_THRESH = 0 # Put zero if only one duck will do
QUACKS_FILEPATH = "C:/Users/Justi/PycharmProjects/maze/duck_sounds"
GENERATION_THRESH=50
FPS = 26

# ********************************************************************

def create_random_moves(turns):
    options = MOVE_OPTIONS

    return random.choices(options, k=turns)


def calc_goal_distance(x1, y1, x2, y2, measure="manhattan"):
    if measure=="euclidean":
        goal_dist = sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

    elif measure=="manhattan":
        goal_dist = int(abs(abs(x2) - abs(x1))/PLAYER_SPEED + abs(abs(y2) - abs(y1))/PLAYER_SPEED)

    return goal_dist

def simple_crossover(arr1, arr2):
    cut_point = random.randrange(0, len(arr1)-1)
    if random.random() >= 0.05:
        new_arr = np.concatenate((arr1[:cut_point],  arr2[cut_point:]))
    else:
        new_arr = np.concatenate((arr2[:cut_point],  arr1[cut_point:]))

    return new_arr

def mutate(array, mutation_rate=MUTATION_RATE):

    if random.random() <= MUTATION_RATE:
        total = np.shape(array)[0] * np.shape(array)[1]

        # We will mutate a flat amount every time
        amount_to_mutate = int(total * mutation_rate)

        # Randomly select some places to mutate
        places = [random.randint(0, total-1) for i in range(amount_to_mutate)]

        for ele in places:
            row = ele//NUM_MOVES
            column = ele%NUM_MOVES
            current = array[row, column]
            array[row, column] = random.choice(MOVE_OPTIONS[MOVE_OPTIONS!=current])

        return array

    else:
        return array


def text_objects(text, font):
    textSurface = font.render(text, True, WHITE)
    return textSurface, textSurface.get_rect()

def calc_what_move(old_pos, new_pos):
    diff = [old_pos[i] - new_pos[i] for i in range(len(old_pos))]

    if diff[0] < 0:
        return "right"
    elif diff[0] > 0:
        return "left"
    elif diff[1] < 0:
        return "down"
    elif diff[1] > 0:
        return "up"
    elif diff[0] == 0 and diff[1] == 0:
        return
    else:
        print("MISTAKES WERE MADE! IDK WHAT'S GOING ON")
        print("old pos {}, new pos {}".format(old_pos, new_pos))

def message_display(text, surface, x, y):
    largeText = pygame.font.Font('freesansbold.ttf',TEXT_SIZE)
    TextSurf, TextRect = text_objects(text, largeText)

    TextRect.center = (x, y)
    surface.blit(TextSurf, TextRect)
    #pygame.display.update()

def create_moves_array(x = NUM_PLAYERS, y = NUM_MOVES):
    '''
    Creates an x by y array of player moves. Every row corresponds to a player and every column corresponds
    to a turn. The intersect is what the player should do on a given turn.
    :param x: Number of players
    :param y: Number of turns
    :return: x by y matrix of players and moves
    '''

    moves = []
    for i in range(x):
        moves.append(create_random_moves(y))

    moves = np.array(moves)

    return moves

class Player():
    # x = 46
    # y = 46
    speed = PLAYER_SPEED
    num_moves = NUM_MOVES

    def __init__(self, spawn_position):
        self.move_list = []
        self.fitness = 0
        self.id = None
        self.positions = []
        self.made_goal = 0
        self.spawn_position = spawn_position
        self.unique_positions = {self.spawn_position}
        self.x = spawn_position[0] + 2
        self.y = spawn_position[1] + 2


    def move(self, direction):
        if direction == "right":
            self.x = self.x + self.speed
        elif direction == "left":
            self.x = self.x - self.speed
        elif direction == "up":
            self.y = self.y - self.speed
        elif direction == "down":
            self.y = self.y + self.speed
        else:
            print("unknown move command")

    def check_move(self, move, known_walls_set):
        '''
        Checks to see if the move is ok, and if so, moves the player there. If the player already knows that such a move
        would result in hitting a wall, the function moves the player to a new spot that wouldn't hit a wall and
        returns this move
        '''

        if self.speed == 0:
            return

        # Right, Left, Up, Down
        if move == "right":
            new_coord = (self.x + self.speed, self.y)
        elif move == "left":
            new_coord = (self.x - self.speed, self.y)
        elif move == "up":
            new_coord = (self.x, self.y - self.speed)
        elif move == "down":
            new_coord = (self.x, self.y + self.speed)
        else:
            print(move)
            return

        possible_moves = [(self.x + self.speed, self.y), (self.x - self.speed, self.y),
                          (self.x, self.y-self.speed), (self.x, self.y+self.speed)]
        applicable_moves = [i for i in possible_moves if i not in known_walls_set]

        # If the move isn't going to push us into a wall and it isn't somewhere we have been already
        if new_coord in applicable_moves and new_coord not in self.positions:
            self.move(move)
            return

        # The move is either going to wall us, or it must be to somewhere we have been already
        else:
            # If this, then we are at a dead end
            if len(applicable_moves)==1:
                self.speed=0
                self.fitness += DEAD_END_PENALTY
                return

            # There are two non-wall moves, but we have been to the selected one already
            else:
                remainder = set(applicable_moves) - set(new_coord) - set(self.positions)
                remainder = [i for i in remainder]


                if len(remainder) > 1:
                    old_pos = [self.x, self.y]
                    new_coord = random.choice(remainder)
                    new_coord = [i for i in new_coord]
                    self.x = new_coord[0]
                    self.y = new_coord[1]
                    new_pos = [self.x, self.y]

                    what_move = calc_what_move(old_pos, new_pos)

                    return what_move

                elif len(remainder) == 0:
                    self.speed=0
                    return

                else:
                    # There's exactly one move that can be made
                    old_pos = [self.x, self.y]
                    new_coord = [i for i in remainder]
                    self.x = new_coord[0][0]
                    self.y = new_coord[0][1]
                    new_pos = [self.x, self.y]

                    what_move = calc_what_move(old_pos, new_pos)
                    return what_move

class App:

    window_width = WINDOW_X
    window_height = WINDOW_Y
    num_players = NUM_PLAYERS
    fps = FPS
    fitness_func = FIT_FUNC # distance Or unique
    generations = 1
    average_fitness = []
    best_fitness = []

    def __init__(self):
        self._running = True
        self._display_surf = None
        self._image_surf = None
        self._dead_surf = None
        self._block_surf = None

        self.maze = Maze()

        self.players = [Player(self.maze.spawn_pos) for i in range(self.num_players)]

        id = 0
        for player in self.players:
            player.id = id
            id+=1

        self.FPSclock = None
        self.bootup = True
        self.turn = 1
        self.num_moves = NUM_MOVES
        self.moves_array = create_moves_array()
        self.player_known_walls = set()
        self.made_it_proportion = 0

    def on_init(self):
        pygame.init()
        self._display_surf = pygame.display.set_mode((self.window_width, self.window_height))

        pygame.display.set_caption("Maze Game!")
        self._running = True
        self._image_surf = pygame.image.load("cartoon_duck_40x40.png").convert()
        self._dead_surf = pygame.image.load("dead_duck.png").convert()
        self._block_surf = pygame.image.load("lilly_pad_smol.png").convert()
        self._goal_surf = pygame.image.load("gun_small.png").convert()
        self.FPSclock = pygame.time.Clock()
        self.victory_quack = pygame.mixer.Sound("victory_ding.mp3")
        self.random_quacks = os.listdir(QUACKS_FILEPATH)

    def restart(self, moves_list):
        self.turn = 1
        self.generations += 1
        self.moves_array = np.array(moves_list)
        self.players = [Player(self.maze.spawn_pos) for i in range(self.num_players)]

        id = 0
        for player in self.players:
            player.id = id
            id+=1

        print("Game restarted, on to the next generation")

    def on_event(self, event):
        if event.type == QUIT:
            self._running = False

    def on_loop(self):
        for block_x, block_y in self.maze.collision_coords:
            for player in self.players:
                if self.is_collision(player.x, player.y, block_x, block_y,
                                     bsize=44):
                    # *** THINK OF SOMETHING BETTER ****
                    player.speed = 0
                    self.player_known_walls.add((player.x, player.y))

        for player in self.players:
            if self.is_collision(player.x, player.y, self.maze.goal[0], self.maze.goal[1],
                                 bsize=44):
                player.made_goal = 1
                player.speed = 0
                print("HOORAY!!! I DUCK HAS MADE IT!! WHAT A BLOODY RIPPA!")
                self.victory_quack.play()

    def on_render(self):
        self._display_surf.fill((0, 0, 0))
        for player in self.players:
            if player.speed > 0:
                self._display_surf.blit(self._image_surf, (player.x, player.y))
            elif player.speed == 0:
                self._dead_surf.blit(self._dead_surf, (player.x, player.y))

        try:
            message_display("FPS: {}  |  Generation {}  |  Best Fit {} | Prop Madeit {}".format(str(self.fps),
                                                                           str(self.generations),
                                                                           str(int(min(self.best_fitness))),
                                                                           self.made_it_proportion),
                            self._display_surf,
                            x=5.5 * TEXT_X, y=TEXT_Y)

        except:
            message_display("FPS: {}  |  Generation {}  |  Best Fit | Prop Madeit ".format(str(self.fps),
                                                                           str(self.generations)),
                            self._display_surf,
                            x=5.5 * TEXT_X, y=TEXT_Y)

        self.maze.draw(self._display_surf, self._block_surf, self._goal_surf)
        pygame.display.flip()

        if self.bootup:
            sleep(3)
            self.bootup = False

    def on_cleanup(self):
        pygame.display.quit()

        # Uncomment the following for plots

        # plt.subplot(1, 2, 1)
        # plt.plot([i for i in range(self.generations-1)], self.average_fitness)
        # plt.title("Average Fitness per Generation")
        # plt.xlabel("Generation")
        # plt.ylabel("Fitness, Distance to Target (lower is better)")
        #
        # plt.subplot(1, 2, 2)
        # plt.plot([i for i in range(self.generations-1)], self.best_fitness)
        # plt.title("Best Fitness per Generation")
        # plt.xlabel("Generation")
        # plt.ylabel("Fitness, Distance to Target (lower is better)")
        # plt.waitforbuttonpress()

    def is_collision(self, x1, y1, x2, y2, bsize):
        if x1 >=x2 and x1 <= x2 + bsize:
            if y1 >= y2 and y1 <= y2 + bsize:
                return True
        else:
            return False

    def calc_madeit_prop(self):
        madeit_sum = 0

        for player in self.players:
            if player.made_goal == 1:
                madeit_sum += 1

        return madeit_sum/NUM_PLAYERS

    def play_random_quack(self, likelihood = 0.0002):
        if random.random() <= likelihood:
            fp = QUACKS_FILEPATH + "/" + random.choice(self.random_quacks)
            pygame.mixer.music.load(fp)
            pygame.mixer.music.play()

    def on_execute(self):
        if self.on_init() == False:
            self._running = False

        while( self._running ):
            pygame.event.pump()
            keys = pygame.key.get_pressed()

            # CALC FITNESS *****************************************************
            # If we're on the final turn or all of the players have hit a wall
            if self.turn == self.num_moves or max(player.speed for player in self.players)==0:
                self.made_it_proportion = self.calc_madeit_prop()

                if self.made_it_proportion > MADEIT_THRESH:
                    print("{}% HAVE MADE IT, BLOODY WELL DONE LEGENDS".format(self.made_it_proportion*100))
                    self.on_cleanup()
                    break

                if self.generations == GENERATION_THRESH:
                    print("NO ONE MADE IT IN TIME!!!!!!!!!!!!!! NEW DUCKS PLZ")
                    self.on_cleanup()
                    break

                # Calculate the fitness
                if self.fitness_func == "distance":

                    for player in self.players:
                        player.fitness = calc_goal_distance(player.x, player.y,
                                                            self.maze.goal[0], self.maze.goal[1],
                                                            measure = "manhattan")
                        total_visited = len(player.positions)
                        unique_visited = len(set(player.positions))

                        num_backtracks = total_visited - unique_visited
                        player.fitness = player.fitness + (3*num_backtracks)

                    sum = 0
                    for player in self.players:
                        sum += player.fitness

                else:
                    for player in self.players:
                        player.fitness = len(player.unique_positions)

                        if player.speed==0 and player.made_goal == 0:
                            player.fitness = player.fitness + 20

                    sum = 0
                    for player in self.players:
                        sum += player.fitness

                self.average_fitness.append((sum/self.num_players))
                print("Average fitness of {}".format(sum/self.num_players))

                # ORDER BY FITNESS ****************************************************

                # Sort the players by their fitness
                if self.fitness_func == "distance":
                    self.players.sort(key=lambda x: x.fitness)
                    self.best_fitness.append(self.players[0].fitness)
                    print("Best fitness of {}".format(self.players[0].fitness))

                else:
                    self.players.sort(key=lambda x: x.fitness, reverse=True)
                    print("Best fitness of {}".format(self.players[0].fitness))

                # PERFORM CROSSOVER **************************************************
                moves_lists = []
                for j in range(int(len(self.players)*SELECTION_CUTOFF)):
                    if len(moves_lists) >= NUM_PLAYERS:
                        continue
                    if j == len(self.players):
                        continue

                    for k in range(j+1, len(self.players)):
                        if len(moves_lists) >= NUM_PLAYERS:
                            continue

                        better_moves = self.moves_array[self.players[j].id, ]
                        worse_moves = self.moves_array[self.players[k].id, ]
                        moves_lists.append(simple_crossover(better_moves, worse_moves))

                print("moves list is {} long".format(len(moves_lists)))

                moves_lists = np.array(moves_lists)

                moves_lists = mutate(moves_lists)

                self.restart(moves_list=moves_lists)

            # MOVE PLAYERS ***********************************************************************
            for player in self.players:
                # Uncomment if you want there to be quack sounds
                #self.play_random_quack()

                move = self.moves_array[player.id, self.turn-1]

                new_move = player.check_move(move, self.player_known_walls)

                if new_move:
                    self.moves_array[player.id, self.turn-1] = new_move

                player.positions.append((player.x, player.y))

                if FIT_FUNC == "unique":
                    player.unique_positions.add((player.x, player.y))


            if (keys[K_RIGHT]):
                self.fps += 2

            if (keys[K_LEFT]):
                self.fps -= 2

            if (keys[K_ESCAPE]):
                self.on_cleanup()
                break


            self.on_loop()
            self.on_render()
            self.FPSclock.tick(self.fps)
            self.turn +=1

        self.on_cleanup()

class Maze:
    def __init__(self):
        self.M = MAZE_WIDTH
        self.N = MAZE_HEIGHT

        # The test maze seen in the blog post
        # self.maze = [ 1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
        #               1,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,1,
        #               1,0,1,1,1,1,1,1,1,0,1,0,1,1,1,0,1,1,0,1,
        #               1,0,1,0,1,0,0,0,1,0,0,0,1,0,0,0,1,0,0,1,
        #               1,0,1,0,1,0,1,0,1,1,1,0,1,0,0,0,1,0,1,1,
        #               1,0,0,0,1,0,1,0,0,0,1,0,1,0,0,0,1,0,1,1,
        #               1,1,1,1,1,0,1,1,1,0,0,0,1,0,1,1,1,0,0,1,
        #               1,0,0,0,0,0,1,0,1,1,1,1,1,0,1,0,1,1,0,1,
        #               1,1,1,1,1,1,1,0,0,0,0,0,0,0,1,0,0,0,0,1,
        #               1,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,
        #               1,0,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,1,
        #               1,0,0,0,0,0,0,0,0,0,0,1,0,1,0,1,1,0,1,1,
        #               1,0,1,1,1,1,1,1,1,1,0,1,0,1,1,1,1,1,1,1,
        #               1,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,2,
        #               1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,]

        self.maze = create_maze.make_maze(self.M, self.N)

        self.collision_coords = []
        self.goal = None

        # Populate the collision coords
        bx = 0
        by = 0
        for i in range(0, self.M * self.N):
            if self.maze[ bx + (by*self.M) ] == 1:
                self.collision_coords.append((bx * 44, by * 44))

            elif self.maze[ bx + (by * self.M) ] == 2:
                  self.goal = ((bx * 44, by * 44))

            elif self.maze[ bx + (by * self.M) ] == 3:
                  self.spawn_pos = ((bx * 44, by * 44))

            bx += 1

            if bx > self.M-1:
                bx = 0
                by += 1

        self.collision_coords = np.array(self.collision_coords)

    def draw(self, display_surf, image_surf, goal_surf):
        bx = 0
        by = 0

        # This for loop looks along each row of the maze and determines if there is
        # a 1 or 0 at that place. If there is a one, it draws a square on the surface
        for i in range(0, self.M * self.N):
            if self.maze[ bx + (by*self.M) ] == 1:
                display_surf.blit(image_surf, (bx * 44, by * 44))

            if self.maze[bx + (by * self.M)] == 2:
                display_surf.blit(goal_surf, (bx * 44, by * 44))

            bx += 1

            if bx > self.M-1:
                bx = 0
                by += 1




while True:
    maze_game = App()
    maze_game.on_execute()






















