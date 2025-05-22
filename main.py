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
screen : pgzero.screen.Screen
keyboard: pgzero.keyboard.Keyboard  

WIDTH = 800
HEIGHT = 600

scene = Scene(WIDTH,HEIGHT)
keys_pressed=set()

mainActor=MainActor()
mainActor.set_position((WIDTH/2,HEIGHT/4))
mainActor.setValue(1)
print(mainActor.getValue())
actor_speed=20
def draw():
    background.screen=screen
    screen.clear()
    scene.draw()
    mainActor.draw()

clock = pygame.time.Clock()
def update():
    global clock
    scene.tick()
    mainActor.tick()
    for actor in mainActor.actors:
        for door in scene.elements:
            door.door.invoke(actor)
    if keys.RIGHT in keys_pressed:
        mainActor.delta_pos((actor_speed,0))
    if keys.LEFT in keys_pressed:
        mainActor.delta_pos((-actor_speed,0))
    if keys.UP in keys_pressed:
        mainActor.delta_pos((0,-actor_speed))
    if keys.DOWN in keys_pressed:
        # mainActor.delta_pos((0,actor_speed))
        pass
    clock.tick(60)


def on_key_down(key):
    keys_pressed.add(key)

def on_key_up(key):
    keys_pressed.remove(key)






pgzrun.go()
