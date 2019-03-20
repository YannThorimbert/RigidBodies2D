from __future__ import print_function, division
import math
import pygame
from pygame.math import Vector2 as V2
import pygame.gfxdraw as gfx
import random

import os
os.environ['SDL_VIDEO_CENTERED'] = '1'

W, H = 200, 600
DT = 10.e-3
COLL_TOL = 1
TOL_DEL = COLL_TOL
SPRING_CONSTANT = 1000.
MIND_D = 1
MAX_FORCE_INTENSITY = SPRING_CONSTANT*(MIND_D-COLL_TOL)
GRAVITY = V2(0, 0.)
FRICTION_COEFF = -0.5e-2
COLL_FRICTION = 0.9

COLORS = [(0,)*3, (127,)*3, (255,0,0), (0,255,0), (0,0,255), (255,0,255)]


def periodic_distance(c1, c2):
    dx, dy = abs(c2[0]-c1[0]), abs(c2[1]-c1[1])
    if dx > w/2.: #dx + k = w==> k=w - dx
        dx = w - dx
    if dy > h/2.:
        dy = h - dy;
    return math.hypot(dx,dy)



class Sphere2D:

    def __init__(self, radius, x, y):
        self.radius = radius
        self.cm = V2(x,y)
        self.normal_force = V2()
        self.velocity = V2() #in pix/s
        self.mass = 1.
        self.fixed = False
        self.color = random.choice(COLORS)

    def apply_force(self, point, force):
        r = point - self.cm
        unit_to_cm = r.normalize()
        self.normal_force += force

    def refresh_translation(self):
        a = self.normal_force/self.mass
        self.velocity += a*DT
        self.move(self.velocity*DT)

    def refresh_physics(self):
        if not self.fixed:
            self.refresh_translation()
            if self.velocity.length() > 0:
                self.velocity.scale_to_length(1e-3)
            self.clear_forces()

    def clear_forces(self):
        self.normal_force = V2()

    def draw(self):
        gfx.aacircle(screen, int(self.cm.x), int(self.cm.y), self.radius,
                        self.color)
        #draw points
        n = 12
        a = 360./n
        v = V2(self.radius, 0)
##        for i in range(n):
##            pos = v.rotate(i*a + self.angle)
##            gfx.aacircle(screen, int(self.cm.x+pos.x), int(self.cm.y+pos.y),
##                        4, (0,0,0))

    def move(self, delta):
        self.cm += delta #since pure translation (no deformation, no refresh)
        self.cm.x %= W
        self.cm.y %= H

    def set_pos(self, pos):
        delta = pos - self.cm
        self.move(delta)


    def collide_spring(self, other):
        dx, dy = abs(other.cm.x-self.cm.x), abs(other.cm.y-self.cm.y)
        if dx > W/2.: #dx + k = w==> k=w - dx
            dx = W - dx
        if dy > H/2.:
            dy = H - dy;
        distance = math.hypot(dx,dy)
        delta = self.cm - other.cm
        rsum = self.radius + other.radius
        distance = delta.length()
        if distance <= rsum + COLL_TOL:
            d = distance - rsum
            force_intensity = -SPRING_CONSTANT*(d-COLL_TOL)
            normal_to_wall = delta.normalize()
            contact_point = self.cm + normal_to_wall*self.radius
            force = force_intensity * normal_to_wall
            self.normal_force += force
            self.velocity *= COLL_FRICTION


def draw_meshes():
    for m in meshes:
        m.draw()

def add_forces():
    for im1,m in enumerate(meshes):
        #collisions
        for im2,m2 in enumerate(meshes):
            if im1 != im2:
                m.collide_spring(m2)
        #gravity
        m.normal_force += GRAVITY
        velnorm = m.velocity.length()
        if velnorm > 0:
            friction = m.velocity.normalize()*velnorm*velnorm*FRICTION_COEFF
            m.normal_force += friction

def refresh_physics():
    for m in meshes:
        m.refresh_physics()


screen = pygame.display.set_mode((W,H))

R = 20
n = int(0.88*W*H/(math.pi*R*R))
meshes = []
for i in range(n):
    m = Sphere2D(R, R + random.random()*(W-R), R + random.random()*(H-R))
    meshes.append(m)
print(math.pi*n*R*R/(W*H))

screen.fill((255,255,255))
draw_meshes()
pygame.display.flip()
iteration = 0
loop = True
clock = pygame.time.Clock()
SHOWFORCES = False
SHOWITER = 10
while loop:
    if iteration%SHOWITER == 0:
        clock.tick(100)
        screen.fill((255,255,255))
##        if iteration%100 == 0:
##            print(iteration*DT, sum([m.get_energy() for m in meshes]))
    add_forces()
    refresh_physics()
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            loop = False
        elif e.type == pygame.KEYDOWN:
            SHOWFORCES = not(SHOWFORCES)
    if iteration%SHOWITER == 0:
        draw_meshes()
        pygame.display.flip()
    iteration += 1

pygame.quit()
