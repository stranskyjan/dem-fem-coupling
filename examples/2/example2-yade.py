from libyade import yade
from yade import *
from yade import ymport
from example2_common import *

# basic material
matS,matF = materials()

# standard YADE engines
O.engines = engines()

O.bodies.append(ymport.text('example2-spheres.dat',material=matS))

O.periodic = True
O.cell.setBox(width,thick,2*max(width,thick))
