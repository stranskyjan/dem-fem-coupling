######################################################################
#
# DEM FEM COUPLING MODULE
# auxiliary functions and classes for DEM-FEM coupling using OOFEM
# and YADE
#
######################################################################
from minieigen import Vector3, Matrix3, Matrix6

######################################################################
class TimeStep:
	def __init__(self, time, dt, number=1):
		self.time = time
		self.dt = dt
		self.number = number

######################################################################
# auxiliary UnstructuredGrid class
class Vertex:
	def __init__(self,id,coords):
		self.id = id
		self.coords = Vector3(coords)
		# list of cells which the vertex belongs to
		self.cells = []

class CellTypes:
	# www.vtk.org/VTK/img/file-formats.pdf
	TRIANGLE = "TRIANGLE"
	QUAD = "QUAD"
	TETRA = "TETRA"
	HEXAHEDRON = "HEXAHEDRON"
	# TODO

class Cell:
	def __init__(self,id,type,vertices):
		self.id = id
		self.type = type
		self.vertices = tuple(vertices)
		# list of cells which creates boundaries of this cell
		self.boundaries = []
		# list of cells for which this cell is a boundary
		self.bounding = []
		self.processBoundaries()
		for v in self.vertices: # add info about self to vertices
			v.cells.append(self)
	def processBoundaries(self):
		sides,types = [],[]
		# extract sides (as a vertices ids lists) and types of boundaries
		if self.type == CellTypes.HEXAHEDRON:
			sides = ((0,3,2,1),(0,4,7,3),(0,1,5,4),(1,2,6,5),(2,3,7,6),(4,5,6,7))
			types = [CellTypes.QUAD for _ in sides]
		elif self.type == CellTypes.TETRA:
			sides = ((0,2,1),(0,1,3),(0,3,2),(1,2,3))
			types = [CellTypes.TRIANGLE for _ in sides]
		elif self.type in (CellTypes.QUAD,CellTypes.TRIANGLE):
			pass # TODO ?
		else:
			raise RuntimeError
		# according to sides and types, get / create new boundaries
		bs = [self.getBoundary(side,type) for side,type in zip(sides,types)]
		for b in bs: # update boundaries and bounding members
			self.boundaries.append(b)
			b.bounding.append(self)
	def getBoundary(self,side,type):
		vs = [self.vertices[vi] for vi in side]
		sids = set(v.id for v in vs)
		for v in vs:
			cs = [c for c in v.cells if c.type == type]
			for c in cs:
				if set(v.id for v in c.vertices) == sids:
					return c
		return Cell(-1,type,vs)

class UnstructuredGrid:
	def __init__(self,vertices,cells):
		self.vertices = list(vertices)
		self.cells = list(cells)
	def getSurface(self):
		cs = list(set(b for c in self.cells for b in c.boundaries if len(b.bounding) == 1))
		vs = list(set(v for c in cs for v in c.vertices))
		return self._subCopy(vs,cs)
	def getSubsetByVertices(self,ids):
		ids = set(ids)
		vs = [v for v in self.vertices if v.id in ids]
		cs = [c for c in self.cells if any(v.id in ids for v in c.vertices)]
		return self._subCopy(vs,cs)
	def _subCopy(self,vs,cs):
		vs = [Vertex(v.id,v.coords) for v in vs]
		id2v = dict((v.id,v) for v in vs)
		cs = [Cell(i+1,c.type,[id2v[v.id] for v in c.vertices]) for i,c in enumerate(cs)]
		return UnstructuredGrid(vs,cs)

######################################################################


######################################################################
class ProgramInterface:
	def __init__(self,fileName,_lib):
		self.fileName = fileName
		self._lib = _lib
	def solve(self, tstep):
		raise NotImplementedError
	def vtkExport(self, i):
		pass
class FEMProgramInterface(ProgramInterface):
	def toUnstructuredGrid(self):
		raise NotImplementedError
	def giveIntegrationPoint(self,index):
		raise NotImplementedError
	def numberOfNodes(self):
		raise NotImplementedError
class DEMProgramInterface(ProgramInterface):
	def addSurface(self,surf):
		raise NotImplementedError
	def addContactBody(self,mesh,**kw):
		raise NotImplementedError

class OofemInterface(FEMProgramInterface):
	def __init__(self,fileName,_lib):
		ProgramInterface.__init__(self,fileName,_lib)
		m = __import__(self.fileName)
		self.problem = m.problem
		#
		self.geomType2type = {
			self._lib.Element_Geometry_Type.EGT_hexa_1: CellTypes.HEXAHEDRON,
			self._lib.Element_Geometry_Type.EGT_tetra_1: CellTypes.TETRA,
		}
		if hasattr(m,"vtkExport"):
			self.vtkExport = m.vtkExport
	def initProblem(self):
		self.problem.checkProblemConsistency()
		self.problem.init()
		self.problem.postInitialize()
		self.problem.setRenumberFlag()
	def solve(self, tstep):
		oofemtstep = self.problem.giveNextStep()
		oofemtstep.setTimeIncrement(tstep.dt)
		oofemtstep.setTargetTime(tstep.time)
		oofemtstep.setIntrinsicTime(tstep.time)
		self.problem.solveYourselfAt(oofemtstep)
		self.problem.updateYourself(oofemtstep)
		self.problem.terminate(oofemtstep)
	def toUnstructuredGrid(self):
		d = self.problem.giveDomain(1)
		#
		vertices = {}
		for i in xrange(d.numberOfDofManagers):
			n = d.giveDofManager(i+1)
			id = n.number
			coords = Vector3(n.coordinates)
			v = Vertex(id,coords)
			vertices[id] = v
		#
		cells = []
		for i in xrange(d.giveNumberOfElements()):
			e = d.giveElement(i+1)
			id = e.number
			nis = e.giveDofManArray()
			vs = [vertices[ni] for ni in nis]
			t = self.geomType2type[e.geometryType]
			c = Cell(id,t,vs)
			cells.append(c)
		#
		vertices = vertices.values()
		return UnstructuredGrid(vertices,cells)
	def numberOfSpatialDimensions(self):
		d = self.problem.giveDomain(1)
		t = d.giveDomainType()
		lt = self._lib.domainType
		if t in (lt._2dPlaneStressMode,): # TODO
			return 2
		if t in (lt._3dMode): # TODO
			return 3
		return 0
	def giveIntegrationPoint(self,index):
		ie,igp = index
		domain = self.problem.giveDomain(1)
		assert ie <= domain.giveNumberOfElements()
		ir = domain.giveElement(ie).giveDefaultIntegrationRulePtr()
		assert igp < ir.giveNumberOfIntegrationPoints()
		ip = ir.getIntegrationPoint(igp)
		return ip
	def numberOfNodes(self):
		return self.problem.giveDomain(1).numberOfDofManagers

class YadeInterface(DEMProgramInterface):
	def __init__(self,fileName,_lib):
		ProgramInterface.__init__(self,fileName,_lib)
		m = __import__(self.fileName)
		self.omega = m.O
		if hasattr(m,"vtkExport"):
			self.vtkExport = m.vtkExport
	def solve(self, tstep):
		self.omega.dt = tstep.dt
		self.omega.step()
	def addSurface(self,surf,**kw):
		vertices = [Vertex(i,v.coords) for i,v in enumerate(surf.vertices)]
		v2v = dict((sv,v) for sv,v in zip(surf.vertices,vertices))
		cells = []
		facets = []
		for c in surf.cells:
			if c.type == CellTypes.TRIANGLE:
				vss = [tuple(c.vertices)]
			elif c.type == CellTypes.QUAD:
				vss = [[c.vertices[i] for i in ijk] for ijk in ((0,1,2),(0,2,3))]
			else:
				raise NotImplementedError
			for vs in vss:
				facets.append(self._lib.utils.facet([v.coords for v in vs],**kw))
				vs = [v2v[v] for v in vs]
				cells.append(Cell(-1,CellTypes.TRIANGLE,vs))
		ids = self.omega.bodies.append(facets)
		for c,i in zip(cells,ids):
			c.id = i
		return UnstructuredGrid(vertices,cells)
	def addContactBody(self,mesh,**kw):
		ret = []
		for cell in mesh.cells:
			vs = [v.coords for v in cell.vertices]
			assert len(vs) == 4
			b = self._lib.utils.polyhedron(vs,**kw)
			ret.append(b)
		for b in ret:
			b.state.blockedDOFs = 'xyzXYZ'
		O.bodies.append(ret)
		return ret
######################################################################


######################################################################
class FemDemMeshSurfaceMap:
	def __init__(self,fem,dem,femMesh,demMesh):
		self.fem = fem
		self.dem = dem
		self.femMesh = femMesh
		self.demMesh = demMesh
		self.check()
		self.reset()
	def check(self):
		vfs = self.femMesh.vertices
		vds = self.demMesh.vertices
		assert len(vfs) == len(vds)
		assert all(vf.coords == vd.coords for vf,vd in zip(vfs,vds))
	def reset(self):
		pass
	def getForcesFromDem(self):
		raise NotImplementedError
	def applyForcesOnFem(self):
		raise NotImplementedError
	def getDsplFromFem(self):
		raise NotImplementedError
	def applyDsplOnDem(self):
		raise NotImplementedError

class OofemYadeMeshSurfaceMap(FemDemMeshSurfaceMap):
	def __init__(self,*args):
		FemDemMeshSurfaceMap.__init__(self,*args)
		vs = self.femMesh.vertices
		nvs = len(vs)
		self.forces, self.dspl = [[Vector3.Zero for _ in vs] for __ in (0,1)]
		flib = self.fem._lib
		d = self.fem.problem.giveDomain(1)
		nfs = d.giveNumberOfFunctions() + 1
		d.resizeFunctions(nfs)
		d.setFunction(nfs,flib.constantFunction(nfs,d,f_t=1))
		nbcs = d.giveNumberOfBoundaryConditions()
		d.resizeBoundaryConditions(nbcs+nvs)
		def nLoad(i):
			ret = flib.NodalLoad(i,d)
			ca = flib.FloatArray(3)
			ca.zero()
			ret.setComponentArray(ca)
			ret.setFunction(nfs)
			return ret
		self.loads = [nLoad(nbcs+i+1) for i,v in enumerate(vs)]
		for v,load in zip(vs,self.loads):
			i = v.id
			n = d.giveDofManager(i)
			la = n.giveLoadArray()
			lenla = len(la)
			la.resize(lenla+1)
			la[lenla] = load.number
			d.setBoundaryCondition(load.number, load)
	def getForcesFromDem(self):
		self.forces = [Vector3.Zero for _ in self.femMesh.vertices]
		mesh = self.demMesh
		bodies = self.dem.omega.bodies
		for cell in mesh.cells:
			facet = bodies[cell.id]
			intrs = facet.intrs()
			if not intrs:
				continue
			for intr in intrs:
				cp = intr.geom.contactPoint
				f = intr.phys.normalForce + intr.phys.shearForce
				f = f * (-1 if facet.id == intr.id1 else +1 if facet.id == intr.id2 else 'ERROR')
				ws = w1,w2,w3 = self.facetWeights(cell,facet,cp)
				for v,w in zip(cell.vertices,ws):
					self.forces[v.id] += f*w
	def facetWeights(self,cell,facet,cp):
		v1,v2,v3 = vs = [v.coords for v in cell.vertices]
		n = facet.shape.normal
		dcp = cp - v1
		cp = v1 + (dcp - (dcp.dot(-n))*(-n))
		w1 = (cp-v2).cross(cp-v3).norm()
		w2 = (cp-v3).cross(cp-v1).norm()
		w3 = (cp-v1).cross(cp-v2).norm()
		sws = (w1+w2+w3)
		ws = [w/sws for w in (w1,w2,w3)]
		return ws
	def applyForcesOnFem(self):
		for load,force in zip(self.loads,self.forces):
			ca = self.fem._lib.FloatArray(3)
			for i,v in enumerate(force):
				ca[i] = v
			load.setComponentArray(ca)
	def getDsplFromFem(self):
		p = self.fem.problem
		d = p.giveDomain(1)
		def v2d(v):
			lib = self.fem._lib
			n = d.giveDofManager(v.id)
			uv = lib.FloatArray()
			dm = lib.IntArray(3)
			dm[0] = lib.DofIDItem.D_u
			dm[1] = lib.DofIDItem.D_v
			dm[2] = lib.DofIDItem.D_w
			t = p.giveCurrentStep()
			n.giveUnknownVector(uv,dm,lib.ValueModeType.VM_Total,t,False)
			return Vector3(list(uv))
		self.dspl = [Vector3(v2d(v)) for v in self.femMesh.vertices]
	def applyDsplOnDem(self):
		id2dspl = dict((v.id,dspl) for v,dspl in zip(self.demMesh.vertices,self.dspl))
		lib = self.dem._lib
		bodies = self.dem.omega.bodies
		for c in self.demMesh.cells:
			facet = bodies[c.id]
			v1,v2,v3 = [v.coords+id2dspl[v.id] for v in c.vertices]
			cc = facet.state.pos = lib.utils.inscribedCircleCenter(v1,v2,v3)
			v1,v2,v3 = [v-cc for v in (v1,v2,v3)]
			facet.shape.setVertices(v1,v2,v3)

class FemDemSurfaceCoupler:
	"""
	TODO
	"""
	def __init__(self,fem,dem,femDemMeshMap,exportFunction=None):
		self.fem = fem
		self.dem = dem
		self.femDemMeshMap = femDemMeshMap
		self.exportFunction = exportFunction
		#
		self.fem.initProblem()
	def solveAt(self,tstep):
		"""Solve one step"""
		# solve FEM and DEM part
		self.fem.solve(tstep)
		self.dem.solve(tstep)
		# apply forces from DEM onto FEM
		self.femDemMeshMap.getForcesFromDem()
		self.femDemMeshMap.applyForcesOnFem()
		# apply displacement from FEM onto DEM
		self.femDemMeshMap.getDsplFromFem()
		self.femDemMeshMap.applyDsplOnDem()
	def solve(self,nSteps,dt,doVtkExport=0):
		"""Solve whole simulation"""
		for i in xrange(1,nSteps+1):
			# define one solution time step
			tstep = TimeStep(i*dt,dt,i)
			# solve one step
			self.solveAt(tstep)
			# do vtk export if right time steps
			self.export(i,doVtkExport)
	def export(self,i,doVtkExport=0):
		if self.exportFunction and (doVtkExport==0 or (doVtkExport!=0 and i%doVtkExport==0)):
			self.exportFunction(i,self.fem,self.dem)
######################################################################


######################################################################
class FemDemMeshVolumeMap:
	def __init__(self,fem,dem):
		self.fem = fem
		self.dem = dem
		self.check()
		self.reset()
	def check(self):
		pass
	def reset(self):
		pass
	def getForcesFromDem(self):
		raise NotImplementedError
	def applyForcesOnFem(self):
		raise NotImplementedError
	def getDsplFromFem(self):
		raise NotImplementedError
	def applyDsplOnDem(self):
		raise NotImplementedError

class OofemYadeMeshVolumeMap(FemDemMeshVolumeMap):
	def __init__(self,*args):
		FemDemMeshVolumeMap.__init__(self,*args)
		d = self.fem.problem.giveDomain(1)
		localizer = d.giveSpatialLocalizer()
		liboofem = self.fem._lib
		#
		self.demParticles = []
		self.femNodes = []
		#
		for b in self.dem.omega.bodies:
			pos = liboofem.FloatArray(3)
			for i,v in enumerate(b.state.pos):
				pos[i] = v
			e = localizer.giveElementContainingPoint(pos,None)
			if not e:
				continue
			i = d.numberOfDofManagers + len(self.femNodes) + 1
			pos = tuple(b.state.pos)
			dt = d.giveDomainType()
			nsd = self.fem.numberOfSpatialDimensions()
			dofType = nsd*[2]
			n = liboofem.dofManager("hangingNode",i,d,coords=pos,dofType=dofType,masterElement=e.number)
			b.state.blockedDOFs = "xyzXYZ"
			self.demParticles.append(b)
			self.femNodes.append(n)
		d.resizeDofManagers(d.numberOfDofManagers+len(self.femNodes))
		for n in self.femNodes:
			d.setDofManager(n.number, n)
		#
		nfs = d.giveNumberOfFunctions() + 1
		d.resizeFunctions(nfs)
		d.setFunction(nfs,liboofem.constantFunction(nfs,d,f_t=1))
		nbcs = d.giveNumberOfBoundaryConditions()
		d.resizeBoundaryConditions(nbcs+len(self.femNodes))
		def nLoad(i):
			ret = liboofem.NodalLoad(i,d)
			ca = liboofem.FloatArray(self.fem.numberOfSpatialDimensions())
			ca.zero()
			ret.setComponentArray(ca)
			ret.setFunction(nfs)
			return ret
		self.loads = [nLoad(nbcs+i+1) for i,v in enumerate(self.femNodes)]
		for n,load in zip(self.femNodes,self.loads):
			la = n.giveLoadArray()
			lenla = len(la)
			la.resize(lenla+1)
			la[lenla] = load.number
			d.setBoundaryCondition(load.number, load)
	def getForcesFromDem(self):
		oForces = self.dem.omega.forces
		self.forces = [oForces.f(b.id) for b in self.demParticles]
	def applyForcesOnFem(self):
		ns = self.fem.numberOfSpatialDimensions()
		for load,force in zip(self.loads,self.forces):
			ca = self.fem._lib.FloatArray(ns)
			for i in xrange(ns):
				ca[i] = force[i]
			load.setComponentArray(ca)
	def getDsplFromFem(self):
		def v2d(n):
			lib = self.fem._lib
			uv = lib.FloatArray()
			dm = lib.IntArray(3)
			dm[0] = lib.DofIDItem.D_u
			dm[1] = lib.DofIDItem.D_v
			dm[2] = lib.DofIDItem.D_w
			t = self.fem.problem.giveCurrentStep()
			n.giveUnknownVector(uv,dm,lib.ValueModeType.VM_Total,t,False)
			l = list(uv) + (3-len(uv))*[0]
			return Vector3(l)
		self.dspl = [Vector3(v2d(n)) for n in self.femNodes]
	def applyDsplOnDem(self):
		dt = self.dem.omega.dt
		for p,d in zip(self.demParticles,self.dspl):
			# TODO vel
			dspl = p.state.refPos + d - p.state.pos
			p.state.vel = dspl/dt

class FemDemVolumeStrongCoupler:
	"""
	TODO
	"""
	def __init__(self,fem,dem,femDemMeshMap,exportFunction=None):
		self.fem = fem
		self.dem = dem
		self.femDemMeshMap = femDemMeshMap
		self.exportFunction = exportFunction
		#
		self.fem.initProblem()
	def solveAt(self,tstep):
		"""Solve one step"""
		# solve FEM and DEM part
		self.fem.solve(tstep)
		self.dem.solve(tstep)
		# apply forces from DEM onto FEM
		self.femDemMeshMap.getForcesFromDem()
		self.femDemMeshMap.applyForcesOnFem()
		# apply displacement from FEM onto DEM
		self.femDemMeshMap.getDsplFromFem()
		self.femDemMeshMap.applyDsplOnDem()
	def solve(self,nSteps,dt,doVtkExport=0):
		"""Solve whole simulation"""
		for i in xrange(1,nSteps+1):
			# define one solution time step
			tstep = TimeStep(i*dt,dt,i)
			# solve one step
			self.solveAt(tstep)
			# do vtk export if right time steps
			self.export(i,doVtkExport)
	def export(self,i,doVtkExport=0):
		if self.exportFunction and (doVtkExport==0 or (doVtkExport!=0 and i%doVtkExport==0)):
			self.exportFunction(i,self.fem,self.dem)
######################################################################




######################################################################
class FemDemMeshMultiscaleMap:
	def __init__(self,fem,dem,getIPs,getRVEs):
		self.fem = fem
		self.dem = dem
		self.ips = getIPs(self.fem)
		self.rves = getRVEs(self.dem)
		assert len(self.ips) == len(self.rves)
		self.stresses, self.strains = [[Matrix3.Zero for _ in self.ips] for __ in (0,1)]
	def getStressFromDem(self):
		raise NotImplementedError
	def applyStressOnFem(self):
		raise NotImplementedError
	def getStrainFromFem(self):
		raise NotImplementedError
	def applyStrainOnDem(self):
		raise NotImplementedError
	def solveDem(self,tstep):
		raise NotImplementedError

class OofemYadeMeshMultiscaleMap(FemDemMeshMultiscaleMap):
	def __init__(self,*args):
		FemDemMeshMultiscaleMap.__init__(self,*args)
		liboofem = self.fem._lib
		self._IST_StrainTensor = liboofem.InternalStateType.IST_StrainTensor
		self._IST_StressTensor = liboofem.InternalStateType.IST_StressTensor
	def getStressFromDem(self):
		O = self.dem.omega
		utils = self.dem._lib.utils
		for rvei,rve in enumerate(self.rves):
			O.switchToScene(rve)
			stress = self._stressMatrix2Matrix(utils.getStress())
			self.stresses[rvei] = stress
	def applyStressOnFem(self):
		liboofem = self.fem._lib
		for ip,stress in zip(self.ips,self.stresses):
			ip = self.fem.giveIntegrationPoint(ip)
			val = self._stressMatrix2FloatArray(stress)
			mat.setIPValue(val,ip,self._IST_StressTensor)
	def getStrainFromFem(self):
		liboofem = self.fem._lib
		for i,ip in enumerate(self.ips):
			ip = self.fem.giveIntegrationPoint(ip)
			strain = liboofem.FloatArray()
			ip.giveMaterial().giveIPValue(strain,ip,self._IST_StrainTensor,None)
			strain = self._strainFloatArray2Matrix(strain)
			self.strains[i] = strain
	def applyStrainOnDem(self):
		O = self.dem.omega
		I = Matrix3.Identity
		for rve,strain in zip(self.rves,self.strains):
			O.switchToScene(rve)
			trsf1 = O.cell.trsf
			trsf2 = strain + I
			v = (trsf2*trsf1.inverse()-I)/O.dt
			O.cell.velGrad = v
	def _stressMatrix2FloatArray(self,stress):
		ret = self.fem._lib.FloatArray(6)
		for i,(j,k) in enumerate(((0,0),(1,1),(2,2),(1,2),(2,0),(0,1))):
			ret[i] = stress[j,k]
		return ret
	def _stressMatrix2Matrix(self,stress):
		return .5*(stress+stress.transpose())
	def _strainFloatArray2Matrix(self,strain):
		ret = Matrix3.Zero
		for i in (0,1,2):
			ret[i,i] = strain[i]
		for i,(j,k) in zip((3,4,5),((1,2),(2,0),(0,1))):
			ret[j,k] = ret[k,j] = .5*strain[i]
		return ret
	def solveDem(self,tstep):
		O = self.dem.omega
		for rve in self.rves:
			O.switchToScene(rve)
			self.dem.solve(tstep)

class FemDemMultiscaleCoupler:
	"""
	TODO
	"""
	def __init__(self,fem,dem,femDemMeshMap,exportFunction=None):
		self.fem = fem
		self.dem = dem
		self.femDemMeshMap = femDemMeshMap
		self.exportFunction = exportFunction
		#
		self.fem.initProblem()
	def solveAt(self,tstep):
		"""Solve one step"""
		# solve FEM and DEM part
		self.fem.solve(tstep)
		self.femDemMeshMap.solveDem(tstep)
		# apply stress from DEM to FEM
		self.femDemMeshMap.getStressFromDem()
		self.femDemMeshMap.applyStressOnFem()
		# apply strains from FEM to DEM
		self.femDemMeshMap.getStrainFromFem()
		self.femDemMeshMap.applyStrainOnDem()
	def solve(self,nSteps,dt,doVtkExport=0):
		"""Solve whole simulation"""
		for i in xrange(1,nSteps+1):
			# define one solution time step
			tstep = TimeStep(i*dt,dt,i)
			# solve one step
			self.solveAt(tstep)
			# do vtk export if right time steps
			self.export(i,doVtkExport)
	def export(self,i,doVtkExport=0):
		if self.exportFunction and (doVtkExport==0 or (doVtkExport!=0 and i%doVtkExport==0)):
			self.exportFunction(i,self.fem,self.dem)




######################################################################
class FemDemMeshContactMap:
	def __init__(self,fem,dem,bodies):
		self.fem = fem
		self.dem = dem
		self.bodies = bodies
		self.femMeshes = [None for _ in self.bodies]
		self.demMeshes = [None for _ in self.bodies]
	def getForcesFromDem(self):
		raise NotImplementedError
	def applyForcesOnFem(self):
		raise NotImplementedError
	def getDsplFromFem(self):
		raise NotImplementedError
	def applyDsplOnDem(self):
		raise NotImplementedError

class OofemYadeMeshContactMap(FemDemMeshContactMap):
	def __init__(self,*args):
		FemDemMeshContactMap.__init__(self,*args)
		flib = self.fem._lib
		dlib = self.dem._lib
		d = self.fem.problem.giveDomain(1)
		nfs = d.giveNumberOfFunctions() + 1
		d.resizeFunctions(nfs)
		d.setFunction(nfs,flib.constantFunction(nfs,d,f_t=1))
		def nLoad(i):
			ret = flib.NodalLoad(i,d)
			ca = flib.FloatArray(3)
			ca.zero()
			ret.setComponentArray(ca)
			ret.setFunction(nfs)
			return ret
		self.loads = {}
		for bi,vids in enumerate(self.bodies):
			mesh = self.fem.toUnstructuredGrid()
			mesh = mesh.getSubsetByVertices(vids)
			self.femMeshes[bi] = mesh
			vs = mesh.vertices
			nvs = len(vs)
			nbcs = d.giveNumberOfBoundaryConditions()
			d.resizeBoundaryConditions(nbcs+nvs)
			loads = [nLoad(nbcs+i+1) for i,v in enumerate(vs)]
			for v,load in zip(vs,loads):
				i = v.id
				n = d.giveDofManager(i)
				la = n.giveLoadArray()
				lenla = len(la)
				la.resize(lenla+1)
				la[lenla] = load.number
				d.setBoundaryCondition(load.number, load)
				self.loads[v.id] = load
			self.demMeshes[bi] = self.dem.addContactBody(mesh,mask=(1<<(1+bi))|1)
		#
		colliderFound = False
		for e in self.dem.omega.engines:
			if isinstance(e,dlib.Collider):
				colliderFound = True
				e.avoidSelfInteractionMask = 1
		assert colliderFound
		#
	def getForcesFromDem(self):
		self.forces = dict((v.id,Vector3.Zero) for mesh in self.femMeshes for v in mesh.vertices)
		for demMesh,femMesh in zip(self.demMeshes,self.femMeshes):
			for tetra,cell in zip(demMesh,femMesh.cells):
				intrs = tetra.intrs()
				if not intrs:
					continue
				vs = [v.coords+self.dspl[v.id] for v in cell.vertices]
				for intr in intrs:
					cp = intr.geom.contactPoint
					f = intr.phys.normalForce + intr.phys.shearForce
					f = f * (-1 if tetra.id == intr.id1 else +1 if tetra.id == intr.id2 else 'ERROR')
					ws = w1,w2,w3,w4 = self.tetraWeights(cell,vs,cp)
					for v,w in zip(cell.vertices,ws):
						self.forces[v.id] += f*w
	def tetraWeights(self,cell,vs,cp):
		v1,v2,v3,v4 = vs
		w1 = (cp-v2).cross(cp-v3).dot(cp-v4)
		w2 = (cp-v1).cross(cp-v4).dot(cp-v3)
		w3 = (cp-v1).cross(cp-v2).dot(cp-v4)
		w4 = (cp-v1).cross(cp-v3).dot(cp-v2)
		sws = sum((w1,w2,w3,w4))
		ws = [w/sws for w in (w1,w2,w3,w4)]
		return ws
	def applyForcesOnFem(self):
		for k,load in self.loads.iteritems():
			force = self.forces[k]
			ca = self.fem._lib.FloatArray(3)
			for i,v in enumerate(force):
				ca[i] = v
			load.setComponentArray(ca)
	def getDsplFromFem(self):
		p = self.fem.problem
		d = p.giveDomain(1)
		def v2d(v):
			lib = self.fem._lib
			n = d.giveDofManager(v.id)
			uv = lib.FloatArray()
			dm = lib.IntArray(3)
			dm[0] = lib.DofIDItem.D_u
			dm[1] = lib.DofIDItem.D_v
			dm[2] = lib.DofIDItem.D_w
			t = p.giveCurrentStep()
			n.giveUnknownVector(uv,dm,lib.ValueModeType.VM_Total,t,False)
			return Vector3(list(uv))
		self.dspl = dict((v.id,Vector3(v2d(v))) for mesh in self.femMeshes for v in mesh.vertices)
	def applyDsplOnDem(self):
		for demMesh,femMesh,dspl in zip(self.demMeshes,self.femMeshes,self.dspl):
			for tetra,cell in zip(demMesh,femMesh.cells):
				vs = v1,v2,v3,v4 = [v.coords+self.dspl[v.id] for v in cell.vertices]
				cc = .25*sum(vs,Vector3.Zero)
				v1,v2,v3,v4 = [v-cc for v in vs]
				tetra.shape.setVertices4(v1,v2,v3,v4)
				tetra.state.pos = cc
				tetra.state.ori = tetra.shape.GetOri()

class FemDemContactCoupler:
	"""
	TODO
	"""
	def __init__(self,fem,dem,femDemMeshMap,exportFunction=None):
		self.fem = fem
		self.dem = dem
		self.femDemMeshMap = femDemMeshMap
		self.exportFunction = exportFunction
		#
		self.fem.initProblem()
	def solveAt(self,tstep):
		"""Solve one step"""
		# solve FEM and DEM part
		self.fem.solve(tstep)
		self.dem.solve(tstep)
		# apply forces from DEM onto FEM
		self.femDemMeshMap.getForcesFromDem()
		self.femDemMeshMap.applyForcesOnFem()
		# apply displacement from FEM onto DEM
		self.femDemMeshMap.getDsplFromFem()
		self.femDemMeshMap.applyDsplOnDem()
	def solve(self,nSteps,dt,doVtkExport=0):
		"""Solve whole simulation"""
		for i in xrange(1,nSteps+1):
			# define one solution time step
			tstep = TimeStep(i*dt,dt,i)
			# solve one step
			self.solveAt(tstep)
			# do vtk export if right time steps
			self.export(i,doVtkExport)
	def export(self,i,doVtkExport=0):
		if self.exportFunction and (doVtkExport==0 or (doVtkExport!=0 and i%doVtkExport==0)):
			self.exportFunction(i,self.fem,self.dem)
######################################################################
