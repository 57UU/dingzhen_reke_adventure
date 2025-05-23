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
x_left_door=None
level_count=0

screen_width=-1
screen_height=-1

elapsed_time_frame=0

class MainActor: 
    def __init__(self):
        self.health=100 #生命值
        self.max_health=100 #最大生命值
        self.score=0 #分数
        self.moving_speed=3
        self.inventory=[] #背包
        self.actor=Actor("dz")
        img_size=(100,100)
        scale(self.actor,*img_size)
        scale_without_img(self.actor,0.5)
        self.actor.pos=(100,100)
        self.reke_version=1
        self.reke_max_power=5
        self.reke_power=5
        self.dz_normal=load_png_with_scale("dz",img_size)
        self.dz_cry=load_png_with_scale("dz-cry",img_size)
        self.cry_value=0
    def set_position(self,position): #设置位置
        self.actor.pos=position
    def be_attacked(self,damage):
        self.health-=damage
        self.cry_value=10
    def get_position(self): #获取位置
        return self.actor.pos
    def handle_moving(self,x,y): 
        pos_x,pos_y=self.get_position()
        pos_x+=x*self.moving_speed
        pos_y+=y*self.moving_speed
        #constrain pos_x between 0 and screen.width
        if pos_x<0:
            pos_x=0
        if pos_x>screen.width:
            pos_x=screen.width
        #constrain pos_y between 0 and screen.height
        if pos_y<0:
            pos_y=0
        if x_left_door != None and x<0:
            if pos_x<x_left_door.x:
                pos_x=x_left_door.x
        if pos_y>screen.height:
            pos_y=screen.height
        self.set_position((pos_x,pos_y))
            
    def draw(self):
        self.actor.draw() 
        bar_zise=(300,30)
        draw_health_bar(self.health,self.max_health,(0,0),bar_zise,tips="生命值")
        draw_health_bar(self.reke_power,self.reke_max_power,(screen_width-310,0),bar_zise,tips="锐克电量")
        text=f"速度：{padding(self.moving_speed)}"
        draw_text(text,(0,40))
        t2=f"武器：锐克{self.reke_version}代"
        draw_text(t2,(0,60))
        t3=f"第{padding(level_count)}关"
        draw_text(t3,(400,0))
        
    def tick(self):
        if self.cry_value>0:
            self.actor._surf=self.dz_cry
            self.cry_value-=0.5
        else:
            self.actor._surf=self.dz_normal

class Scene:
    def __init__(self,width,height,mainActor):
        self.width=width
        self.height=height
        self.mainActor=mainActor
        tips=TextActor("向右移动以开始>>>", 30, color="red")
        tips.pos=(width/2,height/2)
        self.doors=[] #门 
        self.elements=[tips] #场景静态元素
        self.actors=[] #场景动态元素
        self.background=empty_actor(width,height,(255,255,255))
        self.deltaXCount=0
        self.generate_level()
        
    def delta_x(self,delta): 
        self.deltaXCount+=-delta
        for element in self.doors:
            element.x+=delta
        for actor in self.actors:
            actor.x+=delta
        for element in self.elements:
            element.x+=delta
        # self.background.x+=delta

        #gc
        thershold=-self.width*1.5
        for element in self.doors:
            if element.x<thershold:
                self.doors.remove(element)
        for actor in self.actors:
            if actor.x<thershold:
                self.actors.remove(actor)
        for element in self.elements:
            if element.x<thershold:
                self.elements.remove(element)
    def tick(self): 
        if self.deltaXCount>=self.width:
            self.deltaXCount-=self.width
            self.generate_level()
        for enemy in self.actors:
            enemy.attr.tick()
    def generate_level(self):
        global level_count
        level_count+=1
        x_offset=self.deltaXCount+self.width
        door1=empty_actor(10,self.height/2,(255,255,0))
        door1.pos=(x_offset,self.height/4)
        self.doors.append(door1)
        door2=empty_actor(10,self.height/2,(255,0,255))
        door2.pos=(x_offset,self.height*3/4)
        self.doors.append(door2)
        door1.attr=get_random_door()(door1)
        door2.attr=get_random_door()(door2)
        door1.attr.other=door2.attr
        door2.attr.other=door1.attr

        cat_ememy=GifActor("cat",(100,100))
        cat_ememy.pos=(x_offset+self.width*2/3,self.height/2)
        cat_ememy.attr=CatEnemy(cat_ememy,self.mainActor,door1,self.width)
        self.actors.append(cat_ememy)

    def draw(self): 
        self.background.draw()
        for element in self.doors:
            element.draw()
            element.attr.draw()
        for actor in self.actors:
            actor.draw()
            actor.attr.draw()
        for element in self.elements:
            element.draw()



class Door:
    def __init__(self,bind:Actor,other=None):
        self.actor=bind
        self.isUsed=False
        self.tips="default"
        self.color="red"
        self.other=None
    def on_enter(self,mainActor:MainActor):
        global x_left_door
        if self.isUsed:
            return
        if self.other is not None:
            self.other.isUsed=True
        x_left_door=self.actor
        self.isUsed=True
        pass
    def draw(self):
        screen.draw.text(
            self.tips, 
            self.actor.pos,
            color="gray" if self.isUsed else self.color,
            fontsize=20,
            fontname='ys', )

class HealthIncreaseDoor(Door): #增加生命值
    def __init__(self,bind:Actor):
        super().__init__(bind)
        self.health=100
        self.tips="恢复生命值"
    def on_enter(self,mainActor:MainActor):
        if self.isUsed:
            return
        super().on_enter(mainActor)
        
        mainActor.health=mainActor.max_health

class SpeedIncreaseDoor(Door): #增加速度
    def __init__(self,bind:Actor):
        super().__init__(bind)
        self.tips="加速"
    def on_enter(self,mainActor:MainActor):
        if self.isUsed:
            return
        super().on_enter(mainActor)
        
        mainActor.moving_speed+=1

doors=[HealthIncreaseDoor, SpeedIncreaseDoor]
def get_random_door(): #随机生成一个门
    return random.choice(doors)

class EnemyData: 
    def __init__(self,bind:Actor,mainActor:MainActor,door:Door,x_range_lim):
        self.actor=bind
        self.mainActor=mainActor
        self.tips="default"
        self.health=100
        self.max_health=100
        self.moving_speed=3
        self.door=door
        self.x_range_lim=x_range_lim
        self.cd=0 #milliseconds
    def tick(self):
        if self.cd>0:
            self.cd-=elapsed_time_frame
            return
        x_direction=self.mainActor.get_position()[0]-self.actor.pos[0]
        y_direction=self.mainActor.get_position()[1]-self.actor.pos[1]
        x_direction,y_direction=normalize(x_direction,y_direction)
        self.actor.x+=x_direction*self.moving_speed
        self.actor.y+=y_direction*self.moving_speed
        left_lim=self.door.x
        right_lim=self.door.x+self.x_range_lim
        self.actor.x=max(left_lim,self.actor.x)
        self.actor.x=min(right_lim,self.actor.x)
    def draw(self):
        screen.draw.text(
            self.tips, 
            self.actor.pos,
            color="black",
            fontsize=20,
            fontname='ys', )
        draw_health_bar(self.health,self.max_health,self.actor.pos,(100,10)) #绘制血条



class CatEnemy(EnemyData): 
    def __init__(self,bind:Actor,mainActor:MainActor,door:Door,x_range_lim):
        super().__init__(bind,mainActor,door,x_range_lim)
        self.tips="耄耋"
    def tick(self):
        super().tick()
        if self.cd>0:
            return
        if self.actor.colliderect(self.mainActor.actor):
            self.mainActor.be_attacked(10)
            self.cd=200
            