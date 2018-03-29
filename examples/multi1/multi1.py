#####################################################
#
# multiscale fem-dem coupling test
#
#####################################################

# import interfaces
import liboofem
import libyade
from demfemcoupling import OofemInterface,YadeInterface,OofemYadeMeshMultiscaleMap,FemDemMultiscaleCoupler, TimeStep

def vtkExport(i,fem,dem):
	"""Do VTK export"""
	fem.vtkExport(i)
	dem.vtkExport(i)

# initialize both domains
femName = 'multi1_oofem'
demName = 'multi1_yade'
fem = OofemInterface(femName,liboofem)
dem = YadeInterface(demName,libyade)

# create coupler object
getIPs = lambda fem: [(i,j) for i in (2,3) for j in xrange(8)]
getRVEs = lambda dem: range(16)
femDemMeshMap = OofemYadeMeshMultiscaleMap(fem,dem,getIPs,getRVEs)
coupler = FemDemMultiscaleCoupler(fem,dem,femDemMeshMap,vtkExport)

nSteps,dt,output = 1000,2e-4,20
coupler.solve(nSteps,dt,output)
