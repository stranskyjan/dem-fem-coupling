import sys
import os
import mupif
from mupif.api.oofem.oofem_interface import *
from mupif.api.yade.yade_interface import *
from example2_common import *

def vtkExport(i):
	"""Do VTK export"""
	fem.problem.giveExportModuleManager().giveModule(1).doForcedOutput(fem.problem.giveCurrentStep())
	from yade import export
	name = ('/tmp/' if os.path.exists('/tmp') else '') + 'example2-yade'
	yade.export.VTKExporter(name,i).exportSpheres(what=[('displ','b.state.displ()')],useRef=True)
	yade.export.VTKExporter(name,i).exportFacets()

def meshSolid2surface(mesh):
	"""From FEM mesh exctracts only surface"""
	assert all(e.giveGeometryType()==mupif.cell.Tetrahedron_3d_1 for e in mesh.cells())
	faces = list(set(tuple(sorted([e.vertices[i] for i in ii])) for ii in ((0,1,2),(0,1,3),(0,2,3),(1,2,3)) for e in mesh.cells()))
	faces = dict((f,0) for f in faces)
	for e in mesh.cells():
		for ii in ((0,1,2),(0,1,3),(0,2,3),(1,2,3)):
			f = tuple(sorted([e.vertices[i] for i in ii]))
			faces[f] += 1
	assert sorted(list(set(faces.values())))==[1,2]
	bfaces = sorted([f for f in faces.iterkeys() if faces[f]==1])
	assert all(faces[f]==1 for f in bfaces)
	ret = mupif.mesh.UnstructuredMesh()
	ret.vertexList = mesh.vertexList
	ret.cellList = [mupif.cell.Triangle_2d_lin(ret,0,0,f) for i,f in enumerate(bfaces)]
	for i,c in enumerate(ret.cellList):
		c.number = i
	return ret

class FemDemSurfaceCoupler:
	def __init__(self,fem,dem):
		self.fem = fem
		self.dem = dem
		#
		tstep = mupif.timestep.TimeStep(1e-8,1e-8)
		self.fem.solve(tstep)
		self.dem.solve(tstep)
		self.dem.registerMesh(meshSolid2surface(fem.giveMesh()),tetras=False)
		self.dspl = fem.giveField(mupif.field.FieldID.FID_Displacement, None)
		self.forces = fem.giveField(mupif.field.FieldID.FID_ForceVector, None)
	def solveAt(self,tstep):
		"""Solve one step"""
		dem.updateField(self.forces, None)
		fem.updateFromField(self.forces, None)
		loadSleeper()
		fem.solve(tstep)
		fem.updateField(self.dspl, None)
		dem.updateFromField(self.dspl, None)
		dem.solve(tstep)
		#
	def solve(self,nSteps,dt,doVtkExport=0,step0=0):
		"""Solve whoel simulation"""
		for i in xrange(step0,nSteps+step0):
			tstep = mupif.timestep.TimeStep(i*dt,dt,i)
			coupler.solveAt(tstep)
			if doVtkExport and not i%doVtkExport: vtkExport(i)

femName = 'example2-oofem.in'
demName = 'example2-yade.py'
dem = YADE_API(demName)
fem = OOFEM_API(femName)
coupler = FemDemSurfaceCoupler(fem,dem)

def sortNodes():
	zMax = 1e-20
	for i in xrange(domain.giveNumberOfDofManagers()):
		zMax = max(zMax,domain.giveDofManager(i+1).giveCoordinates()[2])
	fNodes = []
	sNodes = []
	for i in xrange(domain.giveNumberOfDofManagers()):
		a = domain.giveDofManager(i+1).giveCoordinates()
		c = [a[j] for j in xrange(3)]
		if abs(c[0]-.5*(width+sWidth))<1e-6 and abs(c[2]-zMax)<1e-6:
		 	fNodes.append(i+1)
		if abs(c[2]) > 0:
			sNodes.append(i+1)
	return fNodes,sNodes
	 
def loadSleeper1():
	pass

def loadSleeper2():
	load = liboofem.FloatArray()
	load.resize(3)
	load.zero()
	load[2] = -2e3
	for i in fNodes:
		l = domain.giveLoad(i)
		a = l.giveComponentArray()
		a.add(load)
		l.setComponentArray(a)

def sleeperZDspl(mode='min'):
	mask=liboofem.IntArray(3)
	mask[0]=liboofem.DofIDItem.D_u
	mask[1]=liboofem.DofIDItem.D_v
	mask[2]=liboofem.DofIDItem.D_w
	ret = 1e20 if mode=='min' else 1e-20 if mode=='max' else None
	compare = min if mode=='min' else max if mode=='max' else None
	for i in sNodes:
		node = domain.giveDofManager(i)
		dspl = liboofem.FloatArray()
		node.giveUnknownVector(dspl, mask, liboofem.ValueModeType.VM_Total, fem.problem.giveCurrentStep())
		z = dspl[2]
		ret = compare(ret,z)
	return ret

domain = fem.giveMesh()._OofemUnstructuredMesh__domain
fNodes,sNodes = sortNodes()

nSteps,dt,output = 1000,.00125,15
nSteps,dt,output = 5000,.1e-4,100
vtkExport(0)

print O.bodies # accessing Yade through O

loadSleeper = loadSleeper1
coupler.solve(3000,dt,output,step0=1)

loadSleeper = loadSleeper2
i = 3001
while abs(sleeperZDspl()) < .1:
	print abs(sleeperZDspl())
	coupler.solve(100,dt,output,step0=i)
	i += 100
	if i > 7000:
		break
	
loadSleeper = loadSleeper1
coupler.solve(1000,dt,output,step0=i)
