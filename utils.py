import pygame
import os
import pgzero
from pgzero.actor import Actor
import math
from pgzero.rect import Rect

screen : pgzero.screen.Screen

text_color=(0, 25, 184)

def scale(actor, new_width, new_height):
    actor._surf=pygame.transform.scale(actor._surf, (new_width, new_height))
    actor.anchor=(new_width/2,new_height/2)
    actor.width=new_width
    actor.height=new_height

def scale_without_img(actor,ratio):

    actor.width=actor.width*ratio
    actor.height=actor.height*ratio
    actor.anchor=(actor.width/2,actor.height/2)

def load_png_with_scale(filename,size):
    img=pygame.image.load("./images/"+filename+".png")
    img=pygame.transform.scale(img, size)
    return img

def empty_actor(width,height,color=(255,255,255)):
    actor = Actor("placeholder")  
    actor.anchor=(width/2,height/2)
    actor._surf = pygame.Surface((width, height)) 
    actor._surf.fill(color)
    actor.width=width
    actor.height=height
    return actor
from typing import List,Tuple
def get_images_from_folder(folder_path)->List[pygame.Surface]:
    images = []
    folder_path =f"images/{folder_path}"
    for filename in os.listdir(folder_path):
        if filename.endswith((".png", ".jpg", ".jpeg")):
            image_path = os.path.join(folder_path, filename)
            image = pygame.image.load(image_path)
            images.append(image)
    return images

import imageio
from PIL import Image
gif_actors=[]
class GifActor(Actor):
    def __init__(self, gif_path,size:Tuple[int,int]=None):
        super().__init__("placeholder")
        self.frames = []
        self.current_frame = 0
        self.animation_speed = 0.1
        self.time_since_last_frame = 0
        gif_actors.append(self)
        
        self.frames=get_images_from_folder(gif_path)

        if not self.frames:
            raise ValueError(f"Failed to load GIF frames from {gif_path}")
            
        self._surf = self.frames[0]
        self.width = self._surf.get_width()
        self.height = self._surf.get_height()
        self.anchor = (self.width/2, self.height/2)

        if size is not None:
            scale(self,size[0],size[1])
            tmp=[]
            for frame in self.frames:
                tmp.append(pygame.transform.scale(frame, size))
            self.frames=tmp
    
    def update(self, dt):
        self.time_since_last_frame += dt
        if self.time_since_last_frame >= self.animation_speed:
            self.time_since_last_frame = 0
            self.current_frame = (self.current_frame + 1) % len(self.frames)
            self._surf = self.frames[self.current_frame]
            
    def draw(self):
        super().draw()

def padding(text,length:int=4):
    text=str(text)
    return text.ljust(length)

def draw_text(text,position):
    screen.draw.text(text,
        position,
        fontsize=20,
        fontname='ys', 
        color=text_color)

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
def draw_health_bar(value:int,max_health:int,position:Tuple[int,int],size:Tuple[int,int]=(100,20),color=(0,0,0),tips=""):
    screen.draw.rect(Rect(position,size),color)
    margin=2
    inner_width=size[0]-2*margin
    inner_height=size[1]-2*margin
    ratio=value/max_health
    screen.draw.filled_rect(Rect((position[0]+margin,position[1]+margin),(inner_width*ratio,inner_height)),ratio_to_color(ratio))
    draw_text_center(f"{tips} {value}/{max_health}",(position[0]+size[0]/2,position[1]+size[1]/2))

def normalize(x,y,thershold=5): #归一化向量
    length=math.sqrt(x*x+y*y)
    if length<thershold:
        return (0,0)
    return (x/length,y/length)

class TextActor(Actor):
    def __init__(self, text,fontsize,**kwargs):
        super().__init__("placeholder")
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