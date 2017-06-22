from yade import pack,export
from example2_common import *

base = '/tmp/example2'

matS,matF = materials()

sp = pack.SpherePack()
sp.makeCloud((0,0,0),(width,thick,width),rMean=particleRadius,num=1000,seed=1)
sp.toSimulation(material=matS)

#O.bodies.append(wall((0,0,0),2))
O.bodies.append((
	facet(((0,0,0),(width,0,0),(width,thick,0)),wire=False,material=matF),
	facet(((0,0,0),(width,thick,0),(0,thick,0)),wire=False,material=matF),
))

O.engines = engines()
O.periodic = True
O.cell.setBox(width,thick,2*max(width,thick))
O.dt = PWaveTimeStep()

O.run(20000,True)

box = box((.5*width,.5*thick,.7*width),.5*Vector3(sWidth,sThick,sHeight),material=matF)
box.state.blockedDOFs = 'xyXYZ'
box.state.vel = (0,0,-10)
O.bodies.append(box)

O.run(30000,True)

for b in O.bodies: b.state.pos = O.cell.wrap(b.state.pos)

export.text(base+'-spheres.dat')
f = open(base+'-sleeper.dat','w')
f.write('# z coordinate of bottom\n{}\n'.format(box.state.pos[2]-.5*sHeight))
f.close()
