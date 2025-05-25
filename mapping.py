import math

def reke_version_repel_strength(reke_version):
    return 300+100*math.log(reke_version)

def reke_version_damage(reke_version):
    return 50+10*math.log(reke_version)

def reke_version_cigarette_damage(reke_version):
    return 50+10*math.log(reke_version)

def rad_to_deg(rad):
    return rad*180/math.pi

def enemy_count_level_index(levelIndex:int):
    return max(1,math.floor(math.log(levelIndex,1.6)))