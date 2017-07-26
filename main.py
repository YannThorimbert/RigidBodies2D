"""2D simulation of rigid bodies represented by arbitrary meshes, using PyGame
for drawing and vector calculus.

(c) 2017 Yann Thorimbert
"""
from __future__ import print_function, division
import pygame
from pygame.math import Vector2 as V2
import pygame.gfxdraw as gfx

import physics
import parameters #all physical quantities are defined here

def draw_meshes():
    for m in meshes:
        m.draw()

def refresh_physics():
    for m in meshes:
        m.refresh_physics()

W, H = 500, 500 #size of the domain (and size of screen)

m1 = physics.get_polygon(3, 20) #get n-polygon of 'radius' 20
m2 = physics.get_polygon(3, 20)
m1.move((250,250))
m1.rotate(180)
m2.set_pos(m1.cm + (0,-120)) #.cm denotes the center of mass

m3 = physics.get_polygon(4,200)
m3.rotate(45)
m3.set_pos((W//2,H//2))
m3.normal = -1. #invert normals
m3.fixed = True #object never moves

m4 = physics.get_polygon(3,20)
m4.set_pos(m1.cm+(40,0))
m5 = physics.get_polygon(3,20)
m5.set_pos(m1.cm-(40,0))

meshes = [m1,m2,m3,m4,m5]

##m1.ang_velocity = 1.
##m1.velocity = V2(0., 5.)

# ##############################################################################
screen = pygame.display.set_mode((W,H))
parameters.screen = screen #used as global variable inside physics.py
iteration = 0
loop = True
parameters.clock = pygame.time.Clock()
SHOWITER = 10
while loop:
    if iteration%SHOWITER == 0:
        screen.fill((255,255,255))
    physics.add_forces(meshes)
    refresh_physics()
##    for m in meshes:
##        m.draw_normals()
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            loop = False
    if iteration%SHOWITER == 0:
        draw_meshes()
        pygame.display.flip()
    iteration += 1

pygame.quit()
