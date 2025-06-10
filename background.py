import pgzrun  # 导入游戏库
import pgzero.screen
import pgzero.keyboard
from pgzero.actor import Actor
import pygame
import random
import math
from utils import *
import assets
import mapping
screen : pgzero.screen.Screen

moving_speed=3
difficulty=1 #约大越难
x_left_door=None
level_count=0

def reset_global_variables():
    global moving_speed,difficulty,x_left_door,level_count
    x_left_door=None
    level_count=0
    moving_speed=3

class MainActor: 
    def __init__(self):
        self.isLosed=False 
        self.health=100 #生命值
        self.max_health=100 #最大生命值
        self.score=0 #分数
        self.moving_speed=3.0
        self.inventory=[] #背包
        self.actor=EnhancedActor("dz")
        img_size=(100,100)
        self.img_size=img_size
        scale(self.actor,*img_size)
        
        scale_ratio=0.5
        scale_without_img(self.actor,scale_ratio)
        self.actor.height*=2 
        scaled_w=img_size[0]*scale_ratio
        scaled_h=img_size[1]*scale_ratio
        self.actor.anchor=(scaled_w,scaled_h+20) 
        self.actor.pos=(assets.screen_width*2/3,assets.screen_height/2)
        self.reke_version=10 if assets.debug else 1
        self.reke_max_power=5
        self.reke_power:int=5
        self.dz_normal=load_png_with_scale("dz",img_size)
        self.dz_cry=load_png_with_scale("dz-cry",img_size)
        self.cry_value=0
        self.body=Body()
        self.direction=1 #1:right -1:left
        self.attack_cd_counter=0
        self.attack_cd=600 #ms
        self.normal_attack_ui=CDableAttackUI(EnhancedActor("cigarette-circle"),self.attack_cd,"[1]烟圈")
        self.big_reke_ui=CDableAttackUI(EnhancedActor("explode-reke"),self.attack_cd*5,"[2]炸锐")
        self.reke_to_health_ui=CDableAttackUI(EnhancedActor("reke-rec"),self.attack_cd*10,"[3]恢复")
        self.CDs=[self.normal_attack_ui,self.big_reke_ui,self.reke_to_health_ui]
        self.tip_text=""
        self.tip_text_timer=0
        self.scene:Scene
        self.cigarette=Cigarette()
        self.smoke=CDableAttackUI(EnhancedActor("placeholder"),self.attack_cd,"invisable")
        self.chain:EnhancedActor=None
    def set_tip_text(self,text): #设置提示文本
        self.tip_text=text
        self.tip_text_timer=1200
    @property
    def x(self): #获取x坐标
        return self.actor.x
    @x.setter
    def x(self,value): #设置x坐标
        self.set_position((value,self.actor.y))
    @property
    def y(self): #获取y坐标
        return self.actor.y
    @y.setter
    def y(self,value): #设置y坐标
        self.set_position((self.actor.x,value))
    def set_position(self,position): #设置位置
        if self.isLosed:
            return
        self.actor.pos=position
        x=position[0]
        y=position[1]
        self.body.actor.x=x
        self.body.actor.y=y+40
        cig_x=x
        cig_y=y-26
        self.cigarette.set_position((cig_x,cig_y))
    def attacked(self,damage): 
        self.be_attacked(damage)
    def be_attacked(self,damage):
        self.health-=damage
        self.cry_value=10
        if self.health<=0:
            self.isLosed=True
    def get_position(self): #获取位置
        return self.actor.pos
    def attack(self): #攻击
        if not self.normal_attack_ui.can_use():
            self.set_tip_text("攻击冷却中!!!")
            return
        if self.reke_power<=0:
            self.set_tip_text("锐克电量不足!!!")
            return
        self.reke_power-=1
        self.normal_attack_ui.use()
        self.smoke.use()
        attack_entity=SmokeAttack(self.direction,self.get_position(),self.reke_version)
        self.scene.self_misiles.append(attack_entity)
        
    def use_reke_to_health(self): #使用锐克恢复
        if self.reke_power<1:
            self.set_tip_text("锐克电量不足!!! 恢复需要1格电量")
            return
        if not self.reke_to_health_ui.can_use():
            self.set_tip_text("冷却中!!!")
            return
        self.reke_power-=1
        self.reke_to_health_ui.use()
        self.health=min(self.health+20,self.max_health)
        self.smoke.use()
    def use_big_reke(self): #使用大锐克
        if self.reke_power<3:
            self.set_tip_text("锐克电量不足!!! 大招需要3格电量")
            return
        if not self.big_reke_ui.can_use():
            self.set_tip_text("攻击冷却中!!!")
            return
        self.big_reke_ui.use()
        def spawn_missile(angle):
            def _spawn():
                misile=CigaretteAttack(self.get_position(),angle,self.reke_version)
                self.scene.self_misiles.append(misile)
            return _spawn
        angle=0
        self.reke_power-=3
        for i in range(8):
            timerEffect=Effect(None,60*i)
            timerEffect.attach_on_finish_functions.append(spawn_missile(angle))
            angle+=math.pi/4
    def handle_moving(self,x,y): 
        if x<0:
            self.body.direction=-1
            self.direction=-1
            self.body.state=2
            self.cigarette.direction=-1
        elif x>0:
            self.body.direction=1
            self.direction=1
            self.body.state=2
            self.cigarette.direction=1
        else:
            self.body.state=1
        if self.chain!=None and self.chain.visible:
            if self.actor.colliderect(self.chain) and x>0:
                x=0
        pos_x,pos_y=self.get_position()
        pos_x+=x*self.moving_speed
        pos_y+=y*self.moving_speed
        #constrain pos_x between 0 and screen.width
        if pos_x<0:
            pos_x=0
        if pos_x>screen.width:
            pos_x=screen.width
        #constrain pos_y between 0 and screen.height
        if pos_y<2:
            pos_y=2
        if x_left_door != None and x<0:
            if pos_x<x_left_door.x:
                pos_x=x_left_door.x
        if pos_y>screen.height-2:
            pos_y=screen.height-2
        self.set_position((pos_x,pos_y))
            
    def draw(self):
        self.body.draw()
        self.actor.draw() 
        bar_zise=(300,30)
        draw_health_bar(max(self.health,0),self.max_health,(0,0),bar_zise,tips="生命值")
        draw_health_bar(self.reke_power,self.reke_max_power,(assets.screen_width-310,0),bar_zise,tips="锐克电量")
        text=f"速度：{padding(f"{self.moving_speed:.1f}")}"
        draw_text(text,(0,40))
        t2=f"武器：锐克{self.reke_version}代"
        draw_text(t2,(0,60))
        t3=f"第{padding(level_count)}关"
        draw_text(t3,(400,0))

        # draw_health_bar(self.attack_cd_counter,self.attack_cd,(assets.screen_width-310,35),vector_y_offset(bar_zise,-10),tips="攻击冷却")
        self.normal_attack_ui.draw()
        self.big_reke_ui.draw()
        self.reke_to_health_ui.draw()

        if self.tip_text_timer>0:
            draw_text(self.tip_text,(0,assets.screen_height-30),color="red")
        if assets.debug:
            left=self.actor.x-self.actor.width/2
            top=self.actor.y-self.actor.height/2
            main_actor_rect = Rect((left,top), (self.actor.width, self.actor.height))  

            screen.draw.rect(main_actor_rect, "red")
        if self.smoke.cd>0:
            self.cigarette.draw()
        
    def tick(self):
        self.body.tick()
        if self.cry_value>0 or self.isLosed:
            self.actor._surf=self.dz_cry
            self.cry_value-=0.5
        else:
            self.actor._surf=self.dz_normal
        # if self.attack_cd_counter>0:
        #     self.attack_cd_counter-=assets.elapsed_time_frame
        # elif self.attack_cd_counter<0:
        #     self.attack_cd_counter=0
        
        if self.tip_text_timer>0:
            self.tip_text_timer-=assets.elapsed_time_frame
    def clear(self): #清除
        CDableAttackUI.reset()
        reset_global_variables()
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
        self.actor=get_empty_actor()
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
        self.timer+=assets.elapsed_time_frame
        if self.timer>100:
            self.timer=0
            self.count=(self.count+1)%8
    def draw(self):
        self.actor.draw()

class Cigarette:
    def __init__(self):
        self.actor_right=get_empty_actor()
        img_size=(50,50)
        self.img_size=img_size
        self.direction=1 #1:right -1:left
        self.right=load_png_with_scale("cigarette",img_size)
        self.left=pygame.transform.flip(self.right,True,False)
        self.actor_right._surf=self.right
        scale(self.actor_right,*img_size)
        self.actor_right.anchor=(-5,0)
        self.actor_left=get_empty_actor()
        self.actor_left._surf=self.left
        scale(self.actor_left,*img_size)
        self.actor_left.anchor=(img_size[1]+5,0)
        self.visible=True
    def set_position(self,position): #设置位置
        self.actor_right.pos=position
        self.actor_left.pos=position
    def draw(self):
        if not self.visible:
            return
        if self.direction==1:
            self.actor_right.draw()
        else:
            self.actor_left.draw()

class Scene:
    def __init__(self,width,height,mainActor:MainActor):
        global sceneInstance
        self.width=width
        self.height=height
        self.mainActor=mainActor
        tips=TextActor("按下[1]使用锐克攻击(消耗1格电)\n按下[2]使用大招(消耗3格电)\n按下[3]抽锐克恢复生命值(消耗一格电)\n\n道具[尼古丁]可以升级锐克等级提升攻击伤害\n道具[电池]可以恢复锐克电量\n\n向右移动以开始>>>", 30, color="red")
        tips.pos=(width/2,height/2-30)

        tips2=TextActor("你可以先尝试一下各种技能\n充电器可以给锐克充电->",fontsize=30,color="brown")
        tips2.pos=(width/2,height*3/4+20)

        charger=RecoveryUnlimited()
        charger.pos=(width*3/4,height*3/4)

        self.doors=[] #门 
        self.elements=[tips,tips2] #场景静态元素
        self.actors=[] #场景动态元素
        self.tools=[charger] #道具
        self.self_misiles=[] #自身子弹
        self.enemy_misiles=[] #敌人子弹
        self.lists=[self.doors,self.elements,self.actors,self.tools,self.self_misiles,self.enemy_misiles]
        self.background=rectangle_actor(width,height,(255,255,255))
        self.deltaXCount=0
        self.generate_level()
        sceneInstance=self
        self.boss_supply_battery=None
        self.boss=None
    def is_boss(self):
        if self.boss==None:
            return False
        if not self.boss.visible:
            return False
        return level_count>2 and level_count%10==0
    def delta_x(self,delta): 
        self.deltaXCount+=-delta
        for list in self.lists:
            for element in list:
                element.x+=delta
        # self.background.x+=delta

        #gc
        thershold=-self.width*1.5
        for list in self.lists:
            clear_list=[]
            for i in range(len(list)):
                obj=list[i]
                if obj.x<thershold or ("visible" in obj.__dict__ and not obj.visible):
                    clear_list.append(i)
            for i in reversed(clear_list):
                list.pop(i)
                pass
    def tick(self): 
        if self.deltaXCount>=self.width:
            self.deltaXCount-=self.width
            self.generate_level()
        for enemy in self.actors:
            enemy.attr.tick()
        if self.is_boss() and self.mainActor.reke_power<1 and (self.boss_supply_battery==None or self.boss_supply_battery.isUsed):
            self.boss_supply_battery=self.spawn_battery()
            self.boss_supply_battery.x=random.uniform(0,self.boss.attr.bind_door.x)
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
    def spawn_battery(self):
        battery=Battery()
        battery.pos=self.get_random_point()
        self.tools.append(battery)
        return battery
    def spawn_nicotine(self):
        nicotine=Nicotine()
        nicotine.pos=self.get_random_point()
        self.tools.append(nicotine)
        return nicotine
    def spawn_poizon(self):
        poizon=Poizon()
        poizon.pos=self.get_random_point()
        self.tools.append(poizon)
    def spawn_gift(self):
        gift=Gift()
        gift.pos=self.get_random_point()
        self.tools.append(gift)
    def generate_level(self):
        real_level_count=level_count+1
        x_offset=self.deltaXCount+self.width
        door1=rectangle_actor(10,self.height/2,(255,255,0))
        door1.pos=(x_offset,self.height/4)
        self.doors.append(door1)
        door2=rectangle_actor(10,self.height/2,(255,0,255))
        door2.pos=(x_offset,self.height*3/4)
        self.doors.append(door2)
        door1.attr=get_random_door()(door1)
        door2.attr=get_random_door()(door2)
        door1.attr.other=door2.attr
        door2.attr.other=door1.attr

        if random.random()<0.5:
            self.spawn_battery()
        if random.random()<0.5:
            self.spawn_nicotine()
        if random.random()<0.5:
            self.spawn_poizon()
        if random.random()<0.5:
            self.spawn_gift()
        if real_level_count>2 and real_level_count%10==0:
            #boss
            chain=EnhancedActor("chain")
            chain.pos=(x_offset+self.width-50,assets.screen_height/2)
            self.elements.append(chain)
            self.mainActor.chain=chain

            cat_ememy=GifActor("cat",(200,200))
            cat_ememy.pos=self.get_random_point()
            cat_ememy.attr=CatEnemy(cat_ememy,self.mainActor,door1,self.width)
            cat_ememy.attr.tips="大耄耋"
            cat_ememy.attr.bind_door=chain 
            cat_ememy.attr.moving_speed=4.4
            cat_ememy.attr.max_health=250
            cat_ememy.attr.health=250
            self.boss=cat_ememy
            self.actors.append(cat_ememy)



            self.spawn_battery()
            self.spawn_battery()

        else:
            for i in range(10):
                environment=RandomEnvironment()
                environment.pos=self.get_random_point_environment(updown=i<5)
                self.elements.append(environment)

            for i in range(mapping.enemy_count_level_index(real_level_count)):
                cat_ememy=GifActor("cat",(100,100))
                cat_ememy.pos=self.get_random_point()
                cat_ememy.attr=CatEnemy(cat_ememy,self.mainActor,door1,self.width)
                self.actors.append(cat_ememy)
        
        explosiveCat=ExplosiveCatEnemy.create(self.mainActor,door1,self.width)
        explosiveCat.pos=self.get_random_point()
        self.actors.append(explosiveCat)

        slime=SlimeEnemy.create(self.mainActor,door1,self.width)
        slime.pos=self.get_random_point()
        self.actors.append(slime)

        if random.random()<0.5:
            catapult=EnemyCatapult.create(self.mainActor,door1,self.width)
            catapult.pos=self.get_random_point()
            self.actors.append(catapult)
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
        for misile in self.self_misiles:
            misile.draw()
        for misile in self.enemy_misiles:
            misile.draw()

sceneInstance:Scene

class Door:
    def __init__(self,bind:Actor,other=None):
        self.actor=bind
        self.isUsed=False
        self.tips="default"
        self.color="red"
        self.other=None
    def on_enter(self,mainActor:MainActor):
        global level_count
        global x_left_door
        if self.isUsed:
            return
        if self.other is not None:
            self.other.isUsed=True
        x_left_door=self.actor
        self.isUsed=True
        self.onUse(mainActor)
        level_count+=1
    def onUse(self,mainActor:MainActor):
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
        mainActor.moving_speed+=0.6

class RecoverRekePowerDoor(Door): #增加锐克电量
    def __init__(self,bind:Actor):
        super().__init__(bind)
        self.tips="恢复锐克电量"
    def on_enter(self,mainActor:MainActor):
        if self.isUsed:
            return
        super().on_enter(mainActor)
        mainActor.reke_power=min(mainActor.reke_max_power,mainActor.reke_power+2)

class MaxHealthIncreaseDoor(Door):
    def __init__(self,bind:Actor):
        super().__init__(bind)
        self.tips="增加最大生命值"
    def on_enter(self,mainActor:MainActor):
        if self.isUsed:
            return
        super().on_enter(mainActor)
        mainActor.max_health+=15
        mainActor.health=(mainActor.max_health+mainActor.health)/2
        mainActor.set_tip_text("最大生命值增加15")

class MaxRekePowerIncreaseDoor(Door): #增加速度
    def __init__(self,bind:Actor):
        super().__init__(bind)
        self.tips="增加锐克最大电量"
    def on_enter(self,mainActor:MainActor):
        if self.isUsed:
            return
        super().on_enter(mainActor)
        mainActor.reke_max_power+=1
        mainActor.reke_power=math.floor((mainActor.reke_max_power+mainActor.reke_power)/2)
        mainActor.set_tip_text("锐克最大电量增加")

class RecoverRekePowerDoor(Door):
    def __init__(self,bind:Actor):
        super().__init__(bind)
        self.tips="缓慢回血"
    def on_enter(self,mainActor:MainActor):
        if self.isUsed:
            return
        super().on_enter(mainActor)
        SlowRecoverEffect(mainActor,)

class RekeUpgradeDoor(Door):
    def __init__(self,bind:Actor):
        super().__init__(bind)
        self.tips="升级锐克"
    def on_enter(self,mainActor:MainActor):
        if self.isUsed:
            return
        super().on_enter(mainActor)
        mainActor.reke_version+=1
        mainActor.set_tip_text(f"锐克升级到{mainActor.reke_version}代")

doors=[
    HealthIncreaseDoor, 
    SpeedIncreaseDoor,
    RecoverRekePowerDoor,
    MaxHealthIncreaseDoor,
    MaxRekePowerIncreaseDoor,
    RecoverRekePowerDoor,
    RekeUpgradeDoor,
    ]
def get_random_door(): #随机生成一个门
    return random.choice(doors)

class EnemyData: 
    def __init__(self,bind:GifActor,mainActor:MainActor,door:Door,x_range_lim,bind_door:EnhancedActor=None,useClockwise=False):
        self.actor=bind
        self.mainActor=mainActor
        self.tips="default"
        self.health=100
        self.max_health=100
        self.moving_speed=3
        self.door=door
        self.x_range_lim=x_range_lim
        self.cd=0 #milliseconds
        self.cd_duaration=400
        self.text_y_offset=-35
        self.bind_door=bind_door
        self.isMovingRight=True
        self.extraActors=[]
        self.useClockwise=useClockwise
        self.clockwiseSpeed=3
        if useClockwise:
            self.clockwiseDirection=random.random()<0.5
    def set_max_health(self,level_count): #设置最大生命值
        max_health=mapping.enemy_health_level_index(level_count)
        self.max_health=max_health
        self.health=max_health
    def onDeath(self): #死亡
        pass
    def attacked(self,damage): #被攻击
        self.health-=damage
        if self.health<=0:
            self.actor.visible=False
            self.onDeath()
            for i in self.extraActors:
                i.visible=False
            if self.bind_door!=None:
                explode=EnhancedActor("explode")
                scale(explode,150,150)
                explode.pos=self.bind_door.pos
                sceneInstance.elements.append(explode)
                effect=ExplosionEffect(explode,)
                effect.attach_on_finish_functions.append(self._make_bind_door_invisible)
    def _make_bind_door_invisible(self): 
        self.bind_door.visible=False
    def set_cd(self):
        self.cd=self.cd_duaration
    def tick(self):
        if not self.actor.visible:
            return
        if self.cd>0:
            self.cd-=assets.elapsed_time_frame
            return
        
        x_direction,y_direction=get_vector(self.actor.pos,self.mainActor.actor.pos)
        if x_direction>0:
            self.isMovingRight=True
        elif x_direction<0:
            self.isMovingRight=False
        x_direction,y_direction=normalize(x_direction,y_direction)
        self.actor.x+=x_direction*self.moving_speed
        self.actor.y+=y_direction*self.moving_speed
        left_lim=self.door.x
        right_lim=self.door.x+self.x_range_lim
        
        if self.useClockwise:
            dx,dy=mapping.get_vertical_vector(x_direction,y_direction,self.clockwiseDirection)
            dx*=self.clockwiseSpeed
            dy*=self.clockwiseSpeed

            self.actor.x+=dx
            self.actor.y+=dy

        self.actor.x=max(left_lim,self.actor.x)
        self.actor.x=min(right_lim,self.actor.x)
        self.logic_tick()
    def logic_tick(self): #逻辑tick
        pass
    def draw(self):
        if self.actor.visible:
            screen.draw.text(
                self.tips, 
                center=vector_y_offset(self.actor.pos,self.text_y_offset-15),
                color="black",
                fontsize=20,
                fontname='ys', )
            draw_health_bar(self.health,self.max_health,vector_y_offset(self.actor.pos,self.text_y_offset),(100,10),x_center_flag=True) #绘制血条
            if assets.debug:
                left=self.actor.x-self.actor.width/2
                top=self.actor.y-self.actor.height/2
                main_actor_rect = Rect((left,top), (self.actor.width, self.actor.height))
                screen.draw.rect(main_actor_rect, "red")
            for i in self.extraActors:
                i.draw()
            self.draw_extra()
    def draw_extra(self):
        pass



class CatEnemy(EnemyData): 
    def __init__(self,bind:GifActor,mainActor:MainActor,door:Door,x_range_lim):
        super().__init__(bind,mainActor,door,x_range_lim,useClockwise=True)
        self.tips="普通耄耋"
        scale_without_img(self.actor,0.6)
        
    def tick(self):
        super().tick()
        if not self.actor.visible:
            return
        if self.cd>0:
            self.actor.range=(0,4)
            return
        else:
            self.actor.range=(3,7)
        if self.actor.colliderect(self.mainActor.actor):
            self.mainActor.be_attacked(10)
            self.set_cd()
            
class ExplosiveCatEnemy(EnemyData):
    def __init__(self,bind:GifActor,mainActor:MainActor,door:Door,x_range_lim):
        super().__init__(bind,mainActor,door,x_range_lim)
        self.tips="爆炸耄耋"
        scale_without_img(self.actor,0.8) 
        self.max_health=50
        self.health=50
        self.moving_speed=1
        self.text_y_offset=-55
    def tick(self):
        super().tick()
        if not self.actor.visible:
            return
        if self.cd>0:
            return
        self.actor.flip_state=self.isMovingRight
        if self.actor.colliderect(self.mainActor.actor):
            self.attacked(self.max_health)
            entity=ExplodeAttack(3,self.actor.pos)
            sceneInstance.enemy_misiles.append(entity)
            self.set_cd()
    @staticmethod
    def create(mainActor:MainActor,door:Door,x_range_lim):
        # bind=EnhancedActor("cat-3")
        bind=GifActor("cat-3",(100,100))
        scale(bind,100,100)
        attr= ExplosiveCatEnemy(bind,mainActor,door,x_range_lim)
        bind.attr=attr
        return bind

class SlimeEnemy(EnemyData):
    def __init__(self,bind:GifActor,mainActor:MainActor,door:Door,x_range_lim):
        super().__init__(bind,mainActor,door,x_range_lim)
        self.tips="史莱姆"
        self.moving_speed=1.5
        scale_without_img(self.actor,0.5)
        # ResizeEffect(self.actor,150,150,100,100)
    @override
    def logic_tick(self):
        if self.actor.colliderect(self.mainActor.actor):
            self.mainActor.be_attacked(5)
            self.cd=200
            d_x=self.mainActor.get_position()[0]-self.actor.pos[0]
            d_y=self.mainActor.get_position()[1]-self.actor.pos[1]
            d_x,d_y=normalize(d_x,d_y)
            RepelEffect(self.mainActor,(d_x,d_y),isShowText=True)
            self.set_cd()
    @staticmethod
    def create(mainActor:MainActor,door:Door,x_range_lim):
        bind=GifActor("slime")
        scale(bind,100,100)
        attr= SlimeEnemy(bind,mainActor,door,x_range_lim)
        bind.attr=attr
        return bind

class Boss(EnemyData):
    pass

class EnemyCatapult(EnemyData):
    def __init__(self,bind:GifActor,mainActor:MainActor,door:Door,x_range_lim):
        super().__init__(bind,mainActor,door,x_range_lim)
        self.tips="炮台"
        self.moving_speed=0
        scale_without_img(self.actor,0.5)
        self.cd_duaration=2000
        self.actor.canMove=False
        # bullet=EnhancedActor("bullet")
        # scale_ratio(bullet,0.4)
        # self.extraActors.append(bullet)
    @override
    def tick(self):
        super().tick()
        if not self.actor.visible:
            return
        for i in self.extraActors:
            i.pos=self.actor.pos
        
        d_x=self.mainActor.get_position()[0]-self.actor.pos[0]
        d_y=self.mainActor.get_position()[1]-self.actor.pos[1]
        angle=mapping.get_angle(d_x,-d_y)-90
        for i in self.extraActors:
            i.angle=angle
        self.actor.angle=angle
        
    @override
    def logic_tick(self):
        #fire bullet
        bullet=BulletAttack(self.actor.pos,self.actor.angle,)
        sceneInstance.enemy_misiles.append(bullet)
        self.set_cd()
    @staticmethod
    def create(mainActor:MainActor,door:Door,x_range_lim):
        bind=EnhancedActor("catapult")
        scale(bind,100,100)
        attr= EnemyCatapult(bind,mainActor,door,x_range_lim)
        bind.attr=attr
        return bind   
    @override
    def onDeath(self):
        explode=EnhancedActor("explode")
        scale(explode,150,150)
        explode.pos=self.actor.pos
        ExplosionEffect(explode,time=200,strength=0.5)
        sceneInstance.elements.append(explode)

class Tool(Actor):
    def __init__(self,image):
        super().__init__(image)
        scale(self,50,50)
        self.tips="default"
        self.isUsed=False
        self.once=True
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
            if self.once:
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

class RecoveryUnlimited(Tool):
    def __init__(self):
        super().__init__("ligntning")
        self.tips="充电器"
        self.once=False
    @override
    def onUse(self,mainActor:MainActor):
        mainActor.reke_power=mainActor.reke_max_power
        for cd in mainActor.CDs:
            cd.cd=0
        mainActor.set_tip_text("你的锐克电量恢复了！")


class Poizon(Tool):
    def __init__(self):
        super().__init__("poizon")
        self.tips="毒"
    def onUse(self,mainActor:MainActor):
        PoisonEffect(mainActor)

class Gift(Tool):
    def __init__(self):
        super().__init__("gift")
        self.tips="随机礼物"
    def onUse(self,mainActor:MainActor):
        door:Door=get_random_door()(mainActor)
        door.onUse(mainActor)