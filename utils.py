from typing_extensions import ParamSpecArgs
import pygame
import os
import pgzero
from pgzero.actor import Actor
import math
from pgzero.rect import Rect,ZRect
import random
from assets import *
import assets
import mapping

screen : pgzero.screen.Screen

text_color=(0, 25, 184)

placeholder_image=pygame.Surface((1,1))

class EnhancedActor(Actor):
    def __init__(self,*args, **kwargs):
        super().__init__(*args,**kwargs)
        self.visible=True
    def draw(self):
        if self.visible:
            super().draw()

class EmptyActor(Actor):
    def __init__(self, **kwargs):
        self._handle_unexpected_kwargs(kwargs)
        self.__dict__["_rect"] = ZRect((0, 0), (0, 0))
        self._orig_surf=self._surf=placeholder_image
        # self._init_position(pos, anchor, **kwargs)

def get_empty_actor():
    return EmptyActor()

def scale(actor, new_width, new_height):
    actor._surf=pygame.transform.scale(actor._surf, (new_width, new_height))
    actor.anchor=(new_width/2,new_height/2)
    actor.width=new_width
    actor.height=new_height

def scale_center(actor,new_width,new_height):
    old_width=actor.width
    old_height=actor.height
    actor._surf=pygame.transform.scale(actor._surf, (new_width, new_height))
    actor.width=new_width
    actor.height=new_height
    actor.x-=(new_width-old_width)/2
    actor.y-=(new_height-old_height)/2
    actor.anchor=(actor.width/2,actor.height/2)

def scale_without_img(actor,ratio):

    actor.width=actor.width*ratio
    actor.height=actor.height*ratio
    # actor.anchor=(actor.width/2,actor.height/2)

def load_png_with_scale(filename,size):
    img=pygame.image.load("./images/"+filename+".png")
    img=pygame.transform.scale(img, size)
    return img

def rectangle_actor(width,height,color=(255,255,255)):
    actor = get_empty_actor()
    actor.anchor=(width/2,height/2)
    actor._surf = pygame.Surface((width, height)) 
    actor._surf.fill(color)
    actor.width=width
    actor.height=height
    return actor
from typing import List,Tuple, override
cache={}
def get_images_from_folder(folder_path)->List[pygame.Surface]:
    if folder_path in cache:
        return cache[folder_path]
    images = []
    folder_path =f"images/{folder_path}"
    for filename in os.listdir(folder_path):
        if filename.endswith((".png", ".jpg", ".jpeg")):
            image_path = os.path.join(folder_path, filename)
            image = pygame.image.load(image_path)
            images.append(image)
    cache[folder_path]=images
    return images

gif_actors=[]
class GifActor(EmptyActor):
    def __init__(self, gif_path,size:Tuple[int,int]=None):
        super().__init__()
        self.frames = []
        self.current_frame = 0
        self.animation_speed = 0.1
        self.time_since_last_frame = 0
        self.visible=True
        gif_actors.append(self)
        
        self.frames=get_images_from_folder(gif_path)

        if not self.frames:
            raise ValueError(f"Failed to load GIF frames from {gif_path}")
            
        self._surf = self.frames[0]
        self.width = self._surf.get_width()
        self.height = self._surf.get_height()
        self.anchor = (self.width/2, self.height/2)
        self.range=(0,len(self.frames))

        if size is not None:
            scale(self,size[0],size[1])
            tmp=[]
            for frame in self.frames:
                tmp.append(pygame.transform.scale(frame, size))
            self.frames=tmp
    
    def update(self, dt):
        if self.visible:
            self.time_since_last_frame += dt
            if self.time_since_last_frame >= self.animation_speed:
                self.time_since_last_frame = 0
                self.current_frame +=1
                if self.current_frame>=self.range[1]:
                    self.current_frame=self.range[0]
                self._surf = self.frames[self.current_frame]
        else:
            self._surf = placeholder_image
            
    def draw(self):
        super().draw()

def padding(text,length:int=4):
    text=str(text)
    return text.ljust(length)

def draw_text(text,position,color=text_color):
    screen.draw.text(text,
        position,
        fontsize=20,
        fontname='ys', 
        color=color)

def draw_text_center(text,position):
    screen.draw.text(text,
        center=position,
        fontsize=20,
        fontname='ys', 
        color=text_color)
def ratio_to_color(ratio): #根据比例返回颜色
    if ratio>0.5:
        return (0,255,0)
    elif ratio>0.2:
        return (255,255,0)
    else:
        return (255,0,0)
def draw_health_bar(value:int,max_health:int,position:Tuple[int,int],size:Tuple[int,int]=(100,20),color=(0,0,0),tips="",x_center_flag=False):
    if x_center_flag:
        position=(position[0]-size[0]/2,position[1])
    screen.draw.rect(Rect(position,size),color)
    margin=2
    inner_width=size[0]-2*margin
    inner_height=size[1]-2*margin
    ratio=value/max_health
    screen.draw.filled_rect(Rect((position[0]+margin,position[1]+margin),(inner_width*ratio,inner_height)),ratio_to_color(ratio))
    draw_text_center(f"{tips} {value:.0f}/{max_health}",(position[0]+size[0]/2,position[1]+size[1]/2))

def normalize(x,y,thershold=5): #归一化向量
    length=math.sqrt(x*x+y*y)
    if length<thershold:
        return (0,0)
    return (x/length,y/length)

class TextActor(EmptyActor):
    def __init__(self, text,fontsize,**kwargs):
        super().__init__()
        self.text = text
        self.fontsize = fontsize
        self.color = kwargs.get("color", "white")
        self.set_width_height()
        
    def set_width_height(self):
        font = pygame.font.Font("fonts/ys.ttf", 20)
        text_surface = font.render(self.text, True, (255, 255, 255))
        h= text_surface.get_height()
        w= text_surface.get_width()
        self.width=w
        self.height=h
        self.anchor=(w/2,h/2)
        
    def draw(self):
        screen.draw.text(
            self.text, 
            center=self.pos,
            color=self.color,
            fontsize=self.fontsize,
            fontname='ys', )

def vector_y_offset(vector,offset): 
    x,y=vector
    return (x,y+offset)

environments=get_images_from_folder("env")

class RandomEnvironment(EmptyActor):
    def __init__(self,size:Tuple[int,int]=(100,100)):
        super().__init__()
        self._surf=random.choice(environments)
        scale(self,*size)

effects=[]

class Effect():
    def __init__(self,target,time):
        self.target=target
        self.time=time
        effects.append(self)
    def tick(self):
        if self.time>0:
            self.invoke()
            self.time-=assets.elapsed_time_frame
        else:
            self.on_finish()
            effects.remove(self)
    def invoke(self):
        pass
    def on_finish(self):
        pass

class DiffuseEffect(Effect):
    def __init__(self,target,direction):
        super().__init__(target,500)
        self.direction=direction
    def invoke(self):
        ratio=1+2*assets.elapsed_time_frame/1000
        scale_center(self.target,self.target.width*ratio,self.target.height*ratio)
        x_delta=self.direction*300*assets.elapsed_time_frame/1000
        self.target.x+=x_delta
    def on_finish(self):
        self.target._surf=placeholder_image

class RepelEffect(Effect):
    def __init__(self,target,direction,strength=300):
        super().__init__(target,500)
        self.direction=direction
        self.strength=strength
    def invoke(self):
        self.target.x+=self.direction[0]*self.strength*assets.elapsed_time_frame/1000
        self.target.y+=self.direction[1]*self.strength*assets.elapsed_time_frame/1000

class ExplosionEffect(Effect):
    def __init__(self,target,time=500,strength=3):
        super().__init__(target,time)
        self.strength=strength
    def invoke(self):
        ratio=1+self.strength*assets.elapsed_time_frame/1000
        scale_center(self.target,self.target.width*ratio,self.target.height*ratio)
    def on_finish(self):
        self.target._surf=placeholder_image
        self.target.visible=False

class Attack(EnhancedActor):
    def __init__(self,img):
        super().__init__(img)
        self.attacked=[]
    def try_attack(self,enemy):
        if not self.visible:
            return 
        actor=enemy
        if not isinstance(actor,Actor):
            actor=enemy.actor
        if enemy in self.attacked:
            return
        if self.colliderect(actor):
            self.attacked.append(enemy)
            self.attack(enemy)
    def attack(self,enemy):
        pass

class SmokeAttack(Attack):
    def __init__(self,direction,pos,reke_version):
        super().__init__("smoke")
        self.pos=pos
        DiffuseEffect(self,direction)
        self.strength=mapping.reke_version_repel_strength(reke_version)
        self.damage=mapping.reke_version_damage(reke_version)
    def attack(self,enemy):
        enemy.attr.attacked(self.damage)
        # 击退
        direction=normalize(enemy.x-self.x,enemy.y-self.y,0)
        RepelEffect(enemy,direction,self.strength)


class ExplodeAttack(Attack):
    def __init__(self,strength,pos):
        super().__init__("explode")
        self.strength=strength
        self.pos=pos
        ExplosionEffect(self,100,self.strength)
    def attack(self,enemy):
        enemy.attacked(50)