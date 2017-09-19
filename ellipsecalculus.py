from __future__ import print_function, division
import math, pygame
from pygame.math import Vector2 as V2
import pygame.gfxdraw as gfx

def rad2deg(x):#180->pi, d->r
    return x*180./math.pi

def deg2rad(x):
    return x*math.pi/180.

RESOLUTION = 1.

class Ellipse2D:

    def __init__(self, a, b, cm, angle):
        self.a = a
        self.b = b
        self.cm = V2(cm)
        self.angle = angle
        self.nx = int(RESOLUTION*self.a)
        self.ny = int(RESOLUTION*self.b)
        self.max_radius = max([self.a, self.b])


    def iterate_points_along_x(self):
        for i in range(self.nx):
            x = -self.a + float(i)/self.nx * 2*self.a
            y = self.b * math.sqrt(1 - (x/self.a)**2)
            yield V2(x,y)
            yield V2(x,-y)

    def iterate_points_along_y(self):
        for i in range(self.ny):
            y = -self.b + float(i)/self.ny * 2*self.b
            x = self.a * math.sqrt(1 - (y/self.b)**2)
            yield V2(x,y)
            yield V2(-x,y)

    def iterate_points(self):
        for point in self.iterate_points_along_x():
            yield point
        for point in self.iterate_points_along_y():
            yield point

    def get_all_intersections(self, other_ellipse):
        intersections = []
        for p1 in self.iterate_points():
            p1 = self.absolute_pos(p1)
            for p2 in other_ellipse.iterate_points():
                p2 = other_ellipse.absolute_pos(p2)
                if p1.distance_to(p2) < 1:
                    intersections.append(p1)
        return intersections

    def get_one_intersection(self, other_ellipse):
        if self.cm.distance_to(other_ellipse.cm) <= self.max_radius + other_ellipse.max_radius:
            for p1 in self.iterate_points():
                p1 = self.absolute_pos(p1)
                for p2 in other_ellipse.iterate_points():
                    p2 = other_ellipse.absolute_pos(p2)
                    d = p1.distance_to(p2)
                    if d < 1:
                        return d, p1, p2

    def absolute_pos(self, p):
        return p.rotate(-self.angle)+self.cm

    def get_angle_to(self, direction):
        return V2(1,0).rotate(self.angle).angle_to(direction)

    def get_radius_at_angle(self, angle):
        """Angle is relative to self's a axis. unit is degrees"""
        angle = deg2rad(angle)
        tan2 = math.tan(angle)**2
        dx2 = self.a2*self.b2/(self.b2 + self.a2*tan2)
        dy2 = tan2 * dx2
        return math.sqrt(dx2 + dy2)

    def get_point_at_angle(self, angle):
        """Angle is relative to self's a axis. unit is degrees.
        Return point relative to self.cm"""
        radius = self.get_radius_at_angle(angle)
        return V2(radius,0).rotate(angle)

    def get_relative_angle_to_point(self, p):
        angle = V2(1,0).angle_to(p-self.cm) #- ?
        return angle + self.angle

    def get_normal(self, p, screen):
        rel_angle = self.get_relative_angle_to_point(p)
        p2 = self.get_point_at_angle(rel_angle+1.)
        p3 = self.get_point_at_angle(rel_angle-1.)
        p2 = self.absolute_pos(p2)
        p3 = self.absolute_pos(p3)
        return (p3-p2).rotate(-90).normalize()

    def draw(self, screen):
        points = []
        for point in self.iterate_points():
            point = self.absolute_pos(point)
            points.append(point)
            gfx.pixel(screen, int(point.x), int(point.y), (0,0,0))
##            pos = gfx.aacircle(screen, int(point.x), int(point.y), 3, (0,0,0))
##        gfx.aapolygon(screen, points, (0,0,0))
        xy = self.absolute_pos(V2(self.a,0))
        x = int(xy[0])
        y = int(xy[1])
        gfx.line(screen, int(self.cm.x), int(self.cm.y), x, y, (0,0,0))
        gfx.aacircle(screen, int(self.cm.x), int(self.cm.y), 3, (0,0,0))


def draw():
    screen.fill((255,255,255))
    for e in ellipses:
        e.draw(screen)
    pygame.display.flip()

def build_lut(e1, e2, A, D):
    lut = [[None for dist in range(D)] for angle in range(A)]
    e1.angle = 0.
    for angle in range(A):
        e2.angle = angle
        for dist in range(D):
            e2.cm = V2(dist, 0)
            lut[angle][dist] = e1.get_one_intersection(e2)


# screen = pygame.display.set_mode((800,600))
# e1 = Ellipse2D(100,50,(200,200),50)
# e2 = Ellipse2D(100,50,(300,300),0)
# ellipses = [e1,e2]
#
# loop = True
# while loop:
#     for e in pygame.event.get():
#         if e.type == pygame.QUIT:
#             loop = False
#         elif e.type == pygame.MOUSEMOTION:
#             e1.cm = V2(e.pos)
#             draw()
#         elif e.type == pygame.MOUSEBUTTONDOWN:
#             e1.angle += 10.
#     i = e1.get_one_intersection(e2)
#     if i:
#         print(i)
#
# pygame.quit()
