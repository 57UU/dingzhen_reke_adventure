import math

def reke_version_repel_strength(reke_version):
    return 300+100*math.log(reke_version)

def reke_version_damage(reke_version):
    return 50+10*math.log(reke_version)