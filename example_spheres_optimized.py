from __future__ import print_function, division
import math, sys
import pygame
from pygame.math import Vector2 as V2
import pygame.gfxdraw as gfx
import random

import os
os.environ['SDL_VIDEO_CENTERED'] = '1'

W, H = 1000, 800
DT = 10.e-3
COLL_TOL = 1
TOL_DEL = COLL_TOL
SPRING_CONSTANT = 1000.
MIND_D = 1
MAX_FORCE_INTENSITY = SPRING_CONSTANT*(MIND_D-COLL_TOL)
GRAVITY = V2(0, 9.81)
FRICTION_COEFF = -5e-3
COLL_FRICTION = 0.999



COLORS = [(0,)*3, (127,)*3, (255,0,0), (0,255,0), (0,0,255), (255,0,255)]
#COLORS = [(0,0,255)]

DRAW_ID = False

def sgn(x):
    if x > 0:
        return 1.
    elif x < 0:
        return -1.
    return 0.



class Sphere2D:
    id_ = 0
    def __init__(self, radius, x, y):
        self.radius = radius
        self.cm = V2(x,y)
        self.angle = 0.
        self.normal_force = V2()
        self.velocity = V2() #in pix/s
        self.ang_velocity = 0. #in 1/s
        self.mass = 1.
        self.moment_of_inertia = 1.e-6
        self.fixed = False
        self.color = random.choice(COLORS)
        self.id = Sphere2D.id_
        Sphere2D.id_ += 1


    def refresh_translation(self):
        a = self.normal_force/self.mass
        self.velocity += a*DT
        self.cm += self.velocity*DT


    def refresh_physics(self):
        if not self.fixed:
            self.refresh_translation()
            self.normal_force = V2()

    def draw(self, color=None):
        if DRAW_ID:
            label = myfont.render(str(self.id), 1, (0,0,0))
            screen.blit(label, (int(self.cm.x), int(self.cm.y)))
        color = self.color if color is None else color
        gfx.aacircle(screen, int(self.cm.x), int(self.cm.y), self.radius,
                        color)
        #draw points
        n = 12
        a = 360./n
        v = V2(self.radius, 0)


    def set_pos(self, pos):
        delta = pos - self.cm
        self.cm += delta #since pure translation (no deformation, no refresh)


    def collide_spring_wall(self, wallcoord):
        delta = wallcoord - self.cm
        distance = delta.length()
        if distance <= self.radius + COLL_TOL: #+ margin
            d = distance - self.radius
            force_intensity = SPRING_CONSTANT*(d-COLL_TOL)
            normal_to_wall = delta.normalize()
            self.normal_force += force_intensity * normal_to_wall
            self.velocity *= COLL_FRICTION

    def is_in_collision(self, others):
        for other in others:
            delta = self.cm - other.cm
            rsum = self.radius + other.radius
            distance = delta.length()
            if distance <= rsum + COLL_TOL:
                return True
        return False

    def collide_spring(self, other):
        rsum = self.radius + other.radius
        delta = self.cm - other.cm
        distance = delta.length()
        if distance <= rsum + COLL_TOL:
            d = distance - rsum
            force_intensity = -SPRING_CONSTANT*(d-COLL_TOL)
            normal_to_wall = delta.normalize()
            self.normal_force += force_intensity * normal_to_wall
            self.velocity *= COLL_FRICTION

class CollisionGrid:

    def __init__(self, nx, ny):
        self.nx = nx
        self.ny = ny
        self.meshes = None
        self.factorX = float(nx) / W
        self.factorY = float(ny) / H

    def coord2grid(self, coord):
        x, y = int(self.factorX*coord[0]), int(self.factorY*coord[1])
        if x < 0: x = 0
        if x >= self.nx: x = self.nx-1
        if y < 0: y = 0
        if y >= self.ny: y = self.ny-1
        return x, y
        # return int(factorX*coord[0]), int(factorY*coord[1])

    def add_mesh(self, mesh):
        x,y = self.coord2grid(mesh.cm)
        self.meshes[x][y].append(mesh)

    def rebuild(self, meshes):
        self.meshes = [[list() for i in range(self.ny)] for j in range(self.nx)]
        for m in meshes:
            self.add_mesh(m)

    def collide(self):
        for x in range(self.nx):
            for y in range(self.ny):
                for m1 in self.meshes[x][y]:
                    #x
                    self.collide_with(m1, x, y)
                    self.collide_with(m1, x, y-1)
                    self.collide_with(m1, x, y+1)
                    #x-1
                    self.collide_with(m1, x-1, y)
                    self.collide_with(m1, x-1, y-1)
                    self.collide_with(m1, x-1,  y+1)
                    #x+1
                    self.collide_with(m1, x+1, y)
                    self.collide_with(m1, x+1, y-1)
                    self.collide_with(m1, x+1, y+1)

    def collide_with(self, mesh, x, y):
        exist = 0 <= x < self.nx and 0 <= y < self.ny
        if not exist:
            return
        for other in self.meshes[x][y]:
            if mesh is not other:
                mesh.collide_spring(other)

def draw_meshes():
    for m in meshes:
        m.draw()

def add_forces():
    collision_grid.rebuild(meshes)
    collision_grid.collide()
    for im1,m in enumerate(meshes):
        #special collision with walls
        m.collide_spring_wall((m.cm.x,H)) #bottom wall
        m.collide_spring_wall((0,m.cm.y)) #left wall
        m.collide_spring_wall((W,m.cm.y)) #right wall
        #gravity
        m.normal_force += GRAVITY
        velnorm = m.velocity.length()
        if velnorm > 0:
            friction = m.velocity.normalize()*velnorm*velnorm*FRICTION_COEFF
            m.normal_force += friction

def refresh_physics():
    for m in meshes:
        m.refresh_physics()

R = 8
#be sure that grid_cell_size >= 2*R, with R the maximum Radius !!!!
grid_cell_size = 4*R
nx = int(W/grid_cell_size)
ny = int(H/grid_cell_size)

print("Nx, Ny ", nx, ny)
print("W, H ", W, H)


collision_grid = CollisionGrid(nx,ny)
print(2*R*collision_grid.factorX, ":", R, collision_grid.factorX,collision_grid.nx,W)
assert 2*R*collision_grid.factorX <= 1.
assert 2*R*collision_grid.factorY <= 1.



screen = pygame.display.set_mode((W,H))
pygame.font.init()

myfont = pygame.font.SysFont("monospace", 12)

##m1 = Sphere2D(30, W//2, H//2)
##m2 = Sphere2D(30, W//2+40, H//2-100)
##meshes = [m1,m2]

if len(sys.argv) == 3:
    nspheres = int(sys.argv[1])
    random.seed(int(sys.argv[2]))
elif len(sys.argv) == 2:
    nspheres = int(sys.argv[1])
else:
    nspheres = 100

print("Wanted number of spheres:",nspheres)

meshes = []
#meshes.append(Sphere2D(3*R, W//2, H//2))
hmin = -H//2
for i in range(nspheres):
    debug_counter = 0
    radius = random.randint(R, 2*R)
    m = Sphere2D(radius, random.randint(radius+1,W-radius-1), random.randint(hmin,H-radius-1))
    while m.is_in_collision(meshes):
        m.set_pos((random.randint(radius+1,W-radius-1), random.randint(hmin,H-radius-1)))
        debug_counter += 1
        if debug_counter > 10000:
            print("Couldn't initialize with this domain size and sphere size")
            break
    if debug_counter > 10000:
        break
    meshes.append(m)

print("Final number of spheres:", len(meshes))


screen.fill((255,255,255))
draw_meshes()
pygame.display.flip()
iteration = 0
loop = True
clock = pygame.time.Clock()
SHOWITER = 10
while loop:
    if iteration%SHOWITER == 0:
        clock.tick(100)
        screen.fill((255,255,255))
    add_forces()
    refresh_physics()
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            loop = False
    if iteration%SHOWITER == 0:
        draw_meshes()
        pygame.display.flip()
    iteration += 1

pygame.quit()
