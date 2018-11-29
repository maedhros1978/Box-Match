# -*- coding: utf-8 -*-
# This is my contribution for the GAME OFF 2018
# The theme was "Hybrid"
# My game is a Hybrid of a SOKOBAN like game, and a match three game, one of those
# where putting together three things of the same type gives you points and an
# upgraded thing.
# The "things" here are referred to as "boxes", and since I did the graphics they
# are represented by wonderful colored squares, with a black border.
# The top level box has a shape that vaguely reminds that of a companion cube
# because, why not? These boxes can be moved, but cannot be matched together
# (who wants to lose one of those?).
# Another square, with a smiley face on it, is the player.
# There are four different game modes:
# 1. Normal: It starts slowly, more boxes appear every few seconds. Put three
#    boxes of the same color close to each other and give them a little push to
#    match them, get points and a higher level box. When points grow, the game
#    gets faster and boxes appear quickly. The objective of this game mode is to
#    get as many points as possible. The game ends when the player cannot move
#    anymore.
# 2. Crazy: just like normal, but faster.
# 3. Peaceful: The pace of the game does not change. Objective: get as many
#    companion boxes as you can.
# 4. Race: make one companion box as fast as you can.
# 
# This is my first game, and my first attempt to make such a big piece of code.
# I hope you will enjoy it.

# LIBRARIES
import pygame as pg
import random
import sys
import pickle

# FREE CONSTANTS
BOX_EDGE = 50      # PLAYER AND BOX SQUARES; FUDAMENTAL UNIT OF DISTANCE
GRID_WIDTH  = 9    # PLAY GRID (BETTER USE ODD NUMBERS)
GRID_HEIGHT = 9
BORDER_GRID = 2    # BORDER AROUND THE GAME AREA
fps = 30           # FRAMERATE
DELAY = 80         # DELAY TO AVOID FAST MOVEMENT
internal_color = (180,180,180) # COLOR OF THE GAME AREA BACKGROUND
NEW_BOX_DELAY = [(20, 80), (40, 60),\
                 (60, 50), (80, 30),\
                 (100,20)] # SPEED BY SCORE LEVEL NORMAL
NEW_BOX_DELAY_CRAZY = [(10, 50), (20, 40),\
                       (40, 30), (50, 20),\
                       (80, 15)]# SPEED BY SCORE LEVEL CRAZY
NEW_BOX_DELAY_PEACE = [(0, 80), (0, 80),\
                       (0, 80), (0, 80),\
                       (0, 80)]# SPEED BY SCORE LEVEL PEACEFUL
NEW_BOX_DELAY_RACE = [(10000, 60), (0, 60),\
                      (0, 60), (0, 60),\
                      (0, 60)]# SPEED BY SCORE LEVEL RACE
NEW_BOX_PROBABILITY = [(100, 0, 0, 0, 0),\
                       (80, 100, 0, 0, 0),\
                       (60, 90, 100, 0, 0),\
                       (60, 85, 95, 100, 0),\
                       (50, 80, 95, 100, 0)] # PROBABILITIES OF APPEARANCE BY BOX TYPE

# OTHER CONSTANTS, OBTAINED FROM THE ABOVE
BORDER_WIDTH = BORDER_GRID * BOX_EDGE
SCREEN_LENGTH = BOX_EDGE * (GRID_WIDTH  + 2 * BORDER_GRID)
SCREEN_HEIGHT = BOX_EDGE * (GRID_HEIGHT + 2 * BORDER_GRID)
GAME_AREA_LENGTH = SCREEN_LENGTH - 2 * BORDER_WIDTH
GAME_AREA_HEIGHT = SCREEN_HEIGHT - 2 * BORDER_WIDTH

internal_rect = pg.Rect(BORDER_WIDTH, BORDER_WIDTH,\
                        GAME_AREA_LENGTH, GAME_AREA_HEIGHT) #GAME AREA
initial_player_position = (((GRID_WIDTH - 1)//2), ((GRID_HEIGHT - 1)//2))
initial_box_position = ((initial_player_position[0] - 3,\
                         initial_player_position[1]),
                        (initial_player_position[0] + 3,\
                         initial_player_position[1]),
                        (initial_player_position[0],\
                         initial_player_position[1] + 3),)

class Level():
    """Definition of the level class. It contains the positions of the boxes,
    of the player, the current score, and controls collisions. It also takes
    care of the matching and upgrading of boxes, and of the appearance of new
    boxes."""
    
    def __init__(self, kind=1):
        self.player = Player(initial_player_position)
        self.boxes = []
        self.score = 0
        self.win = False # FOR PEACEFUL MODE
        self.lose = False
        self.kind = kind
        if self.kind == 1:
            self.box_delay = NEW_BOX_DELAY
        elif self.kind == 2:
            self.box_delay = NEW_BOX_DELAY_CRAZY
        elif self.kind == 3:
            self.box_delay = NEW_BOX_DELAY_PEACE
        elif self.kind == 4:
            self.box_delay = NEW_BOX_DELAY_RACE
        self.current_speed = 0
        self.new_box_delay =  self.box_delay[0][1]
        for box in initial_box_position:
            self.boxes.append(Box(box))
        self.level_dict = {}
        self.companions = 0
        self.update_dict()
    
    def remove_box(self, box):
        "Just pops a box"
        self.boxes.remove(box)
    
    def move_player(self, x, y):
        "Player movements (and boxes, as a consequence)"
        boxes = self.boxes
        player = self.player
        index_collision1 = -1
        has_moved = False # FOR TAKING CARE OF MOVEMENT DELAY
        for index, box in enumerate(boxes): # CHECK COLLISION
            if (box.x, box.y) == (player.x + x, player.y + y):
                index_collision1 = index
                break
        if index_collision1 >= 0: # PLAYER COLLIDES WITH BOX
            box = boxes[index_collision1]
            index_collision2 = -1
            for index, other_box in enumerate(boxes): # CHECK COLLISION WITH SECOND BOX
                if (box.x + x, box.y + y) == (other_box.x, other_box.y)\
                and index != index_collision1:
                    index_collision2 = index
                    break
            if  index_collision2 < 0\
            and box.x + x >= 0\
            and box.x + x < GRID_WIDTH\
            and box.y + y >= 0\
            and box.y + y < GRID_HEIGHT: #PLAYER AND BOX MOVE
                player.move(x, y)
                box.move(x, y)
                has_moved = True
            else: # BOX COLLIDES WITH SECOND BOX OR GOES OUT
                if x == 1 and\
                self.check_line(player.x + 1, player.y): # PLAYER MOVES RIGHT AND MATCHES THREE
                    self.match_line(player.x + 1, player.y)
                elif x == -1 and\
                self.check_line(player.x - 3, player.y): # PLAYER MOVES LEFT AND MATCHES THREE
                    self.match_line(player.x - 3, player.y)
                elif y == 1 and\
                self.check_vert(player.x, player.y + 1): # PLAYER MOVES DOWN AND MATCHES THREE
                    self.match_vert(player.x, player.y + 1)
                elif y == -1 and\
                self.check_vert(player.x, player.y - 3): # PLAYER MOVES UP AND MATCHES THREE
                    self.match_vert(player.x, player.y - 3)
                    
        else: # PLAYER IS NOT TOUCHING ANYTHING, THEY JUST MOVE
            player.move(x, y)
            has_moved = True
        return has_moved
	
    def you_win(self):
        "In peaceful mode, you ot to the companion box"
        self.win = True
    
    def game_over(self):
        "Player can't move anymore"
        self.lose = True
    
    def check_line(self, row, column):
        """Checks if three boxes on the same line and on the same kind have to 
        be matched"""
        result = False
        all_kinds = ['B1', 'B2', 'B3', 'B4']
        pos1 = self.level_dict.get((row, column))
        pos2 = self.level_dict.get((row + 1, column))
        pos3 = self.level_dict.get((row + 2, column))
        if pos1 in all_kinds and pos2 in all_kinds and pos3 in all_kinds:
            if pos1 == pos2 and pos2 == pos3:
                result = True
                return result
    
    def match_line(self, row, column):
        "Removes two boxes in line and gives you a better one"
        box_to_remove = []
        for box in self.boxes:
            if box.x == row and box.y == column:
                box_to_remove.append(box)
            elif box.x == row + 2 and box.y == column:
                box_to_remove.append(box)
            elif box.x == row + 1 and box.y == column:
                self.score += 2 ** box.kind
                box.kind += 1
        for box in box_to_remove:
            self.remove_box(box)
    
    def check_vert(self, row, column):
        """Checks if three boxes on the same column and on the same kind have to 
        be matched"""
        result = False
        all_kinds = ['B1', 'B2', 'B3', 'B4']
        pos1 = self.level_dict.get((row, column))
        pos2 = self.level_dict.get((row, column + 1))
        pos3 = self.level_dict.get((row, column + 2))
        if pos1 in all_kinds and pos2 in all_kinds and pos3 in all_kinds:
            if pos1 == pos2 and pos2 == pos3:
                result = True
        return result
    
    def match_vert(self, row, column):
        "Removes two boxes in line, vertically, and gives you a better one"
        box_to_remove = []
        for box in self.boxes:
            if box.x == row and box.y == column:
                box_to_remove.append(box)
            elif box.x == row and box.y == column + 2:
                box_to_remove.append(box)
            elif box.x == row and box.y == column + 1:
                self.score += 2 ** box.kind
                box.kind += 1
        for box in box_to_remove:
            self.remove_box(box)

    def update_dict(self):
        """Resets and recreates the updated dictionary where the position of
        the player and the positions and kind of the boxes are stored. Also
        updates the speed delay"""
        self.level_dict = {}
        self.level_dict[(self.player.x, self.player.y)] = "P"
        for box in self.boxes:
            self.level_dict[(box.x, box.y)] = "B" + str(box.kind)
        if self.score > self.box_delay[self.current_speed][0]\
        and self.current_speed < 4:
            self.current_speed += 1
            self.new_box_delay = self.box_delay[self.current_speed][1]
        self.companions = len([v for v in self.level_dict.values() if v == "B5"])
        if self.kind == 4 and self.companions == 1:
            self.you_win()
    
    def add_box(self):
        """Add a random box in an empty positions, according to the weights given
        in NEW_BOX_PROBABILITY. The weights change with the speed"""
        if len(self.level_dict) >= GRID_HEIGHT * GRID_WIDTH - 1 :
            self.game_over() # Game area is full
        go_on = True
        this_kind = 1
        extraction = random.randint(1, 100)
        for index, weight in enumerate(NEW_BOX_PROBABILITY[self.current_speed]):
            if extraction <= weight:
                this_kind = index + 1
                break
        while go_on:
            x = random.randint(0, GRID_WIDTH - 1)
            y = random.randint(0, GRID_HEIGHT - 1)
            if self.level_dict.get((x, y)) == None:
                go_on = False
                self.boxes.append(Box((x, y), this_kind))
    
class Box():
    "A box has a position, a rect object, a kind, and a movement method"
    def __init__(self, data, kind=1):
        self.x = data[0]
        self.y = data[1]
        self.rectangle = pg.Rect(self.x * BOX_EDGE + BORDER_WIDTH,\
                                 self.y * BOX_EDGE + BORDER_WIDTH,\
                                 BOX_EDGE, BOX_EDGE)
        self.kind = kind
    
    def move(self, x, y):
        self.x = self.x + x
        self.y = self.y + y
        self.rectangle = pg.Rect(self.x * BOX_EDGE + BORDER_WIDTH,\
                                 self.y * BOX_EDGE + BORDER_WIDTH,\
                                 BOX_EDGE, BOX_EDGE)

class Player():
    "A player has a position, a rect object, and a movement method"
    def __init__(self, data):
        self.x = data[0]
        self.y = data[1]
        self.rectangle = pg.Rect(self.x * BOX_EDGE + BORDER_WIDTH,\
                                 self.y * BOX_EDGE + BORDER_WIDTH,\
                                 BOX_EDGE, BOX_EDGE)
    
    def move(self, x, y):
        self.x = self.x + x
        self.y = self.y + y
        self.x = max(self.x, 0) # DONT GO OUT
        self.x = min(self.x, GRID_WIDTH - 1)
        self.y = max(self.y, 0)
        self.y = min(self.y, GRID_HEIGHT - 1)
        self.rectangle = pg.Rect(self.x * BOX_EDGE + BORDER_WIDTH,\
                                 self.y * BOX_EDGE + BORDER_WIDTH,\
                                 BOX_EDGE, BOX_EDGE)
    
class GameArea():
    """The game area is a Rect, with a level object in it. It takes care of
    restarting the game"""
    def __init__(self):
        self.rectangle = pg.Rect(internal_rect)
        self.level = Level()
        
    def restart(self, kind):
        self.level = Level(kind)

class Screen():
    "The main surface where everything happens. It contains the game area object"
    def __init__(self, length, height):
        self.surf = pg.display.set_mode((length, height), )
        self.height = height
        self.length = length
        self.kind = 1
        self.area = GameArea()

class Application():
    """Main program, with menus, clocks, user input, and images. Its main
    method is the main loop of the program"""
    def __init__(self):
        self.run = True
        self.is_in_game = False
        self.image_library = {}
        self.clock = pg.time.Clock()
        self.timer_start = pg.time.get_ticks() # STORES THE STARING TIME
        self.ticks = pg.time.get_ticks()
        self.seconds = 0
        self.temp_ticks = 0 # USEFUL FOR PAUSE
        self.temp_seconds = 0
        self.count = 0 # COUNTER FOR BOX APPEARANCE
        self.pause = False
        pg.display.set_caption("Box Match")
        pg.display.set_icon(self.get_image('player.ico'))
        self.screen = Screen(SCREEN_LENGTH, SCREEN_HEIGHT)
        try:
            with open("Highscores.txt") as file:
                self.highscores = pickle.load(file)
        except EOFError:
            self.highscores = {1:[103,3,600], 2:[103,2,600], 3:[103,15,6000], 4:[103,1,600]}
    
    def reset_timer(self):
        self.timer_start = pg.time.get_ticks()
        self.ticks = pg.time.get_ticks()
        self.seconds = 0
        self.temp_ticks = 0
        self.temp_seconds = 0
        self.count = 0
    
    def ask_exit(self):
        "Asks if the user wants to quit"
        self.screen.surf.fill((0,0,0))
        go_on = True
        if self.is_in_game:
            text = "Quit to Menu (y/n)"
        else:
            text = "Really Quit (y/n)"
        font = pg.font.Font(None, 100)
        fg = 255, 0, 0
        ren = font.render(text, 0, fg)
        length, height = ren.get_size()
        self.screen.surf.blit(ren,\
                              ((SCREEN_LENGTH - length)// 2,\
                               (SCREEN_HEIGHT - height)// 2))
        pg.display.flip()
        while go_on:
            self.clock.tick(fps)
            self.ticks = pg.time.get_ticks()
            self.seconds = (self.ticks - self.timer_start)/1000 - self.temp_seconds
            for event in pg.event.get():
                if event.type == pg.KEYDOWN and event.key == pg.K_y:
                    return True
                elif event.type == pg.KEYDOWN and event.key == pg.K_n:
                    return False
    
    def get_image(self,path):
        "Adds image to the library"
        image = self.image_library.get(path)
        if image == None:
            image = pg.image.load(path)
            self.image_library[path] = image
        return image
    
    def main(self):
        "Main loop. Tick, update, draw"
        while self.run:
            self.clock.tick(fps)
            self.update()
            if self.run and self.is_in_game: self.draw()
    
    def write_menu(self):    
        self.screen.surf.fill((0,0,0))
        text = "Box Match"
        font = pg.font.Font(None, 100)
        fg = 255, 0, 0
        ren = font.render(text, 0, fg)
        length, height = ren.get_size()
        distance_so_far = 30 + height
        self.screen.surf.blit(ren,\
                              ((SCREEN_LENGTH - length)// 2,\
                               30))
        text = "1. Normal mode"
        font = pg.font.Font(None, 70)
        fg = 255, 0, 0
        ren = font.render(text, 0, fg)
        length, height = ren.get_size()
        distance_so_far += height + 30
        self.screen.surf.blit(ren,\
                              ((SCREEN_LENGTH - length)// 2,\
                               distance_so_far))
        text = "2. Crazy mode"
        font = pg.font.Font(None, 70)
        fg = 255, 0, 0
        ren = font.render(text, 0, fg)
        length, height = ren.get_size()
        distance_so_far += height + 30
        self.screen.surf.blit(ren,\
                              ((SCREEN_LENGTH - length)// 2,\
                               distance_so_far))
        text = "3. Peaceful mode"
        font = pg.font.Font(None, 70)
        fg = 255, 0, 0
        ren = font.render(text, 0, fg)
        length, height = ren.get_size()
        distance_so_far += height + 30
        self.screen.surf.blit(ren,\
                              ((SCREEN_LENGTH - length)// 2,\
                               distance_so_far))
        text = "4. Race mode"
        font = pg.font.Font(None, 70)
        fg = 255, 0, 0
        ren = font.render(text, 0, fg)
        length, height = ren.get_size()
        distance_so_far += height + 30
        self.screen.surf.blit(ren,\
                              ((SCREEN_LENGTH - length)// 2,\
                               distance_so_far))
        text = "5. Help"
        font = pg.font.Font(None, 70)
        fg = 255, 0, 0
        ren = font.render(text, 0, fg)
        length, height = ren.get_size()
        distance_so_far += height + 30
        self.screen.surf.blit(ren,\
                              ((SCREEN_LENGTH - length)// 2,\
                               distance_so_far))
        text = "ESC. Quit"
        font = pg.font.Font(None, 70)
        fg = 255, 0, 0
        ren = font.render(text, 0, fg)
        length, height = ren.get_size()
        distance_so_far += height + 30
        self.screen.surf.blit(ren,\
                              ((SCREEN_LENGTH - length)// 2,\
                               distance_so_far))
        pg.display.flip()
    
    def menu_sreen(self):
        "Asks the user which mode to start playing"
        go_on = True
        self.write_menu()
        area = self.screen.area
        while go_on:
            for event in pg.event.get():
                if event.type == pg.QUIT\
                or (event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE): # QUIT
                    if self.ask_exit():
                        self.run = False
                        self.screen.surf.fill((0,0,0))
                        pg.display.flip()
                        go_on = False
                    else:
                        self.write_menu()
                elif event.type == pg.KEYDOWN and event.key == pg.K_1:
                    go_on = False
                    self.reset_timer()
                    area.restart(1)
                    self.is_in_game = True
                elif event.type == pg.KEYDOWN and event.key == pg.K_2:
                    go_on = False
                    self.reset_timer()
                    area.restart(2)
                    self.is_in_game = True
                elif event.type == pg.KEYDOWN and event.key == pg.K_3:
                    go_on = False
                    self.reset_timer()
                    area.restart(3)
                    self.is_in_game = True
                elif event.type == pg.KEYDOWN and event.key == pg.K_4:
                    go_on = False
                    self.reset_timer()
                    area.restart(4)
                    self.is_in_game = True
                elif event.type == pg.KEYDOWN and event.key == pg.K_5:
                    self.write_help()
                    self.help_screen()
    
    def write_help(self):
        self.screen.surf.fill((0,0,0))
        text = "Help"
        font = pg.font.Font(None, 90)
        fg = 255, 0, 0
        ren = font.render(text, 0, fg)
        length, height = ren.get_size()
        distance_so_far = 30 + height
        self.screen.surf.blit(ren,\
                              ((SCREEN_LENGTH - length)// 2,\
                               30))
        text = "You control the player (the one with the face) with the arrows."
        font = pg.font.Font(None, 30)
        fg = 250, 250, 250
        ren = font.render(text, 0, fg)
        length, height = ren.get_size()
        distance_so_far += height + 30
        self.screen.surf.blit(ren, (10, distance_so_far))
        text = "You can push one box (the other squares), but not two boxes"
        font = pg.font.Font(None, 30)
        fg = 250, 250, 250
        ren = font.render(text, 0, fg)
        length, height = ren.get_size()
        distance_so_far += height + 15
        self.screen.surf.blit(ren, (10, distance_so_far))
        text = "together. When you put three boxes close to each other, and"
        font = pg.font.Font(None, 30)
        fg = 250, 250, 250
        ren = font.render(text, 0, fg)
        length, height = ren.get_size()
        distance_so_far += height + 15
        self.screen.surf.blit(ren, (10, distance_so_far))
        text = "give them another push, you get one upgraded box.There are 4"
        font = pg.font.Font(None, 30)
        fg = 250, 250, 250
        ren = font.render(text, 0, fg)
        length, height = ren.get_size()
        distance_so_far += height + 15
        self.screen.surf.blit(ren, (10, distance_so_far))
        text = "normal boxes (red, yellow, green, purple in this order), and one"
        font = pg.font.Font(None, 30)
        fg = 250, 250, 250
        ren = font.render(text, 0, fg)
        length, height = ren.get_size()
        distance_so_far += height + 15
        self.screen.surf.blit(ren, (10, distance_so_far))
        text = "special companion box (with a heart!). The companion"
        font = pg.font.Font(None, 30)
        fg = 250, 250, 250
        ren = font.render(text, 0, fg)
        length, height = ren.get_size()
        distance_so_far += height + 15
        self.screen.surf.blit(ren, (10, distance_so_far))
        text = "box cannot be matched. Every few seconds a new box appear."
        font = pg.font.Font(None, 30)
        fg = 250, 250, 250
        ren = font.render(text, 0, fg)
        length, height = ren.get_size()
        distance_so_far += height + 15
        self.screen.surf.blit(ren, (10, distance_so_far))
        text = "When the screen is filled the game is over."
        font = pg.font.Font(None, 30)
        fg = 250, 250, 250
        ren = font.render(text, 0, fg)
        length, height = ren.get_size()
        distance_so_far += height + 15
        self.screen.surf.blit(ren, (10, distance_so_far))
        text = "There are 4 game modes normal, crazy (just faster), peaceful"
        font = pg.font.Font(None, 30)
        fg = 250, 250, 250
        ren = font.render(text, 0, fg)
        length, height = ren.get_size()
        distance_so_far += height + 30
        self.screen.surf.blit(ren, (10, distance_so_far))
        text = "(the speed does not grow, so you can calmly make companions),"
        font = pg.font.Font(None, 30)
        fg = 250, 250, 250
        ren = font.render(text, 0, fg)
        length, height = ren.get_size()
        distance_so_far += height + 15
        self.screen.surf.blit(ren, (10, distance_so_far))
        text = "and race (just be quick to make a companion box)."
        font = pg.font.Font(None, 30)
        fg = 250, 250, 250
        ren = font.render(text, 0, fg)
        length, height = ren.get_size()
        distance_so_far += height + 15
        self.screen.surf.blit(ren, (10, distance_so_far))
        text = "That's it!"
        font = pg.font.Font(None, 70)
        fg = 250, 250, 250
        ren = font.render(text, 0, fg)
        length, height = ren.get_size()
        distance_so_far += height + 20
        self.screen.surf.blit(ren,\
                              ((SCREEN_LENGTH - length)// 2,\
                               distance_so_far))
        pg.display.flip()
    
    def help_screen(self):
        go_on = True
        while go_on:
            for event in pg.event.get():
                if event.type == pg.QUIT\
                or (event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE): # QUIT
                    if self.ask_exit():
                        self.run = False
                        self.screen.surf.fill((0,0,0))
                        pg.display.flip()
                        go_on = False
                    else:
                        self.write_menu()
                elif event.type == pg.KEYDOWN:
                    go_on = False
                    self.write_menu()
    
    def draw(self):
        "Draws the player and boxes and score and time on the screen surface"
        if not self.pause:
            self.screen.surf.fill((0,0,0))
            level = self.screen.area.level
            pg.draw.rect(self.screen.surf, internal_color, self.screen.area.rectangle)
            for i, box in enumerate(level.boxes):
                self.screen.surf.blit(self.get_image('Box' + str(box.kind) + '.bmp'),\
                                      box.rectangle)
            self.screen.surf.blit(self.get_image('Player.bmp'), level.player.rectangle)
            text = "Score: %d" % level.score
            font = pg.font.Font(None, 30)
            fg = 250, 250, 250
            bg = 0, 0, 0
            ren = font.render(text, 0, fg, bg)
            self.screen.surf.blit(ren, (10, 10))
            text = "Companions: %d" % level.companions
            font = pg.font.Font(None, 30)
            fg = 250, 250, 250
            bg = 0, 0, 0
            length, height = ren.get_size()
            ren = font.render(text, 0, fg, bg)
            self.screen.surf.blit(ren, ((SCREEN_LENGTH - length)//2, 10))
            text = "Time: %2sm:%2ss" %((int(self.seconds)//60)%60,\
                                        int(self.seconds)%60)
            ren = font.render(text, 0, fg, bg)
            length, height = ren.get_size()
            self.screen.surf.blit(ren, (SCREEN_LENGTH - length - 10, 10))
            text = "Highscore: %d" % self.highscores[level.kind][0]
            font = pg.font.Font(None, 30)
            fg = 250, 250, 250
            bg = 0, 0, 0
            ren = font.render(text, 0, fg, bg)
            length, height = ren.get_size()
            self.screen.surf.blit(ren, (10, SCREEN_HEIGHT - 10 - height))
            text = "Companions: %d" % self.highscores[level.kind][1]
            font = pg.font.Font(None, 30)
            fg = 250, 250, 250
            bg = 0, 0, 0
            length, height = ren.get_size()
            ren = font.render(text, 0, fg, bg)
            self.screen.surf.blit(ren, ((SCREEN_LENGTH - length)//2,\
                                        SCREEN_HEIGHT - 10 - height))
            text = "Time: %2sm:%2ss" %((int(self.highscores[level.kind][2])//60)%60,\
                                        int(self.highscores[level.kind][2])%60)
            ren = font.render(text, 0, fg, bg)
            length, height = ren.get_size()
            self.screen.surf.blit(ren, (SCREEN_LENGTH - length - 10,\
                                        SCREEN_HEIGHT - 10 - height))
        else:
            text = "PAUSED"
            font = pg.font.Font(None, 150)
            fg = 0, 0, 0
            ren = font.render(text, 0, fg)
            length, height = ren.get_size()
            self.screen.surf.blit(ren,\
                                  ((SCREEN_LENGTH - length)// 2,\
                                   (SCREEN_HEIGHT - height)// 2))
        
        pg.display.flip()
        
    def update(self):
        "User input and its consequences"
        if not self.is_in_game:
            self.menu_sreen()
        self.ticks = pg.time.get_ticks()
        self.seconds = (self.ticks - self.timer_start)/1000 - self.temp_seconds
        area = self.screen.area
        level = area.level
        for event in pg.event.get():
            if event.type == pg.QUIT\
            or (event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE): # QUIT
                self.temp_ticks = self.ticks
                if self.ask_exit():
                    self.is_in_game = False
                    self.screen.surf.fill((0,0,0))
                    pg.display.flip()
                else:
                    self.temp_seconds += (self.ticks - self.temp_ticks)/1000
            elif event.type == pg.KEYDOWN and event.key == pg.K_r: #RESTART
                self.timer = pg.time.get_ticks()
                area.restart()
            elif event.type == pg.KEYDOWN and event.key == pg.K_p: #PAUSE
                if self.pause:
                    self.temp_seconds += (self.ticks - self.temp_ticks)/1000
                else:
                    self.temp_ticks = self.ticks
                self.pause = not self.pause
                
            elif event.type == pg.KEYDOWN and event.key == pg.K_t: #NEXT BOX
                level.add_box()
                self.count = 0
                self.screen.area.level.score += 2
        
        if not self.pause:
            keys = pg.key.get_pressed()
            count_movements = 0
            
            if keys[pg.K_a] or keys[pg.K_LEFT]: 
                if level.move_player(-1, 0):
                    count_movements += 1
            if keys[pg.K_d] or keys[pg.K_RIGHT]:
                if level.move_player(1, 0):
                    count_movements += 1
            if keys[pg.K_w] or keys[pg.K_UP]:
                if level.move_player(0, -1):
                    count_movements += 1
            if keys[pg.K_s] or keys[pg.K_DOWN]:
                if level.move_player(0, 1):
                    count_movements += 1
            if count_movements >= 1:
                pg.time.delay(DELAY)
            
            if self.count <= level.new_box_delay:
                self.count += 1
            else:
                self.count = 0
                level.add_box()
        
        level.update_dict()
        
        if level.lose or level.win:
            self.is_in_game = False
            level.lose = False
            level.win = False
            go_on = True
            self.clock.tick(fps)
            self.screen.surf.fill((0,0,0))
            text = "Box Match"
            font = pg.font.Font(None, 100)
            fg = 255, 0, 0
            ren = font.render(text, 0, fg)
            length, height = ren.get_size()
            distance_so_far = 30 + height
            self.screen.surf.blit(ren,\
                                  ((SCREEN_LENGTH - length)// 2,\
                                   30))
            text = "GAME OVER"
            font = pg.font.Font(None, 100)
            fg = 255, 0, 0
            ren = font.render(text, 0, fg)
            length, height = ren.get_size()
            distance_so_far += height + 60
            self.screen.surf.blit(ren,\
                                  ((SCREEN_LENGTH - length)// 2,\
                                   distance_so_far))
            text = "Score: %d" % self.screen.area.level.score
            font = pg.font.Font(None, 40)
            fg = 255, 0, 0
            ren = font.render(text, 0, fg,)
            length, height = ren.get_size()
            distance_so_far += height + 50
            self.screen.surf.blit(ren,\
                                  ((SCREEN_LENGTH - length)// 2,\
                                   distance_so_far))
            text = "Companions: %d" % self.screen.area.level.companions
            font = pg.font.Font(None, 40)
            fg = 255, 0, 0
            ren = font.render(text, 0, fg,)
            length, height = ren.get_size()
            distance_so_far += height + 30
            self.screen.surf.blit(ren,\
                                  ((SCREEN_LENGTH - length)// 2,\
                                   distance_so_far))
            text = "Time: %2sm:%2ss" %((int(self.seconds)//60)%60,\
                                        int(self.seconds)%60)
            font = pg.font.Font(None, 40)
            fg = 255, 0, 0
            ren = font.render(text, 0, fg, )
            length, height = ren.get_size()
            distance_so_far += height + 30
            self.screen.surf.blit(ren,\
                                  ((SCREEN_LENGTH - length)// 2,\
                                   distance_so_far))
            pg.display.flip()
            with open("Highscores.txt", 'w') as file:
                if level.score > self.highscores[level.kind][0]:
                    self.highscores[level.kind][0] = level.score
                if level.companions > self.highscores[level.kind][1]:
                    self.highscores[level.kind][1] = level.companions
                if self.seconds < self.highscores[level.kind][2]:
                    self.highscores[level.kind][2] = self.seconds
                pickle.dump(self.highscores, file)
            area.restart(1)
            while go_on:
                for event in pg.event.get():
                    if event.type == pg.QUIT:
                        if self.ask_exit():
                            self.run = False
                            go_on = False
                    elif event.type == pg.KEYDOWN:
                        go_on = False
        
if __name__ == '__main__':
    "Start application object and handles quitting"
    pg.init()
    app = Application()
    try:
        app.main() # CATCH EXEPTIONS AND PRINT SOME INFO, USEFUL DURING DEBUG
    except Exception:
        print("Unhandled exception in file " + \
              str(sys.exc_info()[2].tb_frame.f_code.co_filename) + \
              " on line " + str(sys.exc_info()[2].tb_lineno) + ".\nGot a " + \
              str(sys.exc_info()[0]) + " while running.\nExplanation: " + \
              str(sys.exc_info()[1]) + "\nThe application will now quit.")
    pg.quit()