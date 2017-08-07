from __future__ import print_function, division
import math
import pygame
from pygame.math import Vector2 as V2
import pygame.gfxdraw as gfx
import random

from ellipsecalculus import Ellipse2D

W, H = 500, 500
DT = 10.e-3
COLL_TOL = 4
TOL_DEL = COLL_TOL
SPRING_CONSTANT = 500.
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

def rad2deg(x):
    return x*180./math.pi

def deg2rad(x):
    return x*math.pi/180.


class EllipticRigidBody2D(Ellipse2D):

    def __init__(self, a, b, x, y, angle=0.):
        Ellipse2D.__init__(self, a, b, (0,0), 0.)
        self.a = a
        self.a2 = a*a
        self.b = b
        self.b2 = b*b
        self.cm = V2(x,y)
        self.angle = angle
        self.tang_force = 0.
        self.normal_force = V2()
        self.velocity = V2() #in pix/s
        self.ang_velocity = 0. #in 1/s
        self.mass = 1.
        self.moment_of_inertia = 1e5
        self.fixed = False
        self.color = random.choice(COLORS)
        #
        n = 12
        angle = 360./n
        angles = [0., 15., 30., 60., 75]
        self.angles =  angles + [90. + angle for angle in angles] +\
                     [180. + angle for angle in angles] + [270. + angle for angle in angles]
##        self.angles = [i*angle for i in range(n)]
        #
        self.img = pygame.Surface((max([int(2*self.a),int(2*self.b)]),)*2)
        self.img.fill((255,255,255))
        pygame.draw.ellipse(self.img, (0,255,0), pygame.Rect(0,0,2*self.a,2*self.b))
        self.img.set_colorkey((255,255,255))

    def apply_force(self, point, force):
        self.normal_force += force
        self.tang_force += force.cross(point - self.cm)
##        r = point - self.cm
##        unit_to_cm = r.normalize()
##        self.tang_force += force.cross(unit_to_cm) * r.length()
##        print(force.cross(point - self.cm), self.tang_force)

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
        self.tang_force = 0.

##    def iter_points(self):
##        for angle in self.angles:
##            yield self.get_point_at_angle(angle).rotate(-self.angle) + self.cm


##    def get_colliding_points(self, other):
##        for p1 in self.iter_points():
##            for p2 in other.iter_points():
##                d = p1.distance_to(p2)
##                if d <= COLL_TOL:
##                    return d, p1, p2

##    def get_wall_colliding_points(self, axis, coord, normal):
##        if axis == "y":
##            candidates = []
##            for p1 in self.iter_points():
##                d = abs(p1.y-coord.y)
##                if d <= COLL_TOL:
##                    candidates.append((d, p1, normal))
##            if candidates:
##                return min(candidates, key=lambda x:x[0])

    def get_colliding_points(self, other):
        return self.get_one_intersection(other)

    def get_wall_colliding_points(self, axis, coord, normal):
        if axis == "y":
            if self.cm.y - coord.y <= self.max_radius:
##                candidates = []
                for p1 in self.iterate_points():
                    p1 = self.absolute_pos(p1)
                    d = abs(p1.y-coord.y)
                    if d <= COLL_TOL:
                        return d, p1, normal
##                        candidates.append((d, p1, normal))
##                if candidates:
##                    return min(candidates, key=lambda x:x[0])
        if axis == "x":
            if abs(self.cm.x - coord.x) <= self.max_radius:
##                candidates = []
                for p1 in self.iterate_points():
                    p1 = self.absolute_pos(p1)
                    d = abs(p1.x-coord.x)
                    if d <= COLL_TOL:
                        return d, p1, normal
##                        candidates.append((d, p1, normal))
##                if candidates:
##                    return min(candidates, key=lambda x:x[0])



##    def draw(self): #faire avec draw.ellipse
####        s = pygame.transform.rotate(self.img, self.angle)
####        r = s.get_rect()
####        r.center = self.cm
####        screen.blit(s, r.topleft)
####        pygame.draw.rect(screen, (0,0,0), r, 1)
####        #
##        points = []
##        for angle in self.angles:
##            point = self.get_point_at_angle(angle).rotate(-self.angle)+self.cm
##            points.append(point)
##            gfx.aacircle(screen, int(point.x), int(point.y), 3, (0,0,0))
##        gfx.aapolygon(screen, points, (0,0,0))
##        gfx.aacircle(screen, int(self.cm.x), int(self.cm.y), 3, (0,0,0))


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


    def collide_spring_wall(self, axis, wallcoord, normal):
        points = self.get_wall_colliding_points(axis, V2(wallcoord), V2(normal))
        if points:
            d, p1, normal_to_wall = points
            force_intensity = SPRING_CONSTANT*(d-COLL_TOL)
            force = force_intensity * normal_to_wall
            contact_point = p1
            self.apply_force(contact_point, V2(force))
            #
##            print(self.angle, self.ang_velocity)
##            screen.fill((255,255,255))
##            self.draw()
##            force /= 10.
##            gfx.line(screen, int(contact_point.x), int(contact_point.y),
##                    int(contact_point.x+force.x), int(contact_point.y+force.y), (0,0,255))
##            gfx.aacircle(screen, int(contact_point.x), int(contact_point.y), 2, (0,0,255))
##            pygame.display.flip()
##            app.pause()


    def collide_spring(self, other):
        points = self.get_colliding_points(other)
        if points:
            d, p1, p2 = points
            force_intensity = SPRING_CONSTANT*(d-COLL_TOL)
            normal_to_wall = other.get_normal(V2(p2),screen)
##            normal_to_wall = (p1-p2).normalize()
##            if self is m1:
##                print("uh")
##                screen.fill((255,255,255))
##                draw_meshes()
##                normal_to_wall = other.get_normal(V2(p2),screen)
##                pygame.display.flip()
##                app.pause()
            force = -force_intensity * normal_to_wall
            contact_point = p1
            fn = force.normalize()
            if (p1 + fn).distance_to(self.cm) > p1.distance_to(self.cm):
                force *= -1.
            self.apply_force(contact_point, V2(force))
            #
##            print(self.angle, self.ang_velocity)
##            if self is m1:
##                print(force, force.angle_to(p1-self.cm))
##                screen.fill((255,255,255))
##                draw_meshes()
##                force /= 10.
##                gfx.line(screen, int(contact_point.x), int(contact_point.y),
##                        int(contact_point.x+force.x), int(contact_point.y+force.y), (0,0,255))
##                gfx.aacircle(screen, int(contact_point.x), int(contact_point.y), 2, (0,0,255))
##                pygame.display.flip()
##                app.pause()

    def is_in_collision(self, others):
        for other in others:
            if self.get_colliding_points(other):
                return True
        return False


def draw_meshes():
    for m in meshes:
        m.draw(screen)

def add_forces():
    for im1,m in enumerate(meshes):
        #special collision with ground
        m.collide_spring_wall("y", (m.cm.x,H), (0,1))
        m.collide_spring_wall("x", (0,m.cm.y), (-1,0))
        m.collide_spring_wall("x", (W,m.cm.y), (1,0))
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

m1 = EllipticRigidBody2D(30, 10, W//2, H//2, angle=30.)
m2 = EllipticRigidBody2D(30, 30, W//2+40, H//2-100)
m3 = EllipticRigidBody2D(10, 30, W//2-40, H//2-200)
m1.angle = 20.
meshes = [m1,m2,m3]
##R = 20
##meshes = []
##for i in range(10):
##    m = EllipticRigidBody2D(30, 20, random.randint(R+1,W-R-1), random.randint(R+1,H-R-1), random.randint(0,360))
##    while m.is_in_collision(meshes):
##        m.set_pos((random.randint(R+1,W-R-1), random.randint(R+1,H-R-1)))
##    meshes.append(m)


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
        clock.tick(50)
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

#definir cutoffM et m
#collision : utiliser distance_to !!!!!!!!!!!!!!!