# -*- coding: utf-8 -*-
# This is my contribution for the GAME OFF 2018
# The theme is Hybrid
# My game is a Hybrid of a cave RPG, sort of rogue like and a match three game,
# where putting together three things of the same type gives you points or an
# upgrade.
# When judging please take into account that this is my first game, and my 
# first attempt to make such a big piece of code.
# I also did the graphics, by hand, with paint :D

# LIBRARIES
import sys
#import os
import pygame as pg
import random

# FREE CONSTANTS
BOX_EDGE = 50       # PLAYER AND BOX SQUARES; FUDAMENTAL UNIT
GRID_WIDTH  = 9    # PLAY GRID (ODD NUMBERS)
GRID_HEIGHT = 9
BORDER_GRID = 2
fps = 30
DELAY = 80
bkgd_color = (0, 0, 0)
internal_color = (180,180,180)
NEW_BOX_DELAY = [(20, 80), (40, 60),\
                 (60, 50), (80, 30),\
                 (100,20)] # SPEED BY SCORE LEVEL
NEW_BOX_PROBABILITY = [(100, 0, 0, 0, 0),\
                       (80, 100, 0, 0, 0),\
                       (60, 90, 100, 0, 0),\
                       (60, 85, 95, 100, 0),\
                       (50, 80, 95, 100, 0)]# PROBABILITIES OF TYPES OF BOX APPEARING


# DERIVED CONSTANTS
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
                        #(initial_player_position[0],\
                        # initial_player_position[1] - 3,),
                        #(initial_player_position[0] + 3,\
                        # initial_player_position[1] - 3),
                        #(initial_player_position[0] - 3,\
                        # initial_player_position[1] + 3),
                        #(initial_player_position[0] + 3,\
                        # initial_player_position[1] + 3),)
PLAYER_POSITIONS = [initial_player_position] # INITIAL PLAYER POSITION FOR EACH LEVEL
BOX_POSITIONS = [initial_box_position,]       # INITIAL BOXES POSITIONS FOR EACH LEVEL

class Level():
    
    def __init__(self,level):
        self.player = Player(PLAYER_POSITIONS[level - 1])
        self.boxes = []
        self.score = 0
        self.win = False
        self.lose = False
        self.current_speed = 0
        self.new_box_delay = 100
        for box in BOX_POSITIONS[level - 1]:
            self.boxes.append(Box(box))
        self.level_dict = {}
        self.update_dict()
    
    def remove_box(self, box):
        self.boxes.remove(box)
        
    
    def move_player(self, x, y):
        boxes = self.boxes
        player = self.player
        index_collision1 = -1
        has_moved = False
        for index, box in enumerate(boxes): # player collides with box
            if (box.x, box.y) == (player.x + x, player.y + y):
                index_collision1 = index
                break
        if index_collision1 >= 0:
            box = boxes[index_collision1]
            index_collision2 = -1
            for index, other_box in enumerate(boxes): # box collides with box or goes out
                if (box.x + x, box.y + y) == (other_box.x, other_box.y)\
                and index != index_collision1:
                    index_collision2 = index
                    break
            if  index_collision2 < 0\
            and box.x + x >= 0\
            and box.x + x < GRID_WIDTH\
            and box.y + y >= 0\
            and box.y + y < GRID_HEIGHT:
                player.move(x, y)
                box.move(x, y)
                has_moved = True
            else:
                if x == 1 and\
                self.check_line(player.x + 1, player.y): # player moves right and matches three
                    self.match_line(player.x + 1, player.y)
                elif x == -1 and\
                self.check_line(player.x - 3, player.y): # player moves left and matches three
                    self.match_line(player.x - 3, player.y)
                elif y == 1 and\
                self.check_vert(player.x, player.y + 1): # player moves down and matches three
                    self.match_vert(player.x, player.y + 1)
                elif y == -1 and\
                self.check_vert(player.x, player.y - 3): # player moves up and matches three
                    self.match_vert(player.x, player.y - 3)
                    
        else:
            player.move(x, y)
            has_moved = True
        #self.update_dict()
        return has_moved
	
    def you_win(self):
        self.win = True
    
    def game_over(self):
        self.lose = True
    
    def check_line(self, row, column):
        result = False
        all_kinds = ['B1', 'B2', 'B3', 'B4', 'B5']
        pos1 = self.level_dict.get((row, column))
        pos2 = self.level_dict.get((row + 1, column))
        pos3 = self.level_dict.get((row + 2, column))
        if pos1 in all_kinds and pos2 in all_kinds and pos3 in all_kinds:
            if pos1 == pos2 and pos2 == pos3:
                result = True
                return result
    
    def match_line(self, row, column):
        box_to_remove = []
        for box in self.boxes:
            if box.kind < 5:
                if box.x == row and box.y == column:
                    box_to_remove.append(box)
                elif box.x == row + 2 and box.y == column:
                    box_to_remove.append(box)
                elif box.x == row + 1 and box.y == column:
                    self.score += 2 ** box.kind
                    box.kind += 1
        for box in box_to_remove:
            self.remove_box(box)
        #self.update_dict()
    
    def check_vert(self, row, column):
        pass
        result = False
        all_kinds = ['B1', 'B2', 'B3', 'B4', 'B5']
        pos1 = self.level_dict.get((row, column))
        pos2 = self.level_dict.get((row, column + 1))
        pos3 = self.level_dict.get((row, column + 2))
        if pos1 in all_kinds and pos2 in all_kinds and pos3 in all_kinds:
            if pos1 == pos2 and pos2 == pos3:
                result = True
        return result
    
    def match_vert(self, row, column):
        box_to_remove = []
        for box in self.boxes:
            if box.kind < 5:
                if box.x == row and box.y == column:
                    box_to_remove.append(box)
                elif box.x == row and box.y == column + 2:
                    box_to_remove.append(box)
                elif box.x == row and box.y == column + 1:
                    self.score += 2 ** box.kind
                    box.kind += 1
        for box in box_to_remove:
            self.remove_box(box)
        #self.update_dict()
    
#    def check_cube(self, row, column):
#        pass
#        result = False
#        all_kinds = ['B1', 'B2', 'B3', 'B4', 'B5']
#        pos1 = self.level_dict.get((row, column))
#        pos2 = self.level_dict.get((row, column + 1))
#        pos3 = self.level_dict.get((row + 1, column))
#        pos4 = self.level_dict.get((row + 1, column + 1))
#        if pos1 in all_kinds and pos2 in all_kinds and pos3 and pos4 in all_kinds:
#            if pos1 == pos2 and pos2 == pos3 and pos3 == pos4:
#                result = True
#        return result
    
#    def match_cube(self, row, column):
#        box_to_remove = []
#        for box in self.boxes:
#            if box.x == row + 1 and box.y == column + 1:
#                box_to_remove.append(box)
#            elif box.x == row and box.y == column + 1:
#                box_to_remove.append(box)
#            elif box.x == row and box.y == column:
#                box.kind += 1
#            elif box.x == row + 1and box.y == column:
#                if self.level_dict.get((row, column))[1] != '4':
#                    box.kind += 1
#                else:
#                    box_to_remove.append(box)
#        for box in box_to_remove:
#            self.remove_box(box)
#        self.update_dict()
    
#    def check_match(self):
#        for row in range(GRID_HEIGHT):
#            for column in range(GRID_WIDTH):
#                #if row + 1 < GRID_HEIGHT:
#                    #if column + 1 < GRID_WIDTH:
#                    #    if self.check_cube(row, column):
#                    #        self.match_cube(row, column)
#                if row + 2 < GRID_HEIGHT:
#                    if self.check_line(row, column):
#                        self.match_line(row, column)
#                if column + 2 < GRID_WIDTH:
#                    if self.check_vert(row, column):
#                        self.match_vert(row, column)
    
    def update_dict(self):
        self.level_dict = {}
        self.level_dict[(self.player.x, self.player.y)] = "P"
        for box in self.boxes:
            self.level_dict[(box.x, box.y)] = "B" + str(box.kind)
        if self.score > NEW_BOX_DELAY[self.current_speed][0]\
        and self.current_speed < 4:
            self.current_speed += 1
            self.new_box_delay = NEW_BOX_DELAY[self.current_speed][1]
    
    def add_box(self):
        if len(self.level_dict) >= GRID_HEIGHT * GRID_WIDTH - 1 :
            self.game_over()
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
        #self.update_dict
    
class Box():
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
    def __init__(self, data):
        self.x = data[0]
        self.y = data[1]
        self.rectangle = pg.Rect(self.x * BOX_EDGE + BORDER_WIDTH,\
                                 self.y * BOX_EDGE + BORDER_WIDTH,\
                                 BOX_EDGE, BOX_EDGE)
    
    def move(self, x, y):
        self.x = self.x + x
        self.y = self.y + y
        self.x = max(self.x, 0)
        self.x = min(self.x, GRID_WIDTH - 1)
        self.y = max(self.y, 0)
        self.y = min(self.y, GRID_HEIGHT - 1)
        self.rectangle = pg.Rect(self.x * BOX_EDGE + BORDER_WIDTH,\
                                 self.y * BOX_EDGE + BORDER_WIDTH,\
                                 BOX_EDGE, BOX_EDGE)
    
class GameArea():
    def __init__(self):
        self.rectangle = pg.Rect(internal_rect)
        self.current_level = 1
        self.level = Level(self.current_level)
        
    def restart_level(self):
        self.level = Level(self.current_level)

class Screen():
    def __init__(self, length, height):
        self.surf = pg.display.set_mode((length, height), )
        self.height = height
        self.length = length
        self.area = GameArea()

class Application():
    def __init__(self):
        self.run = True
        self._image_library = {}
        self.clock = pg.time.Clock()
        self.timer_start = pg.time.get_ticks()
        self.temp_ticks = 0
        self.temp_seconds = 0
        self.ticks = pg.time.get_ticks()
        self.seconds = 0
        self.count = 0
        
        self.pause = False
        pg.display.set_caption("Maze Match")
        pg.display.set_icon(self.get_image('Maze.ico'))
        self.screen = Screen(SCREEN_LENGTH, SCREEN_HEIGHT)
    
    def ask_exit(self):
        self.screen.surf.fill((0,0,0))
        go_on = True
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
        image = self._image_library.get(path)
        if image == None:
            image = pg.image.load(path)
            self._image_library[path] = image
        return image
    
    def main(self):
        self.menu_sreen()
        while self.run:
            self.clock.tick(fps)
            self.update()
            self.draw()
            
    def menu_sreen():
        pass
    
    def draw(self):
        if not self.pause:
            self.screen.surf.fill((0,0,0))
            pg.draw.rect(self.screen.surf, internal_color, self.screen.area.rectangle)
            for i, box in enumerate(self.screen.area.level.boxes):
                self.screen.surf.blit(self.get_image('Box' + str(box.kind) + '.bmp'),\
                                      box.rectangle)
            self.screen.surf.blit(self.get_image('Player.bmp'), self.screen.area.level.player.rectangle)
            text = "Score: %d" % self.screen.area.level.score
            font = pg.font.Font(None, 30)
            fg = 250, 250, 250
            bg = 0, 0, 0
            ren = font.render(text, 0, fg, bg)
            self.screen.surf.blit(ren, (10, 10))
            text = "Timer: %2sm:%2ss" %((int(self.seconds)//60)%60,\
                                        int(self.seconds)%60)
            ren = font.render(text, 0, fg, bg)
            length, height = ren.get_size()
            self.screen.surf.blit(ren, (SCREEN_LENGTH - length - 10, 10))
        else:
            text = "PAUSED"
            font = pg.font.Font(None, 100)
            fg = 0, 0, 0
            ren = font.render(text, 0, fg)
            length, height = ren.get_size()
            self.screen.surf.blit(ren,\
                                  ((SCREEN_LENGTH - length)// 2,\
                                   (SCREEN_HEIGHT - height)// 2))
        
        pg.display.flip()
        
    def update(self):
        self.ticks = pg.time.get_ticks()
        self.seconds = (self.ticks - self.timer_start)/1000 - self.temp_seconds
        area = self.screen.area
        level = area.level
        for event in pg.event.get():
            if event.type == pg.QUIT\
            or (event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE):
                self.temp_ticks = self.ticks
                if self.ask_exit():
                    self.run = False
                else:
                    self.temp_seconds += (self.ticks - self.temp_ticks)/1000
            elif event.type == pg.KEYDOWN and event.key == pg.K_r: #RESTART
                self.timer = pg.time.get_ticks()
                area.restart_level()
            elif event.type == pg.KEYDOWN and event.key == pg.K_p: #PAUSE
                if self.pause:
                    self.temp_seconds += (self.ticks - self.temp_ticks)/1000
                else:
                    self.temp_ticks = self.ticks
                self.pause = not self.pause
                
            elif event.type == pg.KEYDOWN and event.key == pg.K_t: #NEXT CUBE
                level.add_box()
        
        if not self.pause:
            keys = pg.key.get_pressed()
            count_movements = 0
            
            if keys[pg.K_a] or keys[pg.K_LEFT]:  # to move left
                if level.move_player(-1, 0):
                    count_movements += 1
            if keys[pg.K_d] or keys[pg.K_RIGHT]: # to move right
                if level.move_player(1, 0):
                    count_movements += 1
            if keys[pg.K_w] or keys[pg.K_UP]: #to move up
                if level.move_player(0, -1):
                    count_movements += 1
            if keys[pg.K_s] or keys[pg.K_DOWN]: #to move down
                if level.move_player(0, 1):
                    count_movements += 1
            if count_movements >= 1:
                pg.time.delay(DELAY)
            
            #level.check_match()
            if self.count <= level.new_box_delay:
                self.count += 1
            else:
                self.count = 0
                level.add_box()
        
        level.update_dict()
        if level.win:
            self.run = False
        if level.lose:
            self.run = False
        
if __name__ == '__main__':
    pg.init()
    try:
        app = Application()
        app.main()
    except(Exception):
        print("Unhandled exception in file " + \
              str(sys.exc_info()[2].tb_frame.f_code.co_filename) + \
              " on line " + str(sys.exc_info()[2].tb_lineno) + ".\nGot a " + \
              str(sys.exc_info()[0]) + " while running.\nExplanation: " + \
              str(sys.exc_info()[1]) + "\nThe application will now quit.")
        pg.quit()
    pg.quit()
