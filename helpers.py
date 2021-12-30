import pygame

def invert(value):
    if value == "right":
        return "left"
    else:
        return "right"

def collide(obj1, obj2):
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (int(offset_x), int(offset_y))) != None