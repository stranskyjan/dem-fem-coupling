#####################################################
#
# surface fem-dem coupling test
#
#####################################################

import sys
import os
import mupif
import time
# import interfaces
from mupif.api.oofem.oofem_interface import *
# to use sys.argv also with libyade
#argv = sys.argv
#sys.argv = sys.argv[:1]
from mupif.api.yade.yade_interface import *

def vtkExport(i):
	"""Do VTK export"""
	fem.problem.giveExportModuleManager().giveModule(1).doForcedOutput(fem.problem.giveCurrentStep())
	from yade import export
	name = ('/tmp/' if os.path.exists('/tmp') else '') + 'example1-yade'
	yade.export.VTKExporter(name,i).exportSpheres()
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
		#
		#self.dem.registerMesh(fem.giveMesh(),tetras=False)
		self.dem.registerMesh(meshSolid2surface(fem.giveMesh()),tetras=False)
		#print len([b for b in O.bodies if isinstance(b.shape,yade.Facet)])
		# displacement field
		self.dspl = fem.giveField(mupif.field.FieldID.FID_Displacement, None)
		# force field
		self.forces = fem.giveField(mupif.field.FieldID.FID_ForceVector, None)
	def solveAt(self,tstep):
		"""Solve one step"""
		# apply forces from DEM onto FEM
		dem.updateField(self.forces, None)
		fem.updateFromField(self.forces, None)
		# solve FEM part
		fem.solve(tstep)
		# apply displacement from FEM onto DEM
		fem.updateField(self.dspl, None)
		dem.updateFromField(self.dspl, None)
		# solve DEM part
		dem.solve(tstep)
	def solve(self,nSteps,dt,doVtkExport=0):
		"""Solve whoel simulation"""
		for i in xrange(1,nSteps+1):
			# define one solution time step
			tstep = mupif.timestep.TimeStep(i*dt,dt,i)
			# solve one step
			coupler.solveAt(tstep)
			# do vtk export if right time steps
			if doVtkExport and not i%doVtkExport: vtkExport(i)

t1 = time.time()
# initialize both domains
femName = 'example1-oofem.in'
demName = 'example1-yade.py'
#for i,a in enumerate(argv):
#	if a=='-fem': femName = argv[i+1]
#	if a=='-dem': demName = argv[i+1]
dem = YADE_API(demName)
fem = OOFEM_API(femName)
# create coupler object
coupler = FemDemSurfaceCoupler(fem,dem)

# run the simulation
nSteps,dt,output = 1000,.00125,15
vtkExport(0)
t2 = time.time()
coupler.solve(nSteps,dt,output)
t = time.time()
print
print 'Duration of script: %g s'%(t-t1)
print 'Duration of solve:  %g s'%(t-t2)
print
