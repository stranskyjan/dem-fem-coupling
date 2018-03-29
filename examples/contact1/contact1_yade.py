######################################################################
#
# YADE input file. Only material and engines are defined, DEM
# particles themselve will be included from OOFEM
#
######################################################################

from libyade import yade
from yade import *

# basic materials
matS = O.materials.append(PolyhedraMat(young=5e7,poisson=10,frictionAngle=1.4))

# basic YADE engines
O.engines = [
	ForceResetter(),
	InsertionSortCollider([Bo1_Polyhedra_Aabb()]),
	InteractionLoop(
		[Ig2_Polyhedra_Polyhedra_PolyhedraGeom()],
		[Ip2_PolyhedraMat_PolyhedraMat_PolyhedraPhys()],
		[Law2_PolyhedraGeom_PolyhedraPhys_Volumetric()]),
	NewtonIntegrator(),
]

def vtkExport(i):
	name = '/tmp/contact1_yade'
	from yade import export
	export.VTKExporter(name,i).exportPolyhedra()
