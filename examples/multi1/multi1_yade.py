#from libyade import yade
from yade import *
from yade import pack, Vector3, Vector3

nREVs = 16

def randomPeriPack(radius,initSize,seed):
	O.switchScene(); O.resetThisScene()
	sp=pack.SpherePack()
	O.periodic=True
	O.cell.setBox(initSize)
	sp.makeCloud(Vector3().Zero,O.cell.refSize,radius,0.,-1,True,seed=seed)
	O.engines=[ForceResetter(),InsertionSortCollider([Bo1_Sphere_Aabb()],verletDist=.05*radius),InteractionLoop([Ig2_Sphere_Sphere_ScGeom()],[Ip2_FrictMat_FrictMat_FrictPhys()],[Law2_ScGeom_FrictPhys_CundallStrack()]),PeriIsoCompressor(charLen=2*radius,stresses=[-100e9,-1e8],maxUnbalanced=1e-2,doneHook='O.pause();',globalUpdateInt=20,keepProportions=True),NewtonIntegrator(damping=.8)]
	O.materials.append(FrictMat(young=30e9,frictionAngle=.1,poisson=.3,density=1e3))
	for s in sp: O.bodies.append(utils.sphere(s[0],s[1]))
	O.dt=utils.PWaveTimeStep()
	O.timingEnabled=True
	O.run(); O.wait()
	for b in O.bodies: b.state.pos = O.cell.wrap(b.state.pos)
	ret=pack.SpherePack()
	ret.fromSimulation()
	O.switchScene()
	return ret

for i in xrange(nREVs):
	if i != 0:
		newScene = O.addScene()
		O.switchToScene(newScene)
	young = 4e6 if i<8 else 2e6
	O.materials.append(CpmMat(young=young,poisson=.2,epsCrackOnset=1e100,sigmaT=1e100,relDuctility=2))
	sp = randomPeriPack(.01,.1*Vector3.Ones,i+10)
	sp.toSimulation()
	O.engines = [
		ForceResetter(),
		InsertionSortCollider([Bo1_Sphere_Aabb(aabbEnlargeFactor=1.5,label='is2aabb')],allowBiggerThanPeriod=True),
		InteractionLoop(
			[Ig2_Sphere_Sphere_ScGeom(interactionDetectionFactor=1.5,label='ss2d3dg')],
			[Ip2_CpmMat_CpmMat_CpmPhys()],
			[Law2_ScGeom_CpmPhys_Cpm()]),
		NewtonIntegrator(damping=.2),
	]
	O.dt = 0.
	O.step()
	is2aabb.aabbEnlargeFactor = 1.
	ss2d3dg.interactionDetectionFactor = 1.

def vtkExport(i):
	base = '/tmp/multi1_yade_{:02d}'
	from yade import export
	for rvei in xrange(nREVs):
		O.switchToScene(rvei)
		name = base.format(rvei)
		export.VTKExporter(name,i).exportSpheres(useRef=True,what=[('dspl','b.state.displ()')])
