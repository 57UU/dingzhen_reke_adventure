import math

def reke_version_repel_strength(reke_version):
    return 300+100*math.log(reke_version,2)

def reke_version_damage(reke_version):
    return 50+10*math.log(reke_version,1.5)

def reke_version_cigarette_damage(reke_version):
    return 50+10*math.log(reke_version,2)

def rad_to_deg(rad):
    return rad*180/math.pi
def deg_to_rad(deg):
    return deg*math.pi/180
def enemy_count_level_index(levelIndex:int):
    return max(1,math.floor(math.log(levelIndex,2)))

def enemy_health_level_index(levelIndex:int):
    return 100+10*max(1,math.floor(math.log(levelIndex)))

def reke_version_to_cigrarette_strength(reke_version):
    return 500+30*reke_version

def get_angle(dx, dy):
    angle_rad = math.atan2(dy, dx)
    return rad_to_deg(angle_rad)
    