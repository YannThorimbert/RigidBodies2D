from __future__ import print_function, division
import math, pygame, thorpy
from pygame.math import Vector2 as V2
import pygame.gfxdraw as gfx


class Ellipse2D:

    def __init__(self, a, b, cm, angle):
        self.a = a
        self.b = b
        self.cm = V2(cm)
        self.angle = angle
        self.nx = int(2.*self.a)
        self.ny = int(2.*self.b)
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

    def draw(self, screen):
        points = []
        for point in self.iterate_points():
            point = self.absolute_pos(point)
            points.append(point)
            gfx.pixel(screen, int(point.x), int(point.y), (0,0,0))
##            pos = gfx.aacircle(screen, int(point.x), int(point.y), 3, (0,0,0))
##        gfx.aapolygon(screen, points, (0,0,0))
        gfx.aacircle(screen, int(self.cm.x), int(self.cm.y), 3, (0,0,0))



if __name__ == "__main__":
    def refresh():
        pass

    W, H = 800, 600
    e1 = Ellipse2D(120, 50, (W/2, H/2), angle=60.)
    e2 = Ellipse2D(60, 60, (W/2+100, H/2), 0.)


    app = thorpy.Application((W,H))

    b = thorpy.Background.make()
    thorpy.add_time_reaction(b, refresh)

    screen = b.get_image()
    gfx.filled_circle(screen, W//2, H//2, 3, (0,255,0))
    e1.draw()
    e2.draw()
    for p in e1.get_all_intersections(e2):
        print(p)
        gfx.filled_circle(screen, int(p.x), int(p.y), 3, (0,0,255))
    pygame.display.flip()

    m = thorpy.Menu(b).play()


    app.quit()