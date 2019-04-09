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
TOLERANCE = 2.

a, b = 100, 50
min_dist = 2*min(a,b) - 1
max_dist = 2*max(a,b) + 1

BUILD = False
DA = 1
DD = 1
DACM = 1
ANGLES = list(range(0,91,DA))
DISTANCES = list(range(min_dist, max_dist,DD))
ANGLES_CM = list(range(0,91,DACM))

LANGLES = len(ANGLES)
LDISTANCES = len(DISTANCES)
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

    # def iterate_points_along_x_quarter(self):
    #     for i in range(self.nx):
    #         x = -self.a + float(i)/self.nx * 2*self.a
    #         y = self.b * math.sqrt(1 - (x/self.a)**2)
    #         yield V2(x,y)
    #
    # def iterate_points_along_y_quarter(self):
    #     for i in range(self.ny):
    #         y = -self.b + float(i)/self.ny * 2*self.b
    #         x = self.a * math.sqrt(1 - (y/self.b)**2)
    #         yield V2(x,y)
    #
    # def iterate_points_quarter(self):
    #     for point in self.iterate_points_along_x_quarter():
    #         yield point
    #     for point in self.iterate_points_along_y_quarter():
    #         yield point

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
                        # print("chouette")
                        return d, p1, p2

    # def get_one_intersection_quarter(self, other_ellipse):
    #     """Return:
    #         d : the distance between the boundaries
    #         p1 : the concerned point in self's boundary (absolute)
    #         p2 : the concerned point in other's boundary (absolute)
    #     """
    #     R = self.max_radius + other_ellipse.max_radius
    #     if self.cm.distance_to(other_ellipse.cm) <= R:
    #         for p1 in self.iterate_points_quarter():
    #             p1 = self.absolute_pos(p1)
    #             for p2 in other_ellipse.iterate_points_quarter():
    #                 p2 = other_ellipse.absolute_pos(p2)
    #                 d = p1.distance_to(p2)
    #                 if d < TOLERANCE:
    #                     return d, p1, p2

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


def build_lut(e1, e2, fn=None):
    if fn:
        f = open(fn, "w")
    lut = [[[None for acm in ANGLES_CM] for dist in DISTANCES] for angle in ANGLES]
    e1.angle = 0.
    e1.cm = V2(0,0)
    for i_a,angle in enumerate(ANGLES):
        print("lut angle", angle)
        e2.angle = angle
        counterFalse = 0 #number of consecutive times that no intersection is found with this angle, whatever dist and cm are
        for i_d,dist in enumerate(DISTANCES):
            print("     lut distance", dist, end=" ")
            found = False #intersection exists at this angle and distance, whatever cm is
            for i_acm,acm in enumerate(ANGLES_CM):
                print("*",end="")
                sys.stdout.flush()
                if counterFalse > 3:
                    if fn:
                        f.write("None\n")
                else:
                    e2.cm = V2(dist,0).rotate(acm)
                    i = e1.get_one_intersection(e2)
                    if i:
                        found = True
                        d,p1,p2 = i
                        lut[i_a][i_d][i_acm] = d,p1
                        if fn:
                            f.write(str(d)+" "+str(tuple(p1))+"\n")
                    else:
                        if fn:
                            f.write("None\n")
            print()
            if not found: #there is no intersection at this angle and distance
                counterFalse += 1
                if counterFalse == 4:
                    print("BOUM")
            else:
                counterFalse = 0
    f.close()
    return lut

##def get_dist_lut

def load_lut(fn):
    f = open(fn, "r")
    lines = [line for line in f.readlines() if line]
    f.close()
    lut = [[[None for acm in ANGLES_CM] for dist in DISTANCES] for angle in ANGLES]
    iline = 0
    print("LL", len(lines))
    for i_a,angle in enumerate(ANGLES):
        for i_d,dist in enumerate(DISTANCES):
            for i_acm,acm in enumerate(ANGLES_CM):
                s = lines[iline]
                if not "None" in s:
                    d,p = s.split("(")
                    p = p.replace(")","").replace(",","")
                    px = float(p.split(" ")[0])
                    py = float(p.split(" ")[1])
                    d = float(d)
                    lut[i_a][i_d][i_acm] = d, (px,py)
                iline += 1
    f.close()
    return lut

def use_lut(e1, e2, recursive_ok=True):
    neg_acm = False
    big_acm = False
    rel_angle = e1.get_angle_to_ellipse(e2)
    if rel_angle < 0:
        rel_angle = -rel_angle
    if ANGLES[0] <= rel_angle <= ANGLES[-1]:
        dist = e1.cm.distance_to(e2.cm)
        if DISTANCES[0] <= dist <= DISTANCES[-1]:
            acm = V2(1,0).angle_to(e2.cm - e1.cm)
            if acm < 0:
                acm = -acm
                neg_acm = True
            if acm > 90.:
                acm = 180 - acm
                big_acm = True
            if ANGLES_CM[0] <= acm <= ANGLES_CM[-1]:
                i_a = int(rel_angle / DA)
                i_d = int((dist-DISTANCES[0]) / DD)
                i_acm = int(acm / DACM)
                result = lut[i_a][i_d][i_acm]
                if result:
                    d, p = result
                    if neg_acm:
                        p = V2(p[0],-p[1])
                    if big_acm:
                        p = V2(-p[0],p[1])
                    return d, p
                # elif recursive_ok:
                #     # print("None", big_acm, neg_acm)
                #     e1p, e2p = e1.clone(), e2.clone()
                #     # delta_y = e2.cm.y - e1.cm.y
                #     # e2p.cm -= V2(0,2*delta_y)
                #     # delta = e2.cm - e1.cm
                #     # e2p.cm -= 2*delta
                #     delta_x = e2.cm.x - e1.cm.x
                #     e2p.cm -= V2(2*delta_x,0)
                #     # e2p.angle = -e2.angle
                #     # e2p.angle = 180-e2.angle
                #     e2p.draw(screen)
                #     result = move_until_collide_lut(e1p, e2p, V2(0,-1))
                #     if result:
                #         d,p = result
                #         pabs = e2p.cm + p
                #         # pabs.x += 2*delta_x
                #         e2p.draw(screen)
                #         gfx.aacircle(screen, int(pabs.x), int(pabs.y), 3, (0,255,0))
                #         return d,p
                    # result = use_lut(e1p, e2p, False)
                    # return result
    #             print("(angle,dist,acm) =", rel_angle, dist, acm)
    #             print("(i_a,i_d,i_acm) =", i_a,i_d,i_acm)
    #             print()
            else:
                print("acm not in ANGLES_ACM : ", acm, e2.cm - e1.cm, e2.cm, e1.cm)
        else:
            print("Dist not in DISTANCES : ", dist, DISTANCES[0], DISTANCES[-1])
    else:
        print("rel angle not in ANGLES : ", rel_angle)


def move_until_collide_lut(e1, e2, delta):
    for i in range(1000):
        result = use_lut(e1,e2,False)
        if result:
            return result
        e2.cm += delta

def showlut(i_acm, color):
    angles = []
    distances = []
    for i_a,angle in enumerate(ANGLES):
        angles.append(angle)
        found = False
        for i_d in range(LDISTANCES-1,-1,-1):
            result = lut[i_a][i_d][i_acm]
            if result is not None:
                d,p = result
                dist = DISTANCES[i_d]
                distances.append(dist)
                found = True
                break
        if not found:
            distances.append(0)
    plt.plot(angles, distances, color+"--", label="acm="+str(ANGLES_CM[i_acm]))

#
# def showlut():
#     for i_a,angle in enumerate(ANGLES):
#         for i_d,dist in enumerate(DISTANCES):
#             if lut[i_a][i_d] is not None:
#                 print(angle,dist,lut[i_a][i_d] )


#faire en mode [angle_absolu] = (angle_relatif, distance_critique)
e1 = Ellipse2D(a,b,(200,200),0)
e2 = Ellipse2D(a,b,(300,300),0)
ellipses = [e1,e2]

if BUILD:
    lut = build_lut(e1,e2, "lut.dat")
    exit()
else:
    lut = load_lut("lut.dat")


# colors = ["k","y","b","g"]
# plt.clf()
# for i in range(LCM):
#     showlut(i,colors[i%len(colors)])
# # plt.legend()
# plt.xlabel("angle")
# plt.ylabel("distance")
# # plt.ylim([0.,300.])
# plt.show()
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

        # L = use_lut(e1,e2)
        # if L:
        #     d,p = L
        #     x,y = e1.cm + p
        #     x = int(x)
        #     y = int(y)
        #     gfx.aacircle(screen, x,y, 3, (0,0,255))

        # L = e1.get_one_intersection_quarter(e2)
        L = e1.get_one_intersection(e2)
        if L:
            d,p1,p2 = L
            x,y = p1
            x = int(x)
            y = int(y)
            gfx.aacircle(screen, x,y, 3, (0,0,0))
        pygame.display.flip()

    pygame.quit()
