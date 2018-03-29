#####################################################
#
# surface fem-dem coupling test
#
#####################################################

# import interfaces
import liboofem
import libyade
from demfemcoupling import OofemInterface,YadeInterface,OofemYadeMeshSurfaceMap,FemDemSurfaceCoupler,TimeStep

def vtkExport(i,fem,dem):
	"""Do VTK export"""
	fem.vtkExport(i)
	dem.vtkExport(i)

# initialize both domains
femName = 'surf1_oofem'
demName = 'surf1_yade'
fem = OofemInterface(femName,liboofem)
dem = YadeInterface(demName,libyade)

# create coupler object
femSurf = fem.toUnstructuredGrid().getSurface()
demSurf = dem.addSurface(femSurf)
femDemMeshMap = OofemYadeMeshSurfaceMap(fem,dem,femSurf,demSurf)
coupler = FemDemSurfaceCoupler(fem,dem,femDemMeshMap,vtkExport)

# run the simulation
nSteps,dt,output = 300,.005,5
coupler.solve(nSteps,dt,output)
