import pygame
from pgzero.actor import Actor
def scale(actor, new_width, new_height):
    actor._surf=pygame.transform.scale(actor._surf, (new_width, new_height))
    actor.anchor=(new_width/2,new_height/2)
    actor.width=new_width
    actor.height=new_height

def empty_actor(width,height,color=(255,255,255)):
    actor = Actor("placeholder")  
    actor.anchor=(width/2,height/2)
    actor._surf = pygame.Surface((width, height)) 
    actor._surf.fill(color)
    actor.width=width
    actor.height=height
    return actor

class GifActor():
    def __init__(self, gif_path):
        self.actor=Actor(gif_path)
        self.actor.anchor=(self.actor.width/2,self.actor.height/2)
        self.actor._surf=pygame.image.load(gif_path)