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
        self.visible=True
        # self._init_position(pos, anchor, **kwargs)
    def draw(self):
        if self.visible:
            super().draw()
def get_empty_actor():
    return EmptyActor()

def scale(actor:Actor, new_width, new_height):
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

def scale_ratio(actor:Actor,ratio):
    actor._orig_surf = actor._surf=pygame.transform.scale(actor._surf, (actor.width*ratio, actor.height*ratio))
    actor.width=actor.width*ratio
    actor.height=actor.height*ratio
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

def flip_pygame_surface(surface):
    return pygame.transform.flip(surface, True, False)

def clone_actor(actor:Actor):
    new_actor=get_empty_actor()
    new_actor._surf=actor._surf.copy()
    new_actor.width=actor.width
    new_actor.height=actor.height
    new_actor.anchor=actor.anchor
    return new_actor

def xor(a,b)->bool:
    return (a and not b) or (not a and b)

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
        self.flip_state=False
        
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
        self.frame_flip_state=[False]*len(self.frames)
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
        if xor(self.flip_state,self.frame_flip_state[self.current_frame]):
            self.frames[self.current_frame]=flip_pygame_surface(self.frames[self.current_frame])
            self._surf = self.frames[self.current_frame]
            self.frame_flip_state[self.current_frame]=not self.frame_flip_state[self.current_frame]
            
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

def draw_text_center(text,position,color=text_color):
    screen.draw.text(text,
        center=position,
        fontsize=20,
        fontname='ys', 
        color=color)
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
        if not self.visible:
            return
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

import typing
import enum
class EffectType(enum.Enum):
    POSITIVE=enum.auto()
    NEGATIVE=enum.auto()
    NEUTRAL=enum.auto()


effect_type_to_color={
    EffectType.POSITIVE:(51,255,255),
    EffectType.NEGATIVE:(153,0,0),
    EffectType.NEUTRAL:(204,204,0)
}

class Effect():
    def __init__(self,target,time):
        self.target=target
        self.time=time
        self.duration=time
        effects.append(self)
        self.isShowUI=False
        self.tips="default"
        self.attach_on_finish_functions=[]
        self.type=EffectType.NEUTRAL
    def tick(self):
        if self.time>0:
            self.invoke()
            self.time-=assets.elapsed_time_frame
        else:
            self.on_finish()
            for func in self.attach_on_finish_functions:
                func()
            effects.remove(self)

    def invoke(self):
        pass
    def on_finish(self):
        pass
    def get_str(self):
        return f"{self.tips} {self.time/1000:.1f}s"

effects:typing.List[Effect]=[]

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
        self.target.visible=False

class RepelEffect(Effect):
    def __init__(self,target,direction,strength=300.0,isVanish=False,isShowText=False):
        super().__init__(target,500)
        self.direction=direction
        self.strength=strength
        self.isVanish=isVanish
        self.isShowUI=isShowText
        self.tips="被击退"
        self.type=EffectType.NEGATIVE
    def invoke(self):
        self.target.x+=self.direction[0]*self.strength*assets.elapsed_time_frame/1000
        self.target.y+=self.direction[1]*self.strength*assets.elapsed_time_frame/1000
    def on_finish(self):
        if self.isVanish:
            self.target._surf=placeholder_image
            self.target.visible=False
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

class SlowRecoverEffect(Effect):
    def __init__(self,target,time=5*1000,strength=5):
        super().__init__(target,time)
        self.strength=strength
        self.isShowUI=True
        self.tips="缓慢恢复生命"
        self.type=EffectType.POSITIVE
    def invoke(self):
        delta=self.strength*assets.elapsed_time_frame/1000
        self.target.health=min(self.target.health+delta,self.target.max_health)

class PoisonEffect(Effect):
    def __init__(self,target,time=5*1000,strength=4):
        super().__init__(target,time)
        self.strength=strength
        self.isShowUI=True
        self.tips="中毒"
        self.type=EffectType.NEGATIVE
    def invoke(self):
        delta=self.strength*assets.elapsed_time_frame/1000
        self.target.health=max(self.target.health-delta,1)

class InflateEffect(Effect):
    def __init__(self,target,time=1*1000,strength=1.5):
        super().__init__(target,time)
        self.strength=strength
        self.w_original=self.target.width
        self.h_original=self.target.height
    @override
    def invoke(self):
        currentRatio=(1-self.time/self.duration)*(self.strength-1)+1
        h=self.h_original*currentRatio
        w=self.w_original*currentRatio
        # scale(self.target,w,h)
        self.target._surf=pygame.transform.scale(self.target._surf, (w, h))
    @override
    def on_finish(self):
        pass
        # ResizeEffect(self.target,self.w_original,self.h_original,self.duration)

class ResizeEffect(Effect):
    def __init__(self,target,width,height,width_orig,height_orig,time=1*1000,):
        super().__init__(target,time)
        self.w_original=width_orig
        self.h_original=height_orig
        self.target_width=width
        self.target_height=height
    @override
    def invoke(self):
        currentRatio=(1-self.time/self.duration)
        h=self.h_original*(1-currentRatio)+self.target_height*(currentRatio)
        w=self.w_original*(1-currentRatio)+self.target_width*(currentRatio)
        self.target._surf=pygame.transform.scale(self.target._surf, (w, h))
        self.target.anchor=(w/2,h/2)
    @override
    def on_finish(self):
        ResizeEffect(self.target,self.w_original,self.h_original,self.target_width,self.target_height,self.duration)

class FontSizeEffect(Effect):
    def __init__(self,target,speed=3,low=20,high=30):
        super().__init__(target,1145141919810)
        self.low=low
        self.high=high
        self.speed=speed
        self.stop=False
        self.increase=True
    @override
    def invoke(self):
        if self.stop:
            self.time=0
            return
        if self.increase:
            self.target.fontsize+=self.speed*assets.elapsed_time_frame/1000
            if self.target.fontsize>=self.high:
                self.increase=False
        else:
            self.target.fontsize-=self.speed*assets.elapsed_time_frame/1000
            if self.target.fontsize<=self.low:
                self.increase=True


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

cigarette_surface=pygame.image.load("./images/cigarette.png")

class CigaretteAttack(Attack):
    def __init__(self,pos,angle,reke_version):
        super().__init__("cigarette-2")
        direction=(math.cos(angle),math.sin(angle))
        scale_ratio(self,0.5)
        scale_without_img(self,2)
        self.angle=-mapping.rad_to_deg(angle)
        self.strength=mapping.reke_version_repel_strength(reke_version)*2
        self.pos=pos
        self.damage=mapping.reke_version_cigarette_damage(reke_version)
        RepelEffect(self,direction,mapping.reke_version_to_cigrarette_strength(reke_version),isVanish=True)
    @override
    def attack(self,enemy):
        enemy.attr.attacked(self.damage)
        direction=normalize(enemy.x-self.x,enemy.y-self.y,0)
        RepelEffect(enemy,direction,self.strength)
    
transparent_gray = (100, 100,100, 128)
cd_counter_list=[]
x_offset=-1
y_offset=35
class CDableAttackUI:
    def __init__(self,img,cd_time,tip_message="default"):
        global x_offset
        if x_offset==-1:
            x_offset=assets.screen_width-310
        self.size_x=60
        self.top_x=x_offset
        x_offset+=self.size_x+20
        scale(img,self.size_x,self.size_x)
        img.anchor=(0,0)
        img.pos=(self.top_x,y_offset)
        self.img=img
        self.cd_time=cd_time
        self.cd=0
        cd_counter_list.append(self)
        self.tip_message=tip_message
    def can_use(self):
        return self.cd<=0
    def use(self):
        self.cd=self.cd_time
    def tick(self):
        if self.cd>0:
            self.cd-=assets.elapsed_time_frame
        else:
            self.cd=0
    def draw(self):
        ratio=self.cd/self.cd_time
        cd_height=self.size_x*ratio
        self.img.draw()
        if cd_height>0:
            screen.draw.filled_rect(Rect(self.top_x,y_offset+self.size_x-cd_height,self.size_x,cd_height),color=transparent_gray)
        screen.draw.rect(Rect(self.top_x,y_offset,self.size_x,self.size_x),color="black")
        draw_text_center(self.tip_message,(self.top_x+self.size_x/2,y_offset+self.size_x+15),"black")