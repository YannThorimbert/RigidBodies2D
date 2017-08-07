from __future__ import print_function, division
import math
import thorpy, pygame
from pygame.math import Vector2 as V2
import pygame.gfxdraw as gfx
import random

W, H = 300, 600
DT = 10.e-3
COLL_TOL = 1
TOL_DEL = COLL_TOL
SPRING_CONSTANT = 1000.
MIND_D = 1
MAX_FORCE_INTENSITY = SPRING_CONSTANT*(MIND_D-COLL_TOL)
GRAVITY = V2(0, 9.81)
FRICTION_COEFF = -0.5e-2

COLORS = [(0,)*3, (127,)*3, (255,0,0), (0,255,0), (0,0,255), (255,0,255)]

def sgn(x):
    if x > 0:
        return 1.
    elif x < 0:
        return -1.
    return 0.



class Sphere2D:

    def __init__(self, radius, x, y):
        self.radius = radius
        self.cm = V2(x,y)
        self.angle = 0.
        self.tang_force = 0.
        self.normal_force = V2()
        self.velocity = V2() #in pix/s
        self.ang_velocity = 0. #in 1/s
        self.mass = 1.
        self.moment_of_inertia = 1.e-6
        self.fixed = False
        self.color = random.choice(COLORS)

    def apply_force(self, point, force):
        r = point - self.cm
        unit_to_cm = r.normalize()
        self.normal_force += force
        self.tang_force += -force.cross(unit_to_cm) * r.length()

    def refresh_translation(self):
        a = self.normal_force/self.mass
        self.velocity += a*DT
        self.move(self.velocity*DT)

    def refresh_rotation(self):
        a = self.tang_force/self.moment_of_inertia
        self.ang_velocity += a*DT
        self.angle += self.ang_velocity*DT*360.

    def refresh_physics(self):
        if not self.fixed:
            self.refresh_translation()
            self.refresh_rotation()
            self.clear_forces()

    def clear_forces(self):
        self.normal_force = V2()
        self.tang_forces = 0.


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

    def set_pos(self, pos):
        delta = pos - self.cm
        self.move(delta)

    def get_velocity(self, index): #p or angle?
        r = self.points[index] - self.cm
        rnorm = r.length()
        tanvel = r.normalize().rotate(sgn(self.ang_velocity)*90.)
        return self.velocity + self.ang_velocity*rnorm*tanvel#*2*pi

    def get_energy(self):
        return self.mass*(0.5*self.velocity.length()**2 + GRAVITY.y*(H-self.cm.y)) +\
                0.5*self.moment_of_inertia*self.ang_velocity**2

    def collide_spring_wall(self, wallcoord):
        delta = wallcoord - self.cm
        distance = delta.length()
        if distance <= self.radius + COLL_TOL: #+ margin
            d = distance - self.radius
            force_intensity = SPRING_CONSTANT*(d-COLL_TOL)
            normal_to_wall = delta.normalize()
            contact_point = self.cm + normal_to_wall*self.radius
            force = force_intensity * normal_to_wall
            self.apply_force(contact_point, V2(force))

    def is_in_collision(self, others):
        for other in others:
            delta = self.cm - other.cm
            rsum = self.radius + other.radius
            distance = delta.length()
            if distance <= rsum + COLL_TOL:
                return True
        return False

    def collide_spring(self, other):
        delta = self.cm - other.cm
        rsum = self.radius + other.radius
        distance = delta.length()
        if distance <= rsum + COLL_TOL:
            d = distance - rsum
            force_intensity = -SPRING_CONSTANT*(d-COLL_TOL)
            #
##            SPRING_CONSTANT = 2e-1
##            force_intensity = -SPRING_CONSTANT*(d-COLL_TOL)**7
            normal_to_wall = delta.normalize()
            contact_point = self.cm + normal_to_wall*self.radius
            force = force_intensity * normal_to_wall
            self.normal_force += force


def draw_meshes():
    for m in meshes:
        m.draw()

def add_forces():
    for im1,m in enumerate(meshes):
        #special collision with ground
        m.collide_spring_wall((m.cm.x,H))
        m.collide_spring_wall((0,m.cm.y))
        m.collide_spring_wall((W,m.cm.y))
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


app = thorpy.Application((W,H))

##m1 = Sphere2D(30, W//2, H//2)
##m2 = Sphere2D(30, W//2+40, H//2-100)
##meshes = [m1,m2]
R = 20
##meshes = [ for i in range(20)]
meshes = []
for i in range(50):
    m = Sphere2D(R, random.randint(R+1,W-R-1), random.randint(R+1,H))
    while m.is_in_collision(meshes):
        m.set_pos((random.randint(R+1,W-R-1), random.randint(R+1,H)))
    meshes.append(m)

screen = app.get_screen()
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

app.quit()

#a optimiser pour jeuxvideos
    # boucle collision /2
    # pas de vitesse angulaire ==> plein de simplifications
    # positions arrondies sur une grille pour dÃ©tection de collisions