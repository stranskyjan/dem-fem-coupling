######################################################################
#
# Python script (input file for YADE). Creates some DEM particles to
# "bombard" OOFEM mesh
#
######################################################################
from libyade import yade
from yade import *

# basic material
matS = O.materials.append(FrictMat(young=1e5,density=5000))

# create 3 spheres
b1 = utils.sphere((-1,.5,4.5),.48,material=matS)
b2 = utils.sphere((1.6,-3.2,4),.48,material=matS)
b3 = utils.sphere((1.6,1.6,4.0),.48,material=matS)
# and assign initial velocity to them
b1.state.vel = (5,0,.5)
b2.state.vel = (0,5,.5)
b3.state.vel = (0,0,0)

yade.O.bodies.append((b1,b2,b3))

# standard YADE engines
O.engines = [
	ForceResetter(),
	InsertionSortCollider([Bo1_Sphere_Aabb(),Bo1_Facet_Aabb()]),
	InteractionLoop(
		[Ig2_Sphere_Sphere_ScGeom(),Ig2_Facet_Sphere_ScGeom()],
		[Ip2_FrictMat_FrictMat_FrictPhys()],
		[Law2_ScGeom_FrictPhys_CundallStrack()]),
	NewtonIntegrator(gravity=(0,0,-.3)),
]
