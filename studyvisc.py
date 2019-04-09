from __future__ import print_function, division
import math, sys
import pygame
from pygame.math import Vector2 as V2
import pygame.gfxdraw as gfx
import random

import os
os.environ['SDL_VIDEO_CENTERED'] = '1'

#Kausch : circle packing = 0.907; random circle packing = 0.82

W, H = 400, 400
DT = 10.e-3
COLL_TOL = 1
TOL_DEL = COLL_TOL
SPRING_CONSTANT = 1000.
MIND_D = 1
MAX_FORCE_INTENSITY = SPRING_CONSTANT*(MIND_D-COLL_TOL)

Won2 = W / 2.



COLORS = [(0,)*3, (127,)*3, (255,0,0), (0,255,0), (0,0,255), (255,0,255)]
#COLORS = [(0,0,255)]

DRAW_ID = False

def sgn(x):
    if x > 0:
        return 1.
    elif x < 0:
        return -1.
    return 0.


def periodic_delta(c1, c2):
    """points from c1 to c2"""
    delta = c1 - c2
    dx = abs(delta.x)
    if dx > Won2: #dx + k = w ==> k=w - dx
        # print("Uh ! ", dx,dy)
        dx = W - dx
        if c2[0] > c1[0]:
            delta = V2(dx,delta.y)
        else:
            delta = V2(-dx,delta.y)
        return delta
    return delta

class Sphere2D:
    id_ = 0
    def __init__(self, radius, x, y):
        self.radius = radius
        self.cm = V2(x,y)
        self.angle = 0.
        # self.tang_force = 0.
        self.normal_force = V2()
        self.velocity = V2() #in pix/s
        self.ang_velocity = 0. #in 1/s
        self.mass = 1.
        self.moment_of_inertia = 1.e-6
        self.fixed = False
        self.color = random.choice(COLORS)
        self.id = Sphere2D.id_
        Sphere2D.id_ += 1

    def apply_force(self, point, force):
        r = point - self.cm
        unit_to_cm = r.normalize()
        self.normal_force += force
        # self.tang_force += -force.cross(unit_to_cm) * r.length()

    def refresh_translation(self):
        a = self.normal_force/self.mass
        self.velocity += a*DT
        self.move(self.velocity*DT)

    # def refresh_rotation(self):
    #     a = self.tang_force/self.moment_of_inertia
    #     self.ang_velocity += a*DT
    #     self.angle += self.ang_velocity*DT*360.

    def refresh_physics(self):
        if not self.fixed:
            self.refresh_translation()
            # self.refresh_rotation()
            self.clear_forces()

    def clear_forces(self):
        self.normal_force = V2()
        # self.tang_forces = 0.


    def draw(self, color=None):
        if DRAW_ID:
            label = myfont.render(str(self.id), 1, (0,0,0))
            screen.blit(label, (int(self.cm.x), int(self.cm.y)))
        color = self.color if color is None else color
        gfx.aacircle(screen, int(self.cm.x), int(self.cm.y), self.radius, color)
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


    def set_pos(self, pos):
        delta = pos - self.cm
        self.move(delta)

    def get_velocity(self, index): #p or angle?
        r = self.points[index] - self.cm
        rnorm = r.length()
        tanvel = r.normalize().rotate(sgn(self.ang_velocity)*90.)
        return self.velocity + self.ang_velocity*rnorm*tanvel#*2*pi

    def get_energy(self):
        return self.mass*0.5*self.velocity.length()**2

    def collide_spring_wall(self, wallcoord):
        delta = wallcoord - self.cm
        distance = delta.length()
        if distance <= self.radius + COLL_TOL: #+ margin
            d = distance - self.radius
            force_intensity = SPRING_CONSTANT*(d-COLL_TOL)
            normal_to_wall = delta.normalize()
            # if wallcoord[1] < self.cm.y:
            #     normal_to_wall = V2(0,-1)
            # else:
            #     normal_to_wall = V2(0,1)
            contact_point = self.cm + normal_to_wall*self.radius
            force = force_intensity * normal_to_wall
            self.apply_force(contact_point, V2(force))
            self.velocity *= COLL_FRICTION

    def is_in_collision(self, others):
        for other in others:
            rsum = self.radius + other.radius
            delta = periodic_delta(self.cm, other.cm)
            distance = delta.length()
            if distance <= rsum + COLL_TOL:
                return True
        return False

    def collide_spring(self, other):
        rsum = self.radius + other.radius
        delta = periodic_delta(self.cm, other.cm)
        distance = delta.length()
        if distance <= rsum + COLL_TOL:
            gap = distance - rsum
            force_intensity = -SPRING_CONSTANT*(gap-COLL_TOL)
            if distance != 0:
                normal_to_wall = delta.normalize()
            else:
                normal_to_wall = V2(random.random(),random.random()).normalize()
            force = force_intensity * normal_to_wall
            self.normal_force += force
            self.velocity *= COLL_FRICTION
            return 1
                        #
            ##            SPRING_CONSTANT = 2e-1
            ##            force_intensity = -SPRING_CONSTANT*(d-COLL_TOL)**7
        return 0

    # def get_forced_clone(self):
    #     return ForcedSphere2D(self.radius, self.x, self.y)

    def set_forced(self):
        self.apply_force = self.apply_force_null
        self.collide_spring = self.collide_spring_null
        self.refresh_translation = self.refresh_translation_null
        self.collide_spring_wall = self.collide_spring_wall_null

    def apply_force_null(self, point, force):
        pass
    def collide_spring_null(self, other):
        rsum = self.radius + other.radius
        delta = periodic_delta(self.cm, other.cm)
        distance = delta.length()
        if distance <= rsum + COLL_TOL:
            return 1
        return 0
    def refresh_translation_null(self):
        self.move(self.velocity*DT)
    def collide_spring_wall_null(self, wallcoord):
        pass



class CollisionGrid:

    def __init__(self, nx, ny):
        self.nx = nx
        self.ny = ny
        self.meshes = None
        self.factorX = float(nx) / W
        self.factorY = float(ny) / H
        self.ncollisions = 0

    def coord2grid(self, coord):
        x, y = int(self.factorX*coord[0]), int(self.factorY*coord[1])
        if x < 0: x = self.nx - 1 #periodicity left
        if x >= self.nx: x = 0 #periodicity right
        if y < 0: y = 0
        if y >= self.ny: y = self.ny-1
        return x, y
        # return int(factorX*coord[0]), int(factorY*coord[1])

    def add_mesh(self, mesh):
        x,y = self.coord2grid(mesh.cm)
        self.meshes[x][y].append(mesh)

    def rebuild(self, meshes):
        self.ncollisions = 0
        self.meshes = [[list() for i in range(self.ny)] for j in range(self.nx)]
        for m in meshes:
            self.add_mesh(m)

    def collide(self):
        for x in range(self.nx):
            for y in range(self.ny):
                for m in self.meshes[x][y]:
                    #x
                    self.collide_with(m, x, y)
                    self.collide_with(m, x, y-1)
                    self.collide_with(m, x, y+1)
                    #x-1
                    self.collide_with(m, x-1, y)
                    self.collide_with(m, x-1, y-1)
                    self.collide_with(m, x-1,  y+1)
                    #x+1
                    self.collide_with(m, x+1, y)
                    self.collide_with(m, x+1, y-1)
                    self.collide_with(m, x+1, y+1)

    def collide_with(self, mesh, x, y):
        exist = 0 <= y < self.ny
        if not exist:
            return
        if x < 0:
            x = self.nx - 1
        elif x > self.nx - 1:
            x = 0
        for other in self.meshes[x][y]:
            if mesh is not other:
                self.ncollisions += mesh.collide_spring(other)

    def compute_average_u(self):
        u = [[0. for i in range(self.ny)] for j in range(self.nx)]
        for x in range(self.nx):
            for y in range(self.ny):
                for m in self.meshes[x][y]:
                    u[x][y] += m.velocity.x
                N = len(self.meshes[x][y])
                if N > 0:
                    u[x][y] /= N
        return u



def draw_meshes():
    for m in meshes:
        m.draw()

def add_forces(collision_grid,meshes):
    collision_grid.rebuild(meshes)
    collision_grid.collide()
    for im1,m in enumerate(meshes):
        #special collision with walls
        m.collide_spring_wall((m.cm.x,H)) #bottom wall
        m.collide_spring_wall((m.cm.x,0)) #top wall
        # m.collide_spring_wall((0,m.cm.y)) #left wall
        # m.collide_spring_wall((W,m.cm.y)) #right wall
        velnorm = m.velocity.length()
        if velnorm > 0:
            friction = m.velocity.normalize()*velnorm*velnorm*FRICTION_COEFF
            m.normal_force += friction

def refresh_physics(meshes):
    for m in meshes:
        m.refresh_physics()



FRICTION_COEFF = 0.9
COLL_FRICTION = 0.1
def go(seed, nspheres, ulid):
    global FRICTION_COEFF, COLL_FRICTION
    R = 12
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

    ##m1 = Sphere2D(30, W//2, H//2)
    ##m2 = Sphere2D(30, W//2+40, H//2-100)
    ##meshes = [m1,m2]
    print("Wanted number of spheres:",nspheres)

    meshes = []

    BIMODAL_FACTOR = 1.
    #dense initialization: #########################################################
    for i in range(nspheres):
        debug_counter = 0
        radius = random.randint(R, BIMODAL_FACTOR*R)
        m = Sphere2D(radius, random.randint(0,W), random.randint(radius+1,H-radius-1))
        meshes.append(m)


    FRICTION_COEFF = 0.9
    COLL_FRICTION = 0.1

    for m in meshes:
        m.velocity = V2()
        m.clear_forces()
        assert 0 < m.cm[1] < H

    print("Final number of spheres:", len(meshes))
    print("Volume fraction:", sum([math.pi*m.radius**2 for m in meshes]) / (W*H))

    iteration = 0
    loop = True
    clock = pygame.time.Clock()
    SHOWITER = 10
    while loop:
        add_forces(collision_grid,meshes)
        refresh_physics(meshes)
        for m in meshes:
            if not(0 <= m.cm.x <= W) or not(0 <= m.cm.y <= H):
                x = random.randint(0,W)
                y = random.randint(radius+1,H-radius-1)
                m.set_pos(V2(x, y))
        iteration += 1
        if iteration > 400 or collision_grid.ncollisions == 0:
            break

    #true simulation: ##############################################################

    FRICTION_COEFF = 0.
    COLL_FRICTION = 0.999
    VEL_LID = ulid

    for m in meshes:
        assert 0 < m.cm[1] < H
        m.velocity = V2()
        m.clear_forces()
        if m.cm.y < 2*R+5:
            m.velocity.x = VEL_LID
            m.color = (0,255,0)
            m.set_forced()
        elif m.cm.y > H - 2*R+-5:
            m.velocity.x = -VEL_LID
            m.color = (0,255,0)
            m.set_forced()
        else:
            m.color = (0,0,0)


    print("Final number of spheres:", len(meshes))
    phi = sum([math.pi*m.radius**2 for m in meshes]) / (W*H)
    print("Volume fraction:", phi)

    # pygame.time.wait(5000)

    #collision grid just to average vel, no collisions !
    avg_vel = CollisionGrid(1, H//6)

    iteration = 0
    loop = True
    clock = pygame.time.Clock()
    SHOWITER = 10

    stats_u = [0. for i in range(avg_vel.ny)]
    n_avg = 0

    MAXITER = 20000
    AVG_ITER = 100

    while loop:
        if iteration % AVG_ITER == 0 and iteration > 10000:
            avg_vel.rebuild(meshes)
            avg_ux = avg_vel.compute_average_u()[0]
            # print(len(stats_u), len(avg_ux))
            for y,u_x in enumerate(avg_ux):
                stats_u[y] += u_x
                n_avg += 1
            print(iteration, round(sum([m.get_energy() for m in meshes])))
        add_forces(collision_grid,meshes)
        refresh_physics(meshes)
        iteration += 1
        if iteration > MAXITER:
            break

    print("Courbe:")
    avg_ux = [v/n_avg for v in stats_u]

    visc = (avg_ux[8] - avg_ux[len(avg_ux)-1-8]) / len(avg_ux[8:len(avg_ux)-1-8])
    visc *= 1000.
    visc = round(visc,2)
    print("VISC = ", visc)
    return visc


data = []
for ulid in range(40,125,5):
    visc=go(0,300,ulid)
    print(ulid,visc)
    data.append(visc)

print(data)

import matplotlib.pyplot as plt
plt.clf()
plt.plot(data,"o-")
plt.show()
