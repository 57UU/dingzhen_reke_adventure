import pgzrun  # 导入游戏库
import pgzero.screen
import pgzero.keyboard
from pgzero.actor import Actor
import pygame
import random
import math
from background import *
import background
from utils import *
import utils
screen : pgzero.screen.Screen
keyboard: pgzero.keyboard.Keyboard  
import os
os.environ['SDL_VIDEO_CENTERED'] = '1'

WIDTH = 1000
HEIGHT = 600

background.screen_height=HEIGHT
background.screen_width=WIDTH

keys_pressed=set()

mainActor=MainActor()
scene = Scene(WIDTH,HEIGHT,mainActor)


def draw():
    screen.clear()
    scene.draw()
    mainActor.draw()

clock = pygame.time.Clock()
def update():
    global clock
    background.elapsed_time_frame=clock.get_time()
    
    background.screen=screen
    utils.screen=screen
    scene.tick()
    for a in gif_actors:
        a.update(clock.get_time()/1000)
    mainActor.tick()
    moving=[0,0]
    if keys.RIGHT in keys_pressed:
        moving[0]=1
    if keys.LEFT in keys_pressed:
        moving[0]=-1
    if keys.UP in keys_pressed:
        moving[1]=-1
    if keys.DOWN in keys_pressed:
        moving[1]=1
    if keys.F in keys_pressed:
        mainActor.attack()
    mainActor.handle_moving(*moving)

    mainActorPos=mainActor.get_position()
    if mainActorPos[0]>WIDTH*3/4:
        deltaX=mainActorPos[0]-WIDTH*3/4
        mainActor.set_position((mainActorPos[0]-deltaX,mainActorPos[1]))
        scene.delta_x(-deltaX)
    
    for element in scene.doors:
        if element.colliderect(mainActor.actor):
            element.attr.on_enter(mainActor)
    for element in scene.tools:
        element.invoke(mainActor)
    clock.tick(60)


def on_key_down(key):
    keys_pressed.add(key)

def on_key_up(key):
    keys_pressed.remove(key)






pgzrun.go()
