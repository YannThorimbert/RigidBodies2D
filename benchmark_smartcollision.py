from __future__ import print_function, division
import math, sys, random, time
from pygame.math import Vector2 as V2
import matplotlib.pyplot as plt

W, H = 800, 400
DT = 10.e-3
COLL_TOL = 1
TOL_DEL = COLL_TOL
SPRING_CONSTANT = 1000.
MIND_D = 1
MAX_FORCE_INTENSITY = SPRING_CONSTANT*(MIND_D-COLL_TOL)
GRAVITY = V2(0, 9.81)
FRICTION_COEFF = -5e-3
COLL_FRICTION = 0.999



# COLORS = [(0,)*3, (127,)*3, (255,0,0), (0,255,0), (0,0,255), (255,0,255)]
COLORS = [(0,0,255)]

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
        self.tang_force = 0.
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
        if delta.length() == 0:
            print("LOL")
        distance = delta.length()
        if distance <= self.radius + COLL_TOL: #+ margin
            d = distance - self.radius
            force_intensity = SPRING_CONSTANT*(d-COLL_TOL)
            normal_to_wall = delta.normalize()
            contact_point = self.cm + normal_to_wall*self.radius
            force = force_intensity * normal_to_wall
            self.apply_force(contact_point, V2(force))
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

def add_forces(collision_grid, meshes):
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

def naive_add_forces(meshes):
    for im1,m in enumerate(meshes):
        #special collision with walls
        m.collide_spring_wall((m.cm.x,H)) #bottom wall
        m.collide_spring_wall((0,m.cm.y)) #left wall
        m.collide_spring_wall((W,m.cm.y)) #right wall
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

def refresh_physics(meshes):
    for m in meshes:
        m.refresh_physics()


def run(R, grid_cell_factor, nspheres):

    grid_cell_size = grid_cell_factor*R
    nx = int(W/grid_cell_size)
    ny = int(H/grid_cell_size)

    print("Nx, Ny ", nx, ny)
    print("W, H ", W, H)


    collision_grid = CollisionGrid(nx,ny)
    print(2*R*collision_grid.factorX, ":", R, collision_grid.factorX,collision_grid.nx,W)
    assert 2*R*collision_grid.factorX <= 1.
    assert 2*R*collision_grid.factorY <= 1.


    print("Wanted number of spheres:",nspheres)

    meshes = []
    hmin = 0
    for i in range(nspheres):
        debug_counter = 0
        m = Sphere2D(R, random.randint(R+1,W-R-1), random.randint(hmin,H-R-1))
        while m.is_in_collision(meshes):
            m.set_pos((random.randint(R+1,W-R-1), random.randint(hmin,H-R-1)))
            debug_counter += 1
            if debug_counter > 10000:
                print("Couldn't initialize with this domain size and sphere size")
                assert(False)
        meshes.append(m)

    print("Final number of spheres:", len(meshes))
    beg = time.clock()
    for i in range(NITER):
        add_forces(collision_grid, meshes)
        refresh_physics(meshes)
    end = time.clock()
    print("Time ", nspheres, R, grid_cell_factor, end-beg)
    return [nspheres, R, grid_cell_factor, end-beg]

def naive_run(R, nspheres):
    print("Wanted number of spheres:",nspheres)
    meshes = []
    hmin = 0
    for i in range(nspheres):
        debug_counter = 0
        m = Sphere2D(R, random.randint(R+1,W-R-1), random.randint(hmin,H-R-1))
        while m.is_in_collision(meshes):
            m.set_pos((random.randint(R+1,W-R-1), random.randint(hmin,H-R-1)))
            debug_counter += 1
            if debug_counter > 10000:
                print("Couldn't initialize with this domain size and sphere size")
                assert(False)
        meshes.append(m)

    print("Final number of spheres:", len(meshes))
    beg = time.clock()
    for i in range(NITER):
        naive_add_forces(meshes)
        refresh_physics(meshes)
    end = time.clock()
    print("Time naive",end-beg)
    return end-beg


NITER = 1000
Rlist = [2,5,10]
Flist = [2,3,5,10]
Nlist = [2,50,100,150,200,250,300,350,400] #max 400
stats = []
f = open("stats.dat","w")
for R in Rlist:
    for grid_cell_factor in Flist:
        for nspheres in Nlist:
            Tnaive = naive_run(R, nspheres)
            stat = run(R, grid_cell_factor, nspheres) + [Tnaive]
            print()
            print("**********")
            print("Stat : ",stat)
            f.write(" ".join([str(x) for x in stat])+"\n")
            stats.append(stat)
f.close()

# stats_R = []
# for R in Rlist:
#
#
# plt.clf()
# plt.plot([R for R,F,N,T in stats], [T for R,F,N,T in stats], "o")
# plt.title("T(R)")
# plt.show()
