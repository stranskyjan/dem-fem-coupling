######################################################################
#
# Python script (input file for YADE). Creates some DEM particles to
# be split in three point bending
#
######################################################################
from math import sqrt
from libyade import yade
from yade import *

r = .005
dx,dy = .26, .12
nx = int(round(dx/(2*r)))
ny = int(round(dy/(2*r*.5*sqrt(3))))
sp = []
for yi in xrange(ny):
	y = r + yi*2*r*.5*sqrt(3)
	ddx = r if yi%2 else 0
	for xi in xrange(nx):
		x = -.5*dx + .3*r + xi*2*r + ddx
		sp.append(((x,y,0),r))

frictMat = FrictMat(density=3000,young=1e9,poisson=10,frictionAngle=.1)
cpmMat = CpmMat(density=3000,young=1e9,epsCrackOnset=3e-3,sigmaT=1e8,frictionAngle=0,relDuctility=1e2)
O.materials.append((frictMat,cpmMat))

O.bodies.append([utils.sphere(c,r) for c,r in sp])
for b in O.bodies:
	b.state.blockedDOFs = 'zXY'

# standard YADE engines
intRatio = 1.5
O.engines = [
	ForceResetter(),
	InsertionSortCollider([Bo1_Sphere_Aabb(aabbEnlargeFactor=intRatio,label='bo1')]),
	InteractionLoop(
		[Ig2_Sphere_Sphere_ScGeom(interactionDetectionFactor=intRatio,label='ig2')],
		[Ip2_CpmMat_CpmMat_CpmPhys(),Ip2_FrictMat_FrictMat_FrictPhys()],
		[Law2_ScGeom_CpmPhys_Cpm(),Law2_ScGeom_FrictPhys_CundallStrack()]),
	NewtonIntegrator(damping=.1),
	CpmStateUpdater(iterPeriod=20),
]
O.dt = 0.0
O.step()
bo1.aabbEnlargeFactor = ig2.interactionDetectionFactor = 1.0

ys = (.0,.004 ,.009,.016,.026 ,.036,.046,.056,.066,.076)
ys = [.13 + y for y in ys]
rs = (.003,.0055,.008,.012,.016,.02,.02,.02,.02,.02)
impactor = [utils.sphere((0,y,0),r) for y,r in zip(ys,rs)]
cid,ids = O.bodies.appendClumped(impactor)
impactor = O.bodies[cid]
impactor.state.blockedDOFs = 'zXY'
impactor.state.vel = (0,-50,0)
impactor.state.mass *= 3
impactor.state.inertia *= 15
for b in O.bodies:
	b.mat = frictMat

def vtkExport(i):
	from yade import export
	name = '/tmp/vol1_yade'
	export.VTKExporter(name,i).exportSpheres(what=[('dmg','b.state.normDmg if isinstance(b.state,CpmState) else 0')])
	export.VTKExporter(name,i).exportInteractions()
