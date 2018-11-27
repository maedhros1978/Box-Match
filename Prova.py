# -*- coding: utf-8 -*-

# LIBRARIES
import sys
#import os
import pygame as pg

# FREE CONSTANTS
BOX_EDGE = 20       # PLAYER AND BOX SQUARES; FUDAMENTAL UNIT
GRID_WIDTH  = 31    # PLAY GRID (ODD NUMBERS)
GRID_HEIGHT = 21
BORDER_GRID = 2
BOX_COLOR = (200,100,200)
fps = 30
DELAY = 80
bkgd_color = (0, 0, 0)
internal_color = (180,180,180)
GOAL_SCORE = [100]    # SCORE GOALS FOR EACH LEVEL

# DERIVED CONSTANTS
BORDER_WIDTH = BORDER_GRID * BOX_EDGE
SCREEN_LENGTH = BOX_EDGE * (GRID_WIDTH  + 2 * BORDER_GRID)
SCREEN_HEIGHT = BOX_EDGE * (GRID_HEIGHT + 2 * BORDER_GRID)
GAME_AREA_LENGTH = SCREEN_LENGTH - 2 * BORDER_WIDTH
GAME_AREA_HEIGHT = SCREEN_HEIGHT - 2 * BORDER_WIDTH
velocity = BOX_EDGE

internal_rect = pg.Rect(BORDER_WIDTH,BORDER_WIDTH,\
                        GAME_AREA_LENGTH, GAME_AREA_HEIGHT) #GAME AREA
initial_player_position = (((GRID_WIDTH - 1)//2 + BORDER_GRID) * BOX_EDGE,\
                           ((GRID_HEIGHT - 1)//2 + BORDER_GRID) * BOX_EDGE,\
                           BOX_EDGE, BOX_EDGE) #LEVEL
initial_box_position = ((initial_player_position[0] - 3 * velocity,\
                         initial_player_position[1], BOX_EDGE, BOX_EDGE),
                        (initial_player_position[0] + 3 * velocity,\
                         initial_player_position[1], BOX_EDGE, BOX_EDGE)) #LEVEL
PLAYER_POSITIONS = [initial_player_position] # INITIAL PLAYER POSITION FOR EACH LEVEL
BOX_POSITIONS = [initial_box_position,]       # INITIAL BOXES POSITIONS FOR EACH LEVEL

class Level():
    def __init__(self,level):
        self.player = Player(initial_player_position)
        self.boxes = []
        for box in initial_box_position:
            self.boxes.append(Box(box))
        self.level = 1
            
    def update(self):
        self.level += 1
        self.goal_score = GOAL_SCORE[self.level - 1]
        self.player.position = PLAYER_POSITIONS[self.level - 1]
        self.boxes.all_boxes.positions = BOX_POSITIONS[self.leve - 1]
    
    def reset(self):
        self.player = Player(PLAYER_POSITIONS[self.level - 1])
        self.boxes = []
        for i in range(len(BOX_POSITIONS[self.level - 1])):
            self.boxes.append(Box(BOX_POSITIONS[self.level - 1][i]))

class Box():
    def __init__(self,rectangle):
        self.rectangle = pg.Rect(rectangle)
        self.x = rectangle[0]
        self.y = rectangle[1]
    
    def move(self, x, y):
        self.x = self.x + x
        self.y = self.y + y
        self.rectangle = pg.Rect(self.x,self.y,self.rectangle[2],self.rectangle[3])

class Player():
    def __init__(self,rectangle):
        self.rectangle = pg.Rect(rectangle)
        self.x = rectangle[0]
        self.y = rectangle[1]
    
    def move(self, x, y):
        self.x = self.x + x
        self.y = self.y + y
        self.rectangle = pg.Rect(self.x,self.y,self.rectangle[2],self.rectangle[3])
        
    def clamp(self, rectangle):
        self.rectangle.clamp_ip(rectangle)

class GameArea():
    def __init__(self):
        self.rectangle = pg.Rect(internal_rect)
        self.level = Level(1)
    
    def restart_level(self):
        pass
        self.level.reset()

class Screen():
    def __init__(self, length, height):
        self.surf = pg.display.set_mode((length, height), )
        self.height = height
        self.length = length
        #self.goal = Goal()
        #self.score = Score()
        self.area = GameArea()

class Application():
    def __init__(self):
        self.run = True
        self._image_library = {}
        self.clock = pg.time.Clock()
        pg.display.set_caption("Maze Match")
        pg.display.set_icon(self.get_image('Player.bmp'))
        self.screen = Screen(SCREEN_LENGTH, SCREEN_HEIGHT)
    
    def ask_exit(self):
        return True
    
    def get_image(self,path):
        image = self._image_library.get(path)
        if image == None:
            image = pg.image.load(path)
            self._image_library[path] = image
        return image
    
    def main(self):
        while self.run:
            self.clock.tick(fps)
            self.update()
            self.draw()

    def draw(self):
        pg.draw.rect(self.screen.surf, internal_color, self.screen.area.rectangle)
        for i, box in enumerate(self.screen.area.level.boxes):
            self.screen.surf.blit(self.get_image('Box.bmp'), box.rectangle)
        self.screen.surf.blit(self.get_image('Player.bmp'), self.screen.area.level.player.rectangle)
        pg.display.flip()
        
    def update(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                if self.ask_exit(): self.run = False
            elif event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                if self.ask_exit(): self.run = False
            elif event.type == pg.KEYDOWN and event.key == pg.K_r:
                 self.screen.area.restart_level()
            elif event.type == pg.KEYDOWN and event.key == pg.K_t:
                raise Exception('Exception raised by user')
        
        keys = pg.key.get_pressed()
        
        player = self.screen.area.level.player
        boxes = self.screen.area.level.boxes
        
        if keys[pg.K_a] or keys[pg.K_LEFT]:  # to move left
            player.move(-1 * velocity,0 * velocity)
            index_collision1 = -1
            for index, box in enumerate(boxes): # player collides with box
                if box == player:
                    index_collision1 = index
                    break
            if index_collision1 >= 0:
                box = boxes[index_collision1]
                box.move(-1 * velocity,0 * velocity)
                index_collision2 = -1
                for index, other_box in enumerate(boxes): # box collides with box or goes out
                    if box == other_box and index != index_collision1:
                        index_collision2 = index
                        break
                if index_collision2 >= 0 or box.x < BORDER_WIDTH:
                    box.move(1 * velocity,0 * velocity)
                    player.move(1 * velocity,0 * velocity)
            else:
                player.clamp(internal_rect) # player cannot exit screen
            pg.time.delay(DELAY)
        if keys[pg.K_d] or keys[pg.K_RIGHT]: # to move right
            player.move(1 * velocity,0 * velocity)
            index_collision1 = -1
            for index, box in enumerate(boxes): # player collides with box
                if box == player:
                    index_collision1 = index
                    break
            if index_collision1 >= 0:
                box = boxes[index_collision1]
                box.move(1 * velocity,0 * velocity)
                index_collision2 = -1
                for index, other_box in enumerate(boxes): # box collides with box or goes out
                    if box == other_box and index != index_collision1:
                        index_collision2 = index
                        break
                if index_collision2 >= 0 or box.x > GAME_AREA_LENGTH + BORDER_WIDTH - BOX_EDGE:
                    box.move(-1 * velocity,0 * velocity)
                    player.move(-1 * velocity,0 * velocity)
            else:
                player.clamp(internal_rect) # player cannot exit screen
            pg.time.delay(DELAY)
        if keys[pg.K_w] or keys[pg.K_UP]: #to move up
            player.move(0 * velocity,-1 * velocity)
            index_collision1 = -1
            for index, box in enumerate(boxes): # player collides with box
                if box == player:
                    index_collision1 = index
                    break
            if index_collision1 >= 0:
                box = boxes[index_collision1]
                box.move(0 * velocity,-1 * velocity)
                index_collision2 = -1
                for index, other_box in enumerate(boxes): # box collides with box or goes out
                    if box == other_box and index != index_collision1:
                        index_collision2 = index
                        break
                if index_collision2 >= 0 or box.y < BORDER_WIDTH:
                    box.move(0 * velocity,1 * velocity)
                    player.move(0 * velocity,1 * velocity)
            else:
                player.clamp(internal_rect) # player cannot exit screen
            pg.time.delay(DELAY)
        if keys[pg.K_s] or keys[pg.K_DOWN]: #to move down
            player.move(0 * velocity,1 * velocity)
            index_collision1 = -1
            for index, box in enumerate(boxes): # player collides with box
                if box == player:
                    index_collision1 = index
                    break
            if index_collision1 >= 0:
                box = boxes[index_collision1]
                box.move(0 * velocity,1 * velocity)
                index_collision2 = -1
                for index, other_box in enumerate(boxes): # box collides with box or goes out
                    if box == other_box and index != index_collision1:
                        index_collision2 = index
                        break
                if index_collision2 >= 0 or box.y > GAME_AREA_HEIGHT + BORDER_WIDTH - BOX_EDGE:
                    box.move(0 * velocity,-1 * velocity)
                    player.move(0 * velocity,-1 * velocity)
            else:
                player.clamp(internal_rect) # player cannot exit screen
            pg.time.delay(DELAY)

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
