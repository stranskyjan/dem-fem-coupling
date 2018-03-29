############################################################
#
# TODO
#
############################################################
import liboofem

dx,dy = 1., .12 # dimensions
nx,ny = 25, 3 # number of elements per dimension

def createOofemNodes():
	ret = []
	i = 1
	nx1,ny1 = [v+1 for v in (nx,ny)]
	for yi in xrange(ny1):
		y = dy*(yi/float(ny))
		for xi in xrange(nx1):
			x = dx*(-.5+xi/float(nx))
			kw = dict(coords=(x,y,0))
			if xi in (0,nx):
				kw["bc"] = (1,1)
			ret.append(liboofem.node(i,domain,**kw))
			i += 1
	return ret

def createOofemElems():
	ret = []
	i = 1
	for yi in xrange(ny):
		for xi in xrange(nx):
			if xi in [nx/2+_ for _ in (-2,-1,0,1,2)]:
				continue
			n1 = yi*(nx+1) + xi + 1
			n2 = n1 + 1
			n4 = n1 + nx + 1
			n3 = n4 + 1
			nodes = (n1,n2,n3,n4)
			ret.append(liboofem.element('planeStress2d',i,domain,nodes=nodes,mat=1,crossSect=1))
			i += 1
	return ret
############################################################


############################################################
# engngModel
problem = liboofem.engngModel("nldeidynamic",1,nSteps=5,dumpCoef=0,deltaT=10000,outFile="/tmp/vol1_oofem.out")

# domain
domain = liboofem.domain(1, 1, problem, liboofem.domainType._2dPlaneStressMode, tstep_step=10000, dofman_all=True, element_all=True, numberOfSpatialDimensions=2)
problem.setDomain(1, domain, True)

# vtkxml
vtkxmlModule = liboofem.vtkxml(1,problem,tstep_step=10000,vars=[1,4],primvars=[1])
exportModuleManager = problem.giveExportModuleManager()
exportModuleManager.resizeModules(1)
exportModuleManager.setModule(1,vtkxmlModule)

# boundary condition and time function
ltf = liboofem.loadTimeFunction("pieceWiseLinFunction",1,nSteps=2,t=(0,1e-1),f_t=(0,1))
bc = liboofem.boundaryCondition(1, domain, loadTimeFunction=1, prescribedValue=0.0)

# nodes
nodes = createOofemNodes()

# material and cross section
mat = liboofem.isoLE(1, domain, d=2000, E=1e9, n=0.2, tAlpha=0)
cs  = liboofem.simpleCS(1, domain, thick=.01)

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
domain.setBoundaryCondition(1, bc)
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
