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
import assets
import enum

os.environ['SDL_VIDEO_CENTERED'] = '1'

WIDTH = 1000
HEIGHT = 600
TITLE="丁真大冒险"


class GameState(enum.Enum):
    MAIN_MEUE=enum.auto()
    GAME=enum.auto()

game_state=GameState.MAIN_MEUE

assets.screen_height=HEIGHT
assets.screen_width=WIDTH

keys_pressed=set()

mainActor=MainActor()
scene = Scene(WIDTH,HEIGHT,mainActor)
mainActor.scene=scene
loseActor=TextActor("你输了",30)
loseActor.color=(200,25,25)
loseActor.pos=(WIDTH/2,HEIGHT/2)
loseActor.visible=False

mainMenuActors=[]
title=TextActor("丁真大冒险",50)
title.pos=(WIDTH/2,HEIGHT/4)

tip=TextActor("按空格开始游戏",20)
tip.pos=(WIDTH/2,HEIGHT/4*3)

bg=EnhancedActor("bg")

mainMenuActors.append(bg)
mainMenuActors.append(title)
mainMenuActors.append(tip)

fontsizeEffect=FontSizeEffect(title,20,45,70)

def draw():
    screen.clear()
    if game_state==GameState.MAIN_MEUE:
        for actor in mainMenuActors:
            actor.draw()
        return
    scene.draw()
    effects_text=""
    for effect in effects:
        if effect.isShowUI:
            effects_text+=effect.get_str()+"\n"
    draw_text(effects_text,(0,HEIGHT/3))
    mainActor.draw()
    loseActor.draw()

clock = pygame.time.Clock()
def update():
    global clock,loseActor
    assets.elapsed_time_frame=clock.get_time()
    background.screen=screen
    utils.screen=screen
    if game_state==GameState.MAIN_MEUE:
        pass
    scene.tick()
    for a in gif_actors:
        a.update(clock.get_time()/1000)
    for effect in effects:
        effect.tick()
    for cd in cd_counter_list:
        cd.tick()
    mainActor.tick()
    if mainActor.isLosed:
        loseActor.visible=True
    else:
        moving=[0,0]
        if keys.RIGHT in keys_pressed:
            moving[0]=1
        if keys.LEFT in keys_pressed:
            moving[0]=-1
        if keys.UP in keys_pressed:
            moving[1]=-1
        if keys.DOWN in keys_pressed:
            moving[1]=1
        
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
        for attack in scene.self_misiles:
            if not attack.visible:
                    continue
            for enemy in scene.actors:
                attack.try_attack(enemy)
        for attack in scene.enemy_misiles:
            if not attack.visible:
                    continue
            attack.try_attack(mainActor)
    clock.tick(60)


def on_key_down(key):
    global game_state
    keys_pressed.add(key)
    if key==keys.SPACE:
        if game_state==GameState.MAIN_MEUE:
            fontsizeEffect.stop=True
            game_state=GameState.GAME
            return
    
    if key==keys.K_1:
        mainActor.attack()
    if key==keys.K_2:
        mainActor.use_big_reke()
    if key==keys.K_3:
        mainActor.use_reke_to_health()

def on_key_up(key):
    keys_pressed.remove(key)






pgzrun.go()
