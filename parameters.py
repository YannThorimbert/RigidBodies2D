from pygame.math import Vector2 as V2

DT = 2.e-3
FRICTION_COEFF = -1.e-2
COLL_TOL = 5
TOL_DEL = COLL_TOL
SPRING_CONSTANT = -1000.
##MIND_D = 1 #cutoff not used
##MAX_FORCE_INTENSITY = SPRING_CONSTANT*(MIND_D-COLL_TOL)
GRAVITY = V2(0, 9.81)
screen = None