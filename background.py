import pgzrun  # 导入游戏库
import pgzero.screen
import pgzero.keyboard
from pgzero.actor import Actor
import pygame
import random
import math
from utils import *
import assets
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
        self.img_size=img_size
        scale(self.actor,*img_size)
        scale_without_img(self.actor,0.5)
        self.actor.pos=(100,100)
        self.reke_version=1
        self.reke_max_power=5
        self.reke_power=5
        self.dz_normal=load_png_with_scale("dz",img_size)
        self.dz_cry=load_png_with_scale("dz-cry",img_size)
        self.cry_value=0
        self.body=Body()
        self.direction=1 #1:right -1:left
        self.attack_cd_counter=0
        self.attack_cd=400 #ms
        self.tip_text=""
        self.tip_text_timer=0
    def set_tip_text(self,text): #设置提示文本
        self.tip_text=text
        self.tip_text_timer=1200
    def set_position(self,position): #设置位置
        self.actor.pos=position
        self.body.actor.x=position[0]
        self.body.actor.y=position[1]+60
    def be_attacked(self,damage):
        self.health-=damage
        self.cry_value=10
    def get_position(self): #获取位置
        return self.actor.pos
    def attack(self): #攻击
        if self.attack_cd_counter>0:
            return
        if self.reke_power<=0:
            return
        self.reke_power-=1
        self.attack_cd_counter=self.attack_cd #ms
    def handle_moving(self,x,y): 
        if x<0:
            self.body.direction=-1
            self.direction=-1
            self.body.state=2
        elif x>0:
            self.body.direction=1
            self.direction=1
            self.body.state=2
        else:
            self.body.state=1
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
        self.body.draw()
        self.actor.draw() 
        bar_zise=(300,30)
        draw_health_bar(self.health,self.max_health,(0,0),bar_zise,tips="生命值")
        draw_health_bar(self.reke_power,self.reke_max_power,(screen_width-310,0),bar_zise,tips="锐克电量")
        text=f"速度：{padding(self.moving_speed)}"
        draw_text(text,(0,40))
        t2=f"武器：锐克{self.reke_version}代 使用[F]攻击"
        draw_text(t2,(0,60))
        t3=f"第{padding(level_count)}关"
        draw_text(t3,(400,0))

        draw_health_bar(self.attack_cd_counter,self.attack_cd,(screen_width-310,35),vector_y_offset(bar_zise,-10),tips="攻击冷却")

        if self.tip_text_timer>0:
            draw_text(self.tip_text,(0,screen_height-30))
        if assets.debug:
            left=self.actor.x-self.actor.width/2
            top=self.actor.y-self.actor.height/2
            main_actor_rect = Rect((left,top), (self.actor.width, self.actor.height))  

            screen.draw.rect(main_actor_rect, "red")
        
        
    def tick(self):
        self.body.tick()
        if self.cry_value>0:
            self.actor._surf=self.dz_cry
            self.cry_value-=0.5
        else:
            self.actor._surf=self.dz_normal
        if self.attack_cd_counter>0:
            self.attack_cd_counter-=elapsed_time_frame
        elif self.attack_cd_counter<0:
            self.attack_cd_counter=0
        
        if self.tip_text_timer>0:
            self.tip_text_timer-=elapsed_time_frame

class Body:
    def __init__(self):
        self.runlefts=[]
        self.runrights=[]
        size=(100,60)
        for i in range(8):
            img=load_png_with_scale(f"animation/runleft{i}",size)
            self.runlefts.append(img)
            self.runrights.append(pygame.transform.flip(img,True,False))
        self.count=0
        self.timer=0
        self.standleft=load_png_with_scale("animation/standleft",size)
        self.standright=load_png_with_scale("animation/standright",size)
        self.actor=Actor("placeholder")
        scale(self.actor,*size)
        self.actor._surf=self.standright
        self.direction=1 #1:right -1:left
        self.state=1 #1:stand 2:run
    def tick(self):

        if self.state==1:
            if self.direction==1:
                self.actor._surf=self.standright
            else:
                self.actor._surf=self.standleft
            self.count=0
            self.timer=0
        elif self.state==2:
            if self.direction==1:
                self.actor._surf=self.runrights[int(self.count)]
            else:
                self.actor._surf=self.runlefts[int(self.count)]
        self.timer+=elapsed_time_frame
        if self.timer>100:
            self.timer=0
            self.count=(self.count+1)%8
    def draw(self):
        self.actor.draw()


class Scene:
    def __init__(self,width,height,mainActor):
        self.width=width
        self.height=height
        self.mainActor=mainActor
        tips=TextActor("向右移动以开始>>>\n按下[F]使用锐克攻击\n道具[尼古丁]可以升级锐克等级\n道具[电池]可以恢复锐克电量", 30, color="red")
        tips.pos=(width/2,height/2)
        self.doors=[] #门 
        self.elements=[tips] #场景静态元素
        self.actors=[] #场景动态元素
        self.tools=[] #道具
        self.lists=[self.doors,self.elements,self.actors,self.tools]
        self.background=empty_actor(width,height,(255,255,255))
        self.deltaXCount=0
        self.generate_level()
        
    def delta_x(self,delta): 
        self.deltaXCount+=-delta
        for list in self.lists:
            for element in list:
                element.x+=delta
        # self.background.x+=delta

        #gc
        thershold=-self.width*1.5
        for list in self.lists:
            for element in list:
                if element.x<thershold:
                    list.remove(element)
    def tick(self): 
        if self.deltaXCount>=self.width:
            self.deltaXCount-=self.width
            self.generate_level()
        for enemy in self.actors:
            enemy.attr.tick()
    def get_random_point(self,margin=100): 
        x_offset=self.deltaXCount+self.width
        x=random.uniform(x_offset+margin,x_offset+self.width-margin)
        y = random.uniform(margin, self.height - margin)
        return (x,y)
    def get_random_point_environment(self,margin=200,updown=False): 
        x_offset=self.deltaXCount+self.width
        x=random.uniform(x_offset,x_offset+self.width)
        if updown:
            y = random.uniform(0,margin)
        else:
            y = random.uniform(self.height-margin,self.height)
        return (x,y)
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

        if random.random()<0.5:
            battery=Battery()
            battery.pos=self.get_random_point()
            self.tools.append(battery)
        if random.random()<0.5:
            nicotine=Nicotine()
            nicotine.pos=self.get_random_point()
            self.tools.append(nicotine)

        for i in range(10):
            environment=RandomEnvironment()
            environment.pos=self.get_random_point_environment(updown=i<5)
            self.elements.append(environment)
        

        cat_ememy=GifActor("cat",(100,100))
        cat_ememy.pos=(x_offset+self.width*2/3,self.height/2)
        cat_ememy.attr=CatEnemy(cat_ememy,self.mainActor,door1,self.width)
        self.actors.append(cat_ememy)

    def draw(self): 
        self.background.draw()
        for element in self.elements:
            element.draw()
        for tool in self.tools:
            tool.draw()
        for element in self.doors:
            element.draw()
            element.attr.draw()
        for actor in self.actors:
            actor.draw()
            actor.attr.draw()



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

class RecoverRekePowerDoor(Door): #增加锐克电量
    def __init__(self,bind:Actor):
        super().__init__(bind)
        self.tips="恢复锐克电量"
    def on_enter(self,mainActor:MainActor):
        if self.isUsed:
            return
        super().on_enter(mainActor)
        mainActor.reke_power=mainActor.reke_max_power
        
doors=[HealthIncreaseDoor, SpeedIncreaseDoor,RecoverRekePowerDoor]
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
            center=vector_y_offset(self.actor.pos,-45),
            color="black",
            fontsize=20,
            fontname='ys', )
        draw_health_bar(self.health,self.max_health,vector_y_offset(self.actor.pos,-30),(100,10),x_center_flag=True) #绘制血条
        if assets.debug:
            left=self.actor.x-self.actor.width/2
            top=self.actor.y-self.actor.height/2
            main_actor_rect = Rect((left,top), (self.actor.width, self.actor.height))
            screen.draw.rect(main_actor_rect, "red")



class CatEnemy(EnemyData): 
    def __init__(self,bind:Actor,mainActor:MainActor,door:Door,x_range_lim):
        super().__init__(bind,mainActor,door,x_range_lim)
        self.tips="耄耋"
        scale_without_img(self.actor,0.6)
    def tick(self):
        super().tick()
        if self.cd>0:
            return
        if self.actor.colliderect(self.mainActor.actor):
            self.mainActor.be_attacked(10)
            self.cd=200
            

class Tool(Actor):
    def __init__(self,image):
        super().__init__(image)
        scale(self,50,50)
        self.tips="default"
        self.isUsed=False
    @override
    def draw(self):
        if self.isUsed:
            return
        super().draw()
        draw_text_center(self.tips,vector_y_offset(self.pos,40))
    def invoke(self,mainActor:MainActor):
        if self.isUsed:
            return
        if self.colliderect(mainActor.actor):
            self.isUsed=True
            self.onUse(mainActor)
    def onUse(self,mainActor:MainActor):
        pass

class Nicotine(Tool):
    def __init__(self):
        super().__init__("nicotine")
        self.tips="尼古丁"
    @override
    def onUse(self,mainActor:MainActor):
        mainActor.reke_version+=1
        mainActor.set_tip_text("你的锐克升级了！")


class Battery(Tool):
    def __init__(self):
        super().__init__("battery")
        self.tips="电池"
    @override
    def onUse(self,mainActor:MainActor):
        mainActor.reke_power=min(mainActor.reke_max_power,mainActor.reke_power+1)