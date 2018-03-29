######################################################################
#
# Python script (input file for YADE). Creates some DEM particles to
# "bombard" OOFEM mesh
#
######################################################################
from libyade import yade
from yade import *

usePolyhedra = False

# basic material
if usePolyhedra:
	mat = PolyhedraMat(young=2e7,density=4000)
else:
	mat = FrictMat(young=1e5,density=3000)
O.materials.append(mat)

# create 3 spheres
radius = 0.48
if usePolyhedra:
	from yade import polyhedra_utils
	d = 1.7*radius
	b1,b2,b3 = [polyhedra_utils.polyhedra(mat, size=(d,d,d),seed=i) for i in (1,2,3)]
else:
	b1,b2,b3 = [utils.sphere((0,0,0),radius) for _ in (1,2,3)]
b1.state.pos = (-1,.5,4.5)
b2.state.pos = (1.5,-3.2,4)
b3.state.pos = (1.5,1.6,4.0)
# and assign initial velocity to them
b1.state.vel = (6,0,0)
b2.state.vel = (0,5,0)
b3.state.vel = (0,0,0)

yade.O.bodies.append((b1,b2,b3))

# standard YADE engines
if usePolyhedra:
	bo1 = Bo1_Polyhedra_Aabb()
	iLoop = InteractionLoop(
		[Ig2_Polyhedra_Polyhedra_PolyhedraGeom(),Ig2_Facet_Polyhedra_PolyhedraGeom()],
		[Ip2_PolyhedraMat_PolyhedraMat_PolyhedraPhys()],
		[Law2_PolyhedraGeom_PolyhedraPhys_Volumetric()],
	)
else:
	bo1 = Bo1_Sphere_Aabb()
	iLoop = InteractionLoop(
		[Ig2_Sphere_Sphere_ScGeom(),Ig2_Facet_Sphere_ScGeom()],
		[Ip2_FrictMat_FrictMat_FrictPhys()],
		[Law2_ScGeom_FrictPhys_CundallStrack()],
	)

O.engines = [
	ForceResetter(),
	InsertionSortCollider([bo1,Bo1_Facet_Aabb()]),
	iLoop,
	NewtonIntegrator(),
]

def vtkExport(i):
	name = '/tmp/surf1_yade'
	from yade import export
	export.VTKExporter(name,i).exportFacets()
	if usePolyhedra:
		export.VTKExporter(name,i).exportPolyhedra()
	else:
		export.VTKExporter(name,i).exportSpheres()
