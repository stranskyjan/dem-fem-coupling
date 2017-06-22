import itertools
#
import salome
from salome.geom import geomBuilder
geompy = geomBuilder.New(salome.myStudy)
import SMESH,StdMeshers
from salome.smesh import smeshBuilder
smesh = smeshBuilder.New(salome.myStudy)
#
from example2_common import *

def createMesh((x0,y0,z0),(dimx,dimy,dimz),(nx,ny,nz)):
	nodes = [geompy.MakeVertex(x0+i*dimx,y0+j*dimy,z0+k*dimz) for k,j,i in itertools.product(*[(0,1) for l in (0,1,2)])]
	edgesX = [geompy.MakeEdge(nodes[i],nodes[j]) for i,j in ((0,1),(2,3),(4,5),(6,7))]
	edgesY = [geompy.MakeEdge(nodes[i],nodes[j]) for i,j in ((0,2),(1,3),(4,6),(5,7))]
	edgesZ = [geompy.MakeEdge(nodes[i],nodes[j]) for i,j in ((0,4),(1,5),(2,6),(3,7))]
	edges = edgesX + edgesY + edgesZ
	faces = [geompy.MakeFaceWires([edges[i] for i in ii],True) for ii in ((0,1,4,5),(2,3,6,7),(0,2,8,9),(4,6,8,10),(1,3,10,11),(5,7,9,11))]
	solid = geompy.MakeSolid((geompy.MakeShell(faces),))
	
	geompy.addToStudy(solid,"solid")
	
	mesh = smesh.Mesh(solid)
	mesh.Segment().NumberOfSegments(nz)
	for e in edgesX: mesh.Segment(e).NumberOfSegments(nx)
	for e in edgesY: mesh.Segment(e).NumberOfSegments(ny)
	mesh.Quadrangle()
	mesh.Hexahedron()
	mesh.Compute()
	mesh.SplitVolumesIntoTetra(mesh.GetElementsId())
	return mesh

x,y,z = sWidth,sThick,sHeight # dimensions
nx,ny,nz = 3,3,3 # number of elements per dimension
f = open('example2-sleeper.dat')
f.readline()
z0 = float(f.readline().strip().rstrip())
f.close()
mesh = createMesh((.5*(width-sWidth),.5*(thick-sThick),z0),(x,y,z),(nx,ny,nz))
mesh.ExportUNV('/tmp/example2-sleeper.unv')

x,y,z = width,thick,-1 # dimensions
nx,ny,nz = 3,3,3 # number of elements per dimension
mesh = createMesh((0,0,0),(x,y,z),(nx,ny,nz))
mesh.ExportUNV('/tmp/example2-ground.unv')

if salome.sg.hasDesktop():
	salome.sg.updateObjBrowser(1)
