######################################################################
#
# Python script to generate OOFEM input file - cantilever meshed
# with regular tetrahedrons. This cantilever will then be "bombarded"
# by spherical DEM particles from YADE
#
######################################################################
import itertools
#
import salome
from salome.geom import geomBuilder
geompy = geomBuilder.New(salome.myStudy)
import SMESH,StdMeshers
from salome.smesh import smeshBuilder
smesh = smeshBuilder.New(salome.myStudy)

x,y,z = 1,1,5 # dimensions
nx,ny,nz = 3,3,15 # number of elements per dimension
#nx,ny,nz = 1,1,1

nodes = [geompy.MakeVertex(i*x,j*y,k*z) for k,j,i in itertools.product(*[(0,1) for l in (0,1,2)])]
edgesX = [geompy.MakeEdge(nodes[i],nodes[j]) for i,j in ((0,1),(2,3),(4,5),(6,7))]
edgesY = [geompy.MakeEdge(nodes[i],nodes[j]) for i,j in ((0,2),(1,3),(4,6),(5,7))]
edgesZ = [geompy.MakeEdge(nodes[i],nodes[j]) for i,j in ((0,4),(1,5),(2,6),(3,7))]
edges = edgesX + edgesY + edgesZ
faces = [geompy.MakeFaceWires([edges[i] for i in ii],True) for ii in ((0,1,4,5),(2,3,6,7),(0,2,8,9),(4,6,8,10),(1,3,10,11),(5,7,9,11))]
solid = geompy.MakeSolid((geompy.MakeShell(faces),))

"""
for i,n in enumerate(nodes):
	geompy.addToStudy(n,"n%02d"%i)
for i,e in enumerate(edges):
	geompy.addToStudy(e,"e%02d"%i)
for i,f in enumerate(faces):
	geompy.addToStudy(f,"f%02d"%i)
"""
geompy.addToStudy(solid,"solid")

mesh = smesh.Mesh(solid)
mesh.Segment().NumberOfSegments(nz)
for e in edgesX: mesh.Segment(e).NumberOfSegments(nx)
for e in edgesY: mesh.Segment(e).NumberOfSegments(ny)
mesh.Quadrangle()
mesh.Hexahedron()
mesh.Compute()
mesh.SplitVolumesIntoTetra(mesh.GetElementsId())
mesh.ExportUNV('/tmp/example1.unv')


if salome.sg.hasDesktop():
	salome.sg.updateObjBrowser(1)
