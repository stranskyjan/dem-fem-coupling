############################################################
#
# TODO
#
############################################################
import liboofem

############################################################
# engngModel
problem = liboofem.engngModel("nldeidynamic",1,nSteps=5,dumpCoef=30,deltaT=10000,outFile="/tmp/multi1_oofem.out")

# domain
domain = liboofem.domain(1, 1, problem, liboofem.domainType._3dMode, tstep_step=10000, dofman_all=True, element_all=True)
problem.setDomain(1, domain, True)

# vtkxml
vtkxmlModule = liboofem.vtkxml(1,problem,tstep_step=10000,vars=[1,4],primvars=[1],cellvars=[47])
exportModuleManager = problem.giveExportModuleManager()
exportModuleManager.resizeModules(1)
exportModuleManager.setModule(1,vtkxmlModule)

# boundary condition and time function
ltf = liboofem.loadTimeFunction("pieceWiseLinFunction",1,nSteps=2,t=(0,2e-1),f_t=(0,1))
bcs = [liboofem.boundaryCondition(i+1, domain, loadTimeFunction=1, prescribedValue=v) for i,v in enumerate((0,-1.0))]

# nodes
nodes = (
	liboofem.node( 1, domain, coords=(0,0,3), bc=(1,1,2)),
	liboofem.node( 2, domain, coords=(0,1,3), bc=(1,1,2)),
	liboofem.node( 3, domain, coords=(1,1,3), bc=(1,1,2)),
	liboofem.node( 4, domain, coords=(1,0,3), bc=(1,1,2)),
	liboofem.node( 5, domain, coords=(0,0,2), bc=(1,1,0)),
	liboofem.node( 6, domain, coords=(0,1,2), bc=(1,1,0)),
	liboofem.node( 7, domain, coords=(1,1,2), bc=(1,1,0)),
	liboofem.node( 8, domain, coords=(1,0,2), bc=(1,1,0)),
	liboofem.node( 9, domain, coords=(0,0,1), bc=(1,1,0)),
	liboofem.node(10, domain, coords=(0,1,1), bc=(1,1,0)),
	liboofem.node(11, domain, coords=(1,1,1), bc=(1,1,0)),
	liboofem.node(12, domain, coords=(1,0,1), bc=(1,1,0)),
	liboofem.node(13, domain, coords=(0,0,0), bc=(1,1,1)),
	liboofem.node(14, domain, coords=(0,1,0), bc=(1,1,1)),
	liboofem.node(15, domain, coords=(1,1,0), bc=(1,1,1)),
	liboofem.node(16, domain, coords=(1,0,0), bc=(1,1,1)),
)

# material and cross section
materials = [liboofem.material(matType, i+1, domain, d=2000, E=4e6, n=0.2, tAlpha=0) for i,matType in enumerate(("isole","structmatsettable","structmatsettable"))]
crosssects = [liboofem.simpleCS(i) for i in (1,2,3)]

# elements
elems = (
	liboofem.element("lspace", 1, domain, nodes=(1 ,2 ,3 ,4 ,5 ,6 ,7 ,8 ), mat=1, crosssect=1),
	liboofem.element("lspace", 2, domain, nodes=(5 ,6 ,7 ,8 ,9 ,10,11,12), mat=2, crosssect=2),
	liboofem.element("lspace", 3, domain, nodes=(9 ,10,11,12,13,14,15,16), mat=3, crosssect=3),
)

# add eveything to domain (resize container first)
domain.resizeDofManagers(len(nodes))
for n in nodes:
	domain.setDofManager(n.number, n)
domain.resizeElements(len(elems))
for e in elems:
	domain.setElement(e.number, e)
domain.resizeMaterials(len(materials))
for m in materials:
	domain.setMaterial(m.number, m)
domain.resizeCrossSectionModels(len(crosssects))
for cs in crosssects:
	domain.setCrossSection(cs.number, cs)
domain.resizeBoundaryConditions(len(bcs))
for bc in bcs:
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
