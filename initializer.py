import random, math, pygame
import pygame.gfxdraw as gfx

import os
os.environ['SDL_VIDEO_CENTERED'] = '1'

w, h, r, n = None, None, None, None

def sgn(x):
    if x > 0.:
        return 1.
    elif x < 0.:
        return -1.
    return 0.

def set_params(w_,h_,r_,n_):
    global w,h,r,n
    w = w_
    h = h_
    r = r_
    n = n_

def d(c1, c2):
    dx, dy = abs(c2[0]-c1[0]), abs(c2[1]-c1[1])
    if dx > w/2.: #dx + k = w==> k=w - dx
        dx = w - dx
    if dy > h/2.:
        dy = h - dy;
    return math.hypot(dx,dy)

def floatrand(n):
    return random.random()*n

def periodic_pos(sphere):
    sphere[0] %= w
    sphere[1] %= h

################################################################################


def count_collisions(spheres):
    counter = 0
    two_r = 2*r
    for i in range(n): #first loop
        for j in range(n):
            if i != j:
                if d(spheres[i],spheres[j]) < two_r:
                    counter += 1
    return counter


def spring(spheres, factor, vmax):
    forces = [[0.,0.] for i in range(n)]
    two_r = 2*r
    tolerance = 0.1*r #mais attention au counter
    collisions = 0
    for i in range(n): #first loop
        for j in range(n):
            if i != j:
                distance = d(spheres[i],spheres[j])
                if distance < two_r + tolerance:
                    dq = distance - two_r
                    intensity = -(dq-tolerance)
                    dx = spheres[j][0] - spheres[i][0]
                    dy = spheres[j][1] - spheres[i][1]
                    forces[i][0] -= sgn(dx)*intensity
                    forces[i][1] -= sgn(dy)*intensity
    for i in range(n):
        vnorm = math.hypot(forces[i][0],forces[i][1])*factor
        if vnorm > vmax:
            vx = forces[i][0]/vnorm
            vy = forces[i][1]/vnorm
            spheres[i][0] += vx*vmax
            spheres[i][1] += vy*vmax
            periodic_pos(spheres[i])
            collisions += 1
    return collisions

def draw(spheres, screen):
    screen.fill((0,0,0))
    for x,y in spheres:
        gfx.aacircle(screen, int(x), int(y), r, (255,255,255))
    pygame.display.flip()

def initialize_spheres(w,h,r,n,trials):
    """w and h are the size of the domain, spheres is a list of centers.
    Here all spheres have the same radius."""
    print("Volume fraction =", n*math.pi*r*r / (w*h))
    screen = pygame.display.set_mode((w,h))
    set_params(w,h,r,n)
    spheres = []
    for i in range(n): #1. random init
        spheres.append([floatrand(w), floatrand(h)])
    draw(spheres, screen)
    collisions = count_collisions(spheres)
    collisions0 = float(collisions)
    clock = pygame.time.Clock()
    for trial in range(trials):
        clock.tick(45)
##        collisions = spring(spheres,collisions/collisions0 + 0.2)
        collisions = spring(spheres,1.,0.01)
        if trial%1 == 0:
            draw(spheres, screen)
            if trial%100 == 0:
                print("     ",trial,"collisions =",collisions)
        if collisions == 0:
            print("finished at", trial)
            break
    draw(spheres,screen)
    kk = 0
    loop = True
    while loop:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                loop = False
            elif e.type == pygame.MOUSEMOTION:
                pass
            elif e.type == pygame.MOUSEBUTTONDOWN:
                pygame.draw.rect(screen, (255,255,255),
                                pygame.Rect(e.pos[0]-2,e.pos[1]-2,4,4))
                pygame.display.flip()
                kk += 1
                print(kk)

    pygame.quit()
    return spheres

random.seed(100000)
spheres = initialize_spheres(300, 300, 20, n=60, trials=int(2e3))
################################################################################


