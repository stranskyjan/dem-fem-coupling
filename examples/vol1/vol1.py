#####################################################
#
# volume fem-dem coupling test
#
#####################################################

# import interfaces
import liboofem
import libyade
from demfemcoupling import OofemInterface,YadeInterface,FemDemVolumeStrongCoupler,OofemYadeMeshVolumeMap

def vtkExport(i,fem,dem):
	"""Do VTK export"""
	fem.vtkExport(i)
	dem.vtkExport(i)

# initialize both domains
femName = 'vol1_oofem'
demName = 'vol1_yade'
fem = OofemInterface(femName,liboofem)
dem = YadeInterface(demName,libyade)

# create coupler object
femDemMeshMap = OofemYadeMeshVolumeMap(fem,dem)
coupler = FemDemVolumeStrongCoupler(fem,dem,femDemMeshMap,vtkExport)

# run the simulation
nSteps,dt,output = 2000,2e-6,20
coupler.solve(nSteps,dt,output)
