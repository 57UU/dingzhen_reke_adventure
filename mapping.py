import math

def reke_version_repel_strength(reke_version):
    return 300+100*math.log(reke_version)

def reke_version_damage(reke_version):
    return 50+10*math.log(reke_version)

def reke_version_cigarette_damage(reke_version):
    return 50+20*math.log(reke_version)

def rad_to_deg(rad):
    return rad*180/math.pi