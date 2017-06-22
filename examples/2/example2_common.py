young = 1e6
density = 2500
poisson = .2

width = 1.4
thick = .5
particleRadius = .05

sWidth  = .7
sThick  = .2
sHeight = .1

def engines():
	from yade import *
	return  [
		ForceResetter(),
		InsertionSortCollider([Bo1_Sphere_Aabb(),Bo1_Box_Aabb(),Bo1_Facet_Aabb()],allowBiggerThanPeriod=True),
		InteractionLoop(
			[Ig2_Sphere_Sphere_ScGeom(),Ig2_Facet_Sphere_ScGeom(),Ig2_Box_Sphere_ScGeom()],
			[Ip2_FrictMat_FrictMat_FrictPhys()],
			[Law2_ScGeom_FrictPhys_CundallStrack()]
		),
		NewtonIntegrator(gravity=(0,0,-9.81)),
	]

def materials():
	from yade import *
	matS = O.materials.append(FrictMat(young=young,poisson=poisson,density=density))
	matF = O.materials.append(FrictMat(young=10*young,poisson=poisson,density=density))
	return matS,matF
