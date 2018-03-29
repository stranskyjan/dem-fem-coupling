######################################################################
#
# TODO
#
######################################################################
import os
from math import pi,sin,cos
from minieigen import Vector3
import liboofem

# sphere data
resolution = 1
sphereVals = ( # (center,radius,vel,resolution)
	((0, 0,0  ), 1, (0  , 0 ,0), resolution),
	((2, 1,0.6), 1, (-5,-5,0), resolution),
	((1,-4,0.4), 2, (0  , 8,0), resolution),
)

def sphere(center,radius,resolution=1):
	center = Vector3(center)
	vertices = [
		Vector3(+1,  0,  0),
		Vector3(-1,  0,  0),
		Vector3( 0, +1,  0),
		Vector3( 0, -1,  0),
		Vector3( 0,  0, +1),
		Vector3( 0,  0, -1),
	]
	cells = [
		( 0, 4, 2 ),
		( 2, 4, 1 ),
		( 1, 4, 3 ),
		( 3, 4, 0 ),
		( 0, 2, 5 ),
		( 2, 1, 5 ),
		( 1, 3, 5 ),
		( 3, 0, 5 ),
	]
	#
	for r in xrange(resolution):
		newCells = []
		centers = {}
		for i1,i2,i3 in cells:
			v1,v2,v3 = [vertices[i] for i in (i1,i2,i3)]
			iExtra = 3*[None]
			for index in (0,1,2):
				i = (i1,i2,i3)[index]
				j = (i1,i2,i3)[(index+1)%3]
				bij = centers.get((i,j))
				bji = centers.get((j,i))
				if bij or bji:
					iExtra[index] = centers[(i,j)] if bij else centers[(j,i)]
				else:
					ii = len(vertices)
					iExtra[index] = ii
					nn = (vertices[i] + vertices[j]).normalized()
					centers[(i,j)] = ii
					vertices.append(nn)
			i4,i5,i6 = iExtra
			newCells.extend((
				(i1,i4,i6),
				(i4,i2,i5),
				(i5,i3,i6),
				(i4,i5,i6),
			))
		cells = newCells
	vertices = [center + v*radius for v in vertices]
	return vertices,cells

def createNodesAndElemsAndIcs(data):
	nodes, elems, ics = [], [], []
	for spherei,(center,r,vel,resolution) in enumerate(data):
		vertices, cells = sphere(center,r,resolution)
		nNodes, nElems, nIcs = [len(_) for _ in (nodes,elems,ics)]
		ic = [3*spherei+i for i in (1,2,3)]
		nodes.append(liboofem.node(nNodes+1,domain,coords=list(center),ic=ic))
		for i,v in enumerate(vertices):
			nodes.append(liboofem.node(nNodes+2+i,domain,coords=list(v),ic=ic))
		for i,c in enumerate(cells):
			ns = [nNodes+2+_ for _ in c] + [nNodes+1]
			elems.append(liboofem.element("ltrspace",nElems+1+i,domain,nodes=ns,crosssect=1,mat=1,nlgeo=1))
		for i,v in enumerate(vel):
			ics.append(liboofem.initialCondition("initialCondition",nIcs+1+i,domain,conditions=1,v=v))
	return nodes, elems, ics

# engngModel
problem = liboofem.engngModel("nldeidynamic",1,nSteps=10,dumpCoef=0,deltaT=1,outFile="/tmp/contact1_oofem.out")

# domain
domain = liboofem.domain(1, 1, problem, liboofem.domainType._3dMode, tstep_step=10000, dofman_all=True, element_all=True)
problem.setDomain(1, domain, True)

# vtkxml
vtkxmlModule = liboofem.vtkxml(1,problem,tstep_step=10000,vars=[1,4],primvars=[1])
exportModuleManager = problem.giveExportModuleManager()
exportModuleManager.resizeModules(1)
exportModuleManager.setModule(1,vtkxmlModule)

# boundary condition and time function
ltf = liboofem.loadTimeFunction("ConstantFunction",1,f_t=1.)

# material and cross section
mat = liboofem.isoLE(1, domain, d=3000, E=3e6, n=0.2, tAlpha=0)
cs  = liboofem.simpleCS(1, domain)

nodes, elems, ics = createNodesAndElemsAndIcs(sphereVals)

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
#domain.resizeBoundaryConditions(1)
#domain.setBoundaryCondition(1, bc)
domain.resizeInitialConditions(len(ics))
for ic in ics:
	domain.setInitialCondition(ic.number, ic)
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
