############################################################
#
# TODO
#
############################################################
import liboofem


############################################################
class Node:
	def __init__(self,id,coords):
		self.id = id
		self.coords = list(coords)
		self.bcs = [0,0,0]
	def toOofem(self):
		kw = dict(coords=self.coords)
		if any(self.bcs):
			kw["bc"] = self.bcs
		return liboofem.node(self.id,domain,**kw)

class Brick:
	def __init__(self,id,nodes):
		self.id = id
		self.nodes = list(nodes)
	def toOofem(self):
		return liboofem.element("LSpace",self.id, domain, nodes=self.nodes, mat=1, crossSect=1, nlgeo=1)

dx,dy,dz = 1., 1., 5. # dimensions
nx,ny,nz = 3, 3, 15 # number of elements per dimension

def createOofemNodes():
	xs, ys, zs = [[i*d/n for i in xrange(n+1)] for d,n in zip((dx,dy,dz),(nx,ny,nz))]
	nodes = [Node(-1,(x,y,z)) for z in zs for y in ys for x in xs]
	for i,n in enumerate(nodes):
		n.id = i+1
		if n.coords[2] == 0.:
			n.bcs = [1,1,1]
	return [n.toOofem() for n in nodes]

def createOofemElems():
	elems = []
	nx1 = nx + 1
	nx1ny1 = (nx+1)*(ny+1)
	for ix in xrange(nx):
		for iy in xrange(ny):
			for iz in xrange(nz):
				n5 = 1 + ix + nx1*iy + nx1ny1*iz
				n8 = n5 + 1
				n6 = n5 + nx1
				n7 = n6 + 1
				n1 = n5 + nx1ny1
				n2 = n6 + nx1ny1
				n3 = n7 + nx1ny1
				n4 = n8 + nx1ny1
				elems.append(Brick(-1,(n1,n2,n3,n4,n5,n6,n7,n8)))
	for i,e in enumerate(elems):
		e.id = i+1
	return [e.toOofem() for e in elems]
############################################################


############################################################
# engngModel
problem = liboofem.engngModel("nldeidynamic",1,nSteps=5,dumpCoef=.1,deltaT=10000,outFile="/tmp/surf1_oofem.out")

# domain
domain = liboofem.domain(1, 1, problem, liboofem.domainType._3dMode, tstep_step=10000, dofman_all=True, element_all=True)
problem.setDomain(1, domain, True)

# vtkxml
vtkxmlModule = liboofem.vtkxml(1,problem,tstep_step=10000,vars=[1,4],primvars=[1])
exportModuleManager = problem.giveExportModuleManager()
exportModuleManager.resizeModules(1)
exportModuleManager.setModule(1,vtkxmlModule)

# boundary condition and time function
ltf = liboofem.loadTimeFunction("constantFunction",1,f_t=0)
bc = liboofem.boundaryCondition(1, domain, loadTimeFunction=1, prescribedValue=0.0)

# nodes
nodes = createOofemNodes()

# material and cross section
mat = liboofem.isoLE(1, domain, d=2000, E=5e6, n=0.2, tAlpha=0)
cs  = liboofem.simpleCS(1, domain)

# elements
elems = createOofemElems()

# add eveything to domain (resize container first)
domain.resizeDofManagers(len(nodes))
for n in nodes:
	domain.setDofManager(n.number, n)
domain.resizeElements(len(elems))
for e in elems:
	domain.setElement(e.number, e)
domain.resizeMaterials(1)
domain.setMaterial(1, mat)
domain.resizeCrossSectionModels(1)
domain.setCrossSection(1, cs)
domain.resizeBoundaryConditions(1)
domain.setBoundaryCondition(bc.number, bc)
domain.resizeFunctions(1)
domain.setFunction(ltf.number, ltf)

vtkxmlModule.initialize() # (!)
############################################################

def vtkExport(i):
	problem.giveExportModuleManager().giveModule(1).doForcedOutput(problem.giveCurrentStep())

if __name__ == "__main__":
	problem.checkProblemConsistency();
	problem.init();
	problem.postInitialize();
	problem.setRenumberFlag();
	problem.solveYourself();
	problem.terminateAnalysis();
