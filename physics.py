"""2D simulation of rigid bodies represented by arbitrary meshes, using PyGame
for drawing and vector calculus.

(c) 2017 Yann Thorimbert
"""
import math
import pygame
from pygame.math import Vector2 as V2
import pygame.gfxdraw as gfx

import parameters as P

def sgn(x):
    if x > 0:
        return 1.
    elif x < 0:
        return -1.
    return 0.

def location_collision(p,a,b):
    if abs(a.x - b.x) < P.TOL_DEL:
        x_ok = abs(p.x - (a.x+b.x)/2.) < P.TOL_DEL
    else:
        x_ok = (a.x <= p.x <= b.x) or (b.x <= p.x <= a.x)
    if x_ok:
        if abs(a.y - b.y) < P.TOL_DEL:
            y_ok = abs(p.y - (a.y+b.y)/2.) < P.TOL_DEL
        else:
            y_ok = (a.y <= p.y <= b.y) or (b.y <= p.y <= a.y)
        return y_ok
    return False

def point_collide_edge(p, a, b):
    if location_collision(p,a,b):
        dy = b.y-a.y
        dx = b.x-a.x
        bp = b-p
        alpha = (b-a).angle_to(bp)
        dist = math.sin(alpha*math.pi/180.)*bp.length()
        if abs(dist) < P.COLL_TOL:
            return dist
    return None

def point_collide_mesh(p, mesh):
    for i in range(1,len(mesh.points)):
        a = mesh.points[i-1]
        b = mesh.points[i]
        diff = point_collide_edge(p,a,b)
        if diff is not None:
            return i-1, i, diff
    diff = point_collide_edge(p,mesh.points[-1],mesh.points[0])
    if diff is not None:
        return len(mesh.points)-1, 0, diff
    return False


class Mesh2D:

    def __init__(self, points):
        self.points = [V2(float(p[0]),float(p[1])) for p in points]
        self.areas =[0 for p in points]
        self.forces = [V2() for p in points]
        self.tang_forces = [0. for p in points]
        self.normal_forces = [V2() for p in points]
        self.extra_body_force = V2()
        self.extra_body_torque = 0.
        self.cm = V2()
        self.refresh_cm()
        self.refresh_areas()
        self.velocity = V2() #in pix/s
        self.mass = 1.
        self.moment_of_inertia = 1.e4
        self.ang_velocity = 0. #in 1/s
        self.colliding = None
        self.fixed = False
        self.normal = 1.

    def get_normal(self,a,b):
        pa, pb = self.points[a], self.points[b]
        e = (pb - pa).normalize()
        if a == len(self.points)-1 and b == 0:
            a = -1
        if b == len(self.points)-1 and a == 0:
            b = -1
        if a < b:
            return self.normal*e.rotate(-90)
        elif a > b:
            return self.normal*e.rotate(90)

    def draw_normals(self):
        for i in range(1,len(self.points)):
            n = self.get_normal(i,i-1)*50
            b, a = self.points[i], self.points[i-1]
            p = a + (b-a)/2
            gfx.line(P.screen, int(p.x), int(p.y), int(p.x+n.x), int(p.y+n.y), (0,255,0))
        n = self.get_normal(len(self.points)-1,0)*50
        b, a = self.points[len(self.points)-1], self.points[0]
        p = a + (b-a)/2
        gfx.line(P.screen, int(p.x), int(p.y), int(p.x+n.x), int(p.y+n.y), (0,255,0))


    def add_force(self, i, force):
        r = self.points[i] - self.cm
        unit_to_cm = r.normalize()
        self.normal_forces[i] += force
        self.tang_forces[i] += -force.cross(unit_to_cm) * r.length()

    def add_force_edge(self, p, force):
        r = p - self.cm
        unit_to_cm = r.normalize()
        self.extra_body_force += force
        self.extra_body_torque += -force.cross(unit_to_cm) * r.length()

    def get_reduced_force(self):
        tot = V2()
        for f in self.normal_forces:
            tot += f
        return tot

    def get_reduced_torque(self):
        return sum(self.tang_forces)

    def refresh_translation(self):
        body_force = self.get_reduced_force() + self.extra_body_force
        a = body_force/self.mass
        self.velocity += a*P.DT
        self.move(self.velocity*P.DT)

    def refresh_rotation(self):
        body_torque = self.get_reduced_torque() + self.extra_body_torque
        a = body_torque/self.moment_of_inertia
        self.ang_velocity += a*P.DT
        self.rotate(self.ang_velocity*P.DT*360.)

    def refresh_physics(self):
        if not self.fixed:
            self.refresh_translation()
            self.refresh_rotation()
            self.forces = [V2() for p in self.points]
            self.clear_forces()

    def clear_forces(self):
        self.forces = [V2() for p in self.points]
        self.tang_forces = [0. for p in self.points]
        self.normal_forces = [V2() for p in self.points]
        self.extra_body_force = V2()
        self.extra_body_torque = 0.

    def refresh_cm(self):
        self.cm = V2()
        for p in self.points:
            self.cm += p
        self.cm /= len(self.points)

    def refresh_areas(self):
        n = len(self.points)
        def get_area(a,b,c):
            here = self.points[b]
            prev = self.points[a]
            next_ = self.points[c]
            return ((here-prev).length() + (here-next_).length())/2.
        for i in range(1,n-1):
            self.areas[i] = get_area(i-1,i,i+1)
        self.areas[0] = get_area(n-1,0,1)
        self.areas[-1] = get_area(n-2,n-1,0)
        tot = sum(self.areas)
        self.areas = [area/tot for area in self.areas]


    def draw(self):
        pygame.draw.lines(P.screen, (0,0,0), True, self.points)
        for i,p in enumerate(self.points):
            if i == 0:
                color = (255,0,0)
            elif i == 1:
                color = (0,255,0)
            elif i == 2:
                color = (0,0,255)
            else:
                color = (0,255,255)
            gfx.aacircle(P.screen, int(p[0]), int(p[1]), 5, color)

    def move(self, delta):
        for p in self.points:
            p += delta
        self.cm += delta #since pure translation (no deformation, no refresh)

    def set_pos(self, pos):
        delta = pos - self.cm
        self.move(delta)

    def rotate(self, angle_degrees): #around center of mass
        dq = V2(self.cm)
        self.move(-dq)
        for p in self.points:
            p.rotate_ip(angle_degrees)
        self.move(dq)

    def get_velocity(self, index):
        r = self.points[index] - self.cm
        rnorm = r.length()
        tanvel = r.normalize().rotate(sgn(self.ang_velocity)*90.)
        return self.velocity + self.ang_velocity*rnorm*tanvel#*2*pi

    def add_body_force(self, f):
        self.extra_body_force += f

    def collide_spring(self, mesh):
        for i,p in enumerate(self.points):
            collide = point_collide_mesh(p, mesh)
            if collide:
                self.colliding = mesh
                a = mesh.points[collide[0]]
                b = mesh.points[collide[1]]
                d = abs(collide[2])
                #
                force_intensity = P.SPRING_CONSTANT*(d-P.COLL_TOL)#*vp.normalize()
##                if force_intensity > MAX_FORCE_INTENSITY:
##                    print("correct", iteration, d)
##                    force_intensity = MAX_FORCE_INTENSITY
                normal_to_wall = mesh.get_normal(collide[0],collide[1])
                force = force_intensity*normal_to_wall
                self.add_force(i, V2(force))
                mesh.add_force_edge(p, -V2(force))
                return force, p
                break

    def collide(self, mesh):
        if mesh.colliding is not self:
            col = self.collide_spring(mesh)

def get_polygon(n,r):
    points = []
    angle = 0
    delta_angle = 360. / n
    v = V2(r,0)
    for i in range(n):
        points.append(v.rotate(angle))
        angle += delta_angle
    return Mesh2D(points)

def add_forces(meshes):
    for im1,m in enumerate(meshes):
        #collisions
        for im2,m2 in enumerate(meshes):
            if im1 != im2:
                m.collide(m2)
        for i,p in enumerate(m.points):
            #gravity
            m.add_force(i,P.GRAVITY*m.areas[i])
            #movement friction
            vel_i = m.get_velocity(i)
            velnorm = vel_i.length()
            if velnorm > 0:
                friction = vel_i.normalize()*velnorm*velnorm*P.FRICTION_COEFF
                m.add_force(i, friction*m.areas[i])
    for m in meshes:
        m.colliding = None
