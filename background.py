import pgzrun  # 导入游戏库
import pgzero.screen
import pgzero.keyboard
from pgzero.actor import Actor
import pygame
import random
import math
from utils import *
screen : pgzero.screen.Screen

moving_speed=3

difficulty=1 #约大越难

class Scene:
    def __init__(self, width:int,height:int):
        self.elements=[]
        self.left_wall=width/6
        self.right_wall=width*5/6
        self.logic_width=width*2/3
        actor = Actor("placeholder")  
        actor.anchor=(width*2/3/2,height/2)
        actor._surf = pygame.Surface((width*2/3, height)) 
        actor._surf.fill((255, 255, 255))
        actor.pos=(width/2,height/2)
        self.actor=actor
        self.count=148
        self.height=height
    def tick(self):
        self.count+=1
        if self.count%150==0:
            self.count=0
            a=empty_actor(self.logic_width/2,10,(255,0,0))
            a.pos=(self.left_wall+self.logic_width/4,0)
            a2=empty_actor(self.logic_width/2,10,(0,255,0))
            a2.pos=(self.left_wall+self.logic_width/4*3,0)
            self.elements.append(a)
            self.elements.append(a2)

            doors=[choose_door_negtive(), choose_door_positive()]
            random.shuffle(doors)
            a.door=doors[0](a)
            a2.door=doors[1](a2)

            # gc
            for element in self.elements:
                if element.pos[1]>self.height+20:
                    self.elements.remove(element)
        for element in self.elements:
            p=element.pos
            element.pos=(p[0],p[1]+moving_speed)
    def draw(self):
        self.actor.draw()
        for element in self.elements:
            element.draw()
            element.door.draw()
    def gen_door(self):
        pass

class Door:
    def __init__(self,doorActor:Actor):
        self.doorActor=doorActor
    def invoke(self,doorActor:Actor):
        pass
    def draw(self):
        pass
    def draw_text(self,text):
        screen.draw.text(text,
         self.doorActor.pos, 
         fontsize=20,
         fontname='s', 
         color='black')

class IncreaseDoor(Door):
    def __init__(self,doorActor:Actor):
        super().__init__(doorActor)
        self.limit=3
        self.count=0
        self.colide_actors=[]
    def invoke(self,actor:Actor):
        if(self.count>=self.limit or actor in self.colide_actors):
            return
        if(self.doorActor.colliderect(actor)):
            actor.increaseFlag+=1
            self.colide_actors.append(actor)
            self.count+=1
    def draw(self):
        self.draw_text(f"x+{self.limit}")

class DecreaseDoor(Door):
    def __init__(self,doorActor:Actor):
        super().__init__(doorActor)
        self.limit=3
        self.count=0
        self.colide_actors=[]
    def invoke(self,actor:Actor):
        if(self.count>=self.limit or actor in self.colide_actors):
            return
        if(self.doorActor.colliderect(actor)):
            actor.increaseFlag=-1
            self.colide_actors.append(actor)
            self.count+=1
    def draw(self):
        self.draw_text(f"x-{self.limit}")

class MultiplyDoor(Door):
    def __init__(self,doorActor:Actor):
        super().__init__(doorActor)
        self.limit=3
        self.count=0
        self.colide_actors=[]
    def invoke(self,actor:Actor):
        if(self.count>=self.limit or actor in self.colide_actors):
            return
        if(self.doorActor.colliderect(actor)):
            actor.increaseFlag=random.randint(1,3)
            self.colide_actors.append(actor)
            self.count+=1
    def draw(self):
        self.draw_text(f"x*{self.limit}")

DoorPositive=[
    IncreaseDoor,
]
DoorNegtive=[
    DecreaseDoor
]

def choose_door_positive():
    return random.choice(DoorPositive)
def choose_door_negtive():
    return random.choice(DoorNegtive)

class MainActor:
    def __init__(self):
        self.pos=(0,0)
        self.actors=[]
        self.center_attraction = 0.2  # 中心点引力系数
        self.separation_distance = 80  # 排斥作用距离
        self.separation_strength = 0.2  # 排斥力强度
        self.physicsCount=0
        
    def calculate_forces(self):
        # 计算中心点引力
        center = self.pos
        for actor in self.actors:
            dx = center[0] - actor.x
            dy = center[1] - actor.y
            actor.dx += dx * self.center_attraction
            actor.dy += dy * self.center_attraction
            
            # 计算个体间斥力
            for other in self.actors:
                if actor != other:
                    dist = math.sqrt((actor.x-other.x)**2 + (actor.y-other.y)**2)
                    dist=max(dist,1)
                    if dist < self.separation_distance:
                        repulse_x = (actor.x - other.x) / dist
                        repulse_y = (actor.y - other.y) / dist
                        strength = (self.separation_distance - dist) * self.separation_strength
                        actor.dx += repulse_x * strength
                        actor.dy += repulse_y * strength

    def tick(self):
        del_actors_index=[]
        index=0
        for actor in self.actors:
            if actor.increaseFlag>0:
                for c in range(actor.increaseFlag):
                    self.actors.append(self.buildActor(actor.pos))
                    actor.increaseFlag=0
            elif actor.increaseFlag<0:
                del_actors_index.append(index)
            index+=1

        for index in reversed(del_actors_index):
            self.actors.pop(index)
            
        self.delta_pos((0,moving_speed))
        
        if self.physicsCount%10==0:
            self.physicsCount=0
            # 初始化速度变量
            for actor in self.actors:
                actor.dx = 0
                actor.dy = 0
                
            # 计算各种力
            self.calculate_forces()
            
            # 应用速度
            for actor in self.actors:
                actor.x_target = actor.dx+actor.x
                actor.y_target = actor.dy+actor.y
        
        self.physicsCount+=1

        # 插值
        for actor in self.actors:
            actor.x += (actor.x_target - actor.x) * 0.3
            actor.y += (actor.y_target - actor.y) * 0.3
    def set_position(self,pos):
        self.pos=pos
    def getValue(self):
        return len(self.actors)
    def setValue(self,value):
        while len(self.actors)<value:
            self.actors.append(self.buildActor())
        while len(self.actors)>value:
            self.actors.pop()
    def delta_pos(self,delta):
        self.set_position((self.pos[0]+delta[0],self.pos[1]+delta[1]))
        for actor in self.actors:
            actor.x_target += delta[0]
            actor.y_target += delta[1]
    def draw(self):
        for actor in self.actors:
            actor.draw()
        screen.draw.text(str(len(self.actors)),
         self.pos, 
         fontsize=20,
         fontname='s', 
         color='green')

        
    def buildActor(self,pos=None):
        actor=Actor("dz")
        scale(actor,50,50)
        if pos==None:
            pos=self.pos
        actor.pos=(pos[0]+random.randint(0,20),pos[1]+random.randint(0,20))
        actor.x_target=actor.x
        actor.y_target=actor.y
        actor.increaseFlag=0
        return actor