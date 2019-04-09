from __future__ import print_function, division
import math, pygame, sys
import matplotlib.pyplot as plt
from pygame.math import Vector2 as V2
import pygame.gfxdraw as gfx

def rad2deg(x):#180->pi, d->r
    return x*180./math.pi

def deg2rad(x):
    return x*math.pi/180.

RESOLUTION = 1.
TOLERANCE = 1.

a, b = 100, 50
min_dist = 2*min(a,b) - 1
max_dist = 2*max(a,b) + 1

screen = pygame.display.set_mode((800,600))
BUILD = False
DELTA_DIST_DIVIDER = 2.
DELTA_DIST_0 = 20.
DELTA_DIST_TARGET = 0.5
DA = 1
DACM = 1
ANGLES = list(range(-90,91,DA))
ANGLES_CM = list(range(-90,91,DACM))

LANGLES = len(ANGLES)
LCM = len(ANGLES_CM)

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
        """Return:
            d : the distance between the boundaries
            p1 : the concerned point in self's boundary (absolute)
            p2 : the concerned point in other's boundary (absolute)
        """
        R = self.max_radius + other_ellipse.max_radius
        if self.cm.distance_to(other_ellipse.cm) <= R:
            for p1 in self.iterate_points():
                p1 = self.absolute_pos(p1)
                for p2 in other_ellipse.iterate_points():
                    p2 = other_ellipse.absolute_pos(p2)
                    d = p1.distance_to(p2)
                    if d < TOLERANCE:
                        return d, p1, p2

    def get_one_intersection_cache(self, other_ellipse, cache_for_p1):
        """Return:
            d : the distance between the boundaries
            p1 : the concerned point in self's boundary (absolute)
            p2 : the concerned point in other's boundary (absolute)
        """
        R = self.max_radius + other_ellipse.max_radius
        if self.cm.distance_to(other_ellipse.cm) <= R:
            for p1 in cache_for_p1:
                for p2 in other_ellipse.iterate_points():
                    p2 = other_ellipse.absolute_pos(p2)
                    d = p1.distance_to(p2)
                    if d < TOLERANCE:
                        return d, p1, p2

    def absolute_pos(self, p):
        return p.rotate(-self.angle)+self.cm

    def get_angle_to(self, direction):
        return V2(1,0).rotate(self.angle).angle_to(direction)

    def get_a_axis(self):
        return V2(self.a,0).rotate(-self.angle)

    def get_angle_to_ellipse(self, e2):
        return self.get_angle_to(e2.get_a_axis())

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
            gfx.pixel(screen, int(point.x), int(point.y), (0,0,0))
        x,y = self.get_a_axis() + self.cm
        x = int(x)
        y = int(y)
        gfx.line(screen, int(self.cm.x), int(self.cm.y), x, y, (0,255,0))
        gfx.aacircle(screen, int(self.cm.x), int(self.cm.y), 3, (0,0,0))

    def clone(self):
        return Ellipse2D(self.a, self.b, self.cm, self.angle)


def draw():
    screen.fill((255,255,255))
    for e in ellipses:
        e.draw(screen)


def build_lut(e1, e2, fn):
    f = open(fn, "w")
    e1.angle = 0.
    e1.cm = V2(0,0)
    cache_for_p1 = [p for p in e1.iterate_points()]
    for i_a,angle in enumerate(ANGLES):
        print("lut angle", angle)
        e2.angle = angle
        for i_acm,acm in enumerate(ANGLES_CM):
            print("     acm=",acm,end=", dist= ")
            dist = e1.max_radius + e2.max_radius + DELTA_DIST_0
            delta_dist = DELTA_DIST_0
            while True:
                e2.cm = V2(dist,0).rotate(acm)
                result = e1.get_one_intersection_cache(e2, cache_for_p1)
                ################################################################
                screen.fill((255,255,255))
                e1.cm += (300,300)
                e2.cm += (300,300)
                e1.draw(screen)
                e2.draw(screen)
                e1.cm = V2(0,0)
                pygame.display.flip()
                ################################################################
                if result:
                    if delta_dist <= DELTA_DIST_TARGET:
                        d,p1,p2 = result
                        x,y = p1
                        str_output = str(dist) + " " + str(x) + " " + str(y)
                        str_input = str(angle) + " " + str(acm) + " "
                        f.write(str_input + str_output + "\n")
                        ########################################################
                        x = int(x)
                        y = int(y)
                        gfx.aacircle(screen, x+300,y+300, 3, (0,0,0))
                        pygame.display.flip()
                        ########################################################
                        print(dist)
                        break
                    else:
                        dist += delta_dist
                        delta_dist /= DELTA_DIST_DIVIDER
                else:
                    dist -= delta_dist
            else:
                print("Ô_Ô")
                f.write("-1\n")
    f.close()
    return lut


# def load_lut(fn):
#     #Read lut on the format lut[rel_angle][angle_cm] = dist, rel_point_from_e1
#     f = open(fn, "r")
#     lines = [line for line in f.readlines() if line]
#     f.close()
#     lut = [[None for acm in ANGLES_CM] for angle in ANGLES]
#     iline = 0
#     for i_a,angle in enumerate(ANGLES):
#         for i_acm,acm in enumerate(ANGLES_CM):
#             data = [float(v) for v in lines[iline].replace("\n","").split(" ")]
#             lut[i_a][i_acm] = data
#             iline += 1
#     f.close()
#     return lut


def load_lut(fn):
    #Read lut on the format lut[rel_angle][angle_cm] = dist, rel_point_from_e1
    f = open(fn, "r")
    lut = {}
    iline = 0
    for line in f.readlines():
        data = [float(v) for v in line.replace("\n","").split(" ")]
        lut[(int(data[0]),int(data[1]))] = data[2:]
    f.close()
    return lut

# def use_lut(e1, e2, recursive_ok=True):
#     rel_angle = e1.get_angle_to_ellipse(e2)
#     if ANGLES[0] <= rel_angle <= ANGLES[-1]:
#         acm = V2(1,0).angle_to(e2.cm - e1.cm)
#         if ANGLES_CM[0] <= acm <= ANGLES_CM[-1]:
#             i_a = int( (rel_angle-ANGLES[0]) / DA) #a enlever normalement le moins angle0
#             i_acm = int( (acm-ANGLES_CM[0]) / DACM)
#             dist, x, y = lut[i_a][i_acm]
#             if dist < 0:
#                 print("PROBLEM DIST")
#             else:
#                 return dist, x, y
#         else:
#             print("acm not in ANGLES_ACM : ", acm)
#     else:
#         print("rel angle not in ANGLES : ", rel_angle)
#     return -1, None, None

def use_lut(e1, e2):
    rel_angle = e1.get_angle_to_ellipse(e2)
    acm = V2(1,0).angle_to(e2.cm - e1.cm)
    # round_angle = round( (rel_angle/10.))*10
    # round_acm = round( (acm/10.))*10
    # round_angle = int(rel_angle)
    # round_acm = int(acm)
    round_angle = round(rel_angle)
    round_acm = round(acm)
    # print(round_angle, round_acm, lut.get((round_angle, round_acm), (-1,None,None)))
    return lut.get((round_angle, round_acm), (-1,None,None))

def showlut(acm, color):
    angles = []
    distances = []
    for i_a,angle in enumerate(ANGLES):
        angles.append(angle)
        dist, x, y = lut.get((angle, acm), (-1,None,None))
        distances.append(dist)
    # plt.plot(angles, distances, color+"o-", label="acm="+str(acm))
    plt.plot(distances, color+"-", label="acm="+str(acm))

def correct_lut(acm, threshold=5):
    for i_a in range(1,LANGLES):
        pd, px, py = lut.get((ANGLES[i_a-1], acm), (-1,None,None))
        dist, x, y = lut.get((ANGLES[i_a], acm), (-1,None,None))
        if abs(pd-dist) > threshold:
            i_next = (i_a+1)%LANGLES
            nd, nx, ny = lut.get((ANGLES[i_next], acm), (-1,None,None))
            correct_dist = (pd+nd)/2.
            correct_x = (px+nx)/2.
            correct_y = (py+ny)/2.
            lut[(ANGLES[i_a],acm)] = (correct_dist, correct_x, correct_y)



#faire en mode [angle_absolu] = (angle_relatif, distance_critique)
e1 = Ellipse2D(a,b,(200,200),0)
e2 = Ellipse2D(a,b,(300,300),0)
ellipses = [e1,e2]

if BUILD:
    lut = build_lut(e1,e2, "lut.dat")
    exit()
else:
    lut = load_lut("lut.dat")


colors = ["k","y","b","g"]
plt.clf()
for acm in ANGLES_CM:
    correct_lut(acm, threshold=7)
    correct_lut(acm, threshold=7)
    correct_lut(acm, threshold=3)
    correct_lut(acm, threshold=3)
    # for i in range(10):
    #     correct_lut(acm, threshold=7)
    showlut(acm,colors[acm%len(colors)])
plt.legend()
plt.xlabel("angle")
plt.ylabel("distance")
plt.show()
# exit()

if __name__ == "__main__":
    screen = pygame.display.set_mode((800,600))
    e1.cm = V2(300,300)
    loop = True
    clock = pygame.time.Clock()
    while loop:
        clock.tick(100)
        draw()
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                loop = False
            elif e.type == pygame.MOUSEMOTION:
                e2.cm = V2(e.pos)
            elif e.type == pygame.MOUSEBUTTONDOWN:
                if e.button == 1:
                    e2.angle -= 10.
                else:
                    e2.angle += 10.
                print(e1.get_angle_to_ellipse(e2))
        dist_lut, x, y = use_lut(e1,e2)
        if dist_lut <= 0:
            print("UUUH")
        else:
            deltapos = e2.cm - e1.cm
            actual_distance = deltapos.length()
            print(actual_distance)
            # if actual_distance < 0:
            #     continue
            p = V2(x,y) + e1.cm #+ angle !!
            x = int(p.x)
            y = int(p.y)
            if actual_distance > dist_lut:
                gfx.aacircle(screen, x,y, 3, (0,255,0))
            else:
                gfx.aacircle(screen, x,y, 3, (0,0,255))
        pygame.display.flip()

    pygame.quit()
