#####################################################
#
# contact fem-dem coupling test
#
#####################################################
import liboofem
import libyade
from demfemcoupling import OofemInterface,YadeInterface,OofemYadeMeshContactMap,FemDemContactCoupler

def vtkExport(i,fem,dem):
	"""Do VTK exprort"""
	fem.vtkExport(i)
	dem.vtkExport(i)

# initialize both domains
femName = 'contact1_oofem'
demName = 'contact1_yade'
fem = OofemInterface(femName,liboofem)
dem = YadeInterface(demName,libyade)
mesh = fem.toUnstructuredGrid()
# bodies is tuple of lists. Each list contains indices of elements belonging to one macroparticle (thus prevent cotnact search between elements belonging to one physical grain)
n = fem.numberOfNodes() / 3
bodies = [range(i-n+1,i+1) for i in [j*n for j in (1,2,3)]]
# create coupler object
femDemMeshMap = OofemYadeMeshContactMap(fem,dem,bodies)
coupler = FemDemContactCoupler(fem,dem,femDemMeshMap,vtkExport)


# run the simulation
nSteps,dt,output = 1000,5e-4,10
coupler.solve(nSteps,dt,output)
