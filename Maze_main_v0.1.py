# -*- coding: utf-8 -*-
"""
My first attempt

This is the main file of my first attempt at building a game with pygame
"""
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
fps = 10
bkgd_color = (0, 0, 0)
internal_color = (100,100,100)

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

EMPTY_LEVEL = {}
for row in range(21):
    for column in range(31):
        EMPTY_LEVEL[row, column] = None

LEVEL1 = EMPTY_LEVEL.copy()

# GLOBALS
global run
global _image_library
global player
global boxes
global LEVEL
global clock

run = True
_image_library = {}
player = pg.Rect(initial_player_position) #PLAYER
boxes = []
for position in initial_box_position:
    boxes.append(pg.Rect(position)) #BOX
LEVEL = 1 #LEVEL
clock = pg.time.Clock()

def ask_exit():
    return True

def get_image(path):
    global _image_library
    image = _image_library.get(path)
    if image == None:
        image = pg.image.load(path)
        _image_library[path] = image
    return image

def draw(screen): # APPLICATION
    pg.draw.rect(screen, internal_color, internal_rect)
    for i, box in enumerate(boxes):
        screen.blit(get_image('Box.bmp'), box)
    screen.blit(get_image('Player.bmp'), player)
    pg.display.flip()

def restart_level(level): # GAME AREA
    if level == 1:
        player = pg.Rect(initial_player_position)
        boxes = []
        for position in initial_box_position:
            boxes.append(pg.Rect(position))
    return boxes, player

def update(): # APPLICATION
    global run
    global player
    global boxes
    for event in pg.event.get():
        if event.type == pg.QUIT:
            if ask_exit(): run = False
        elif event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
            if ask_exit(): run = False
        elif event.type == pg.KEYDOWN and event.key == pg.K_r:
             boxes, player = restart_level(LEVEL)
    
    keys = pg.key.get_pressed()
    
    if keys[pg.K_a] or keys[pg.K_LEFT]:  # to move left
        player.move_ip(-1 * velocity,0 * velocity)
        index_collision1 = -1
        for index, box in enumerate(boxes): # player collides with box
            if box == player:
                index_collision1 = index
                break
        if index_collision1 >= 0:
            box = boxes[index_collision1]
            box.move_ip(-1 * velocity,0 * velocity)
            index_collision2 = -1
            for index, other_box in enumerate(boxes): # box collides with box or goes out
                if box == other_box and index != index_collision1:
                    index_collision2 = index
                    break
            if index_collision2 >= 0 or box.x < BORDER_WIDTH:
                box.move_ip(1 * velocity,0 * velocity)
                player.move_ip(1 * velocity,0 * velocity)
        else:
            player.clamp_ip(internal_rect) # player cannot exit screen
    if keys[pg.K_d] or keys[pg.K_RIGHT]: # to move right
        player.move_ip(1 * velocity,0 * velocity)
        index_collision1 = -1
        for index, box in enumerate(boxes): # player collides with box
            if box == player:
                index_collision1 = index
                break
        if index_collision1 >= 0:
            box = boxes[index_collision1]
            box.move_ip(1 * velocity,0 * velocity)
            index_collision2 = -1
            for index, other_box in enumerate(boxes): # box collides with box or goes out
                if box == other_box and index != index_collision1:
                    index_collision2 = index
                    break
            if index_collision2 >= 0 or box.x > GAME_AREA_LENGTH + BORDER_WIDTH - BOX_EDGE:
                box.move_ip(-1 * velocity,0 * velocity)
                player.move_ip(-1 * velocity,0 * velocity)
        else:
            player.clamp_ip(internal_rect) # player cannot exit screen
    if keys[pg.K_w] or keys[pg.K_UP]: #to move up
        player.move_ip(0 * velocity,-1 * velocity)
        index_collision1 = -1
        for index, box in enumerate(boxes): # player collides with box
            if box == player:
                index_collision1 = index
                break
        if index_collision1 >= 0:
            box = boxes[index_collision1]
            box.move_ip(0 * velocity,-1 * velocity)
            index_collision2 = -1
            for index, other_box in enumerate(boxes): # box collides with box or goes out
                if box == other_box and index != index_collision1:
                    index_collision2 = index
                    break
            if index_collision2 >= 0 or box.y < BORDER_WIDTH:
                box.move_ip(0 * velocity,1 * velocity)
                player.move_ip(0 * velocity,1 * velocity)
        else:
            player.clamp_ip(internal_rect) # player cannot exit screen
    if keys[pg.K_s] or keys[pg.K_DOWN]: #to move down
        player.move_ip(0 * velocity,1 * velocity)
        index_collision1 = -1
        for index, box in enumerate(boxes): # player collides with box
            if box == player:
                index_collision1 = index
                break
        if index_collision1 >= 0:
            box = boxes[index_collision1]
            box.move_ip(0 * velocity,1 * velocity)
            index_collision2 = -1
            for index, other_box in enumerate(boxes): # box collides with box or goes out
                if box == other_box and index != index_collision1:
                    index_collision2 = index
                    break
            if index_collision2 >= 0 or box.y > GAME_AREA_HEIGHT + BORDER_WIDTH - BOX_EDGE:
                box.move_ip(0 * velocity,-1 * velocity)
                player.move_ip(0 * velocity,-1 * velocity)
        else:
            player.clamp_ip(internal_rect) # player cannot exit screen
    if keys[pg.K_t]:
        raise Exception('Exception raised by user')

def main(): # APPLICATION
    try:
        pg.display.set_caption("Maze Match")
        pg.display.set_icon(get_image('Player.bmp'))
        screen = pg.display.set_mode((SCREEN_LENGTH, SCREEN_HEIGHT), )
        while run:
            clock.tick(fps)
            update()
            draw(screen)
    except(Exception):
        print("Unhandled exception in file " + \
              str(sys.exc_info()[2].tb_frame.f_code.co_filename) + \
              " on line " + str(sys.exc_info()[2].tb_lineno) + ".\nGot a " + \
              str(sys.exc_info()[0]) + " while running.\nExplanation: " + \
              str(sys.exc_info()[1]) + "\nThe application will now quit.")
        pg.quit()

if __name__ == '__main__':
    pg.init()
    main()
    pg.quit()
