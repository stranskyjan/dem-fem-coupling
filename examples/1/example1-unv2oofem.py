######################################################################
#
# Python script to generate OOFEM input file - cantilever meshed
# with regular tetrahedrons. This cantilever will then be "bombarded"
# by spherical DEM particles from YADE
#
######################################################################
import os,sys

class FileReader:
	def __init__(self,fNname):
		self.f = open(fNname)
		self.line = ''
		self.ls = []
	def close(self):
		self.f.close()
	def readline(self):
		self.line = self.f.readline()
		self.ls = self.line.split()

f = FileReader('/tmp/example1.unv')
while not f.ls or f.ls[0]!='2411':
	f.readline()
nodes = []
f.readline()
while not (len(f.ls)==1 and f.ls[0]=='-1'):
	f.readline()
	nodes.append(tuple(float(w) for w in f.ls))
	f.readline()
while not (len(f.ls)==6 and f.ls[1]=='41'):
	f.readline()
faces = []
while not (len(f.ls)==6 and f.ls[1]=='111'):
	f.readline()
	faces.append(tuple(int(w) for w in f.ls))
	f.readline()
elems = []
while not (len(f.ls)==1 and f.ls[0]=='-1'):
	f.readline()
	elems.append(tuple(int(w) for w in f.ls))
	f.readline()
f.close()

fNodes = list(set(n for f in faces for n in f))

assert all(len(n)==3 for n in nodes)
assert all(len(e)==4 for e in elems)

nNodes = len(nodes)
nElems = len(elems)

base = ('/tmp/' if os.path.exists('/tmp') else '') + 'test-fem-dem-1-oofem'
if len(sys.argv) > 1:
	base = sys.argv[1]
outName = base + '.out'
inName  = base + '.in'
f = open(inName,'w')
f.write(outName+'\n')
f.write('surface fem - dem coupling test\n')
f.write('nldeidynamic nsteps 2 dumpcoef 0.03 deltat 0.1 nmodules 1\n')
f.write('vtkxml 1 tstep_step 0 domain_all vars 2 1 4 primvars 1 1 cellvars 1 102\n')
f.write('domain 3d\n')
f.write('OutputManager tstep_all dofman_all element_all\n')
f.write('ndofman %d nelem %d ncrosssect 1 nmat 1 nbc %d nic 0 nltf 1\n'%(nNodes,nElems,len(fNodes)+1))
for i,n in enumerate(nodes):
	loadStr = ' load 1 %d'%(fNodes.index(i)+2) if i in fNodes else ''
	f.write('node %d coords 3 %g %g %g%s%s\n'%(i+1,n[0],n[1],n[2],' bc 3 1 1 1' if n[2]==0 else '',loadStr))
for i,e in enumerate(elems):
	n1,n2,n3,n4 = [n for n in e]
	f.write('ltrspace %d nodes 4 %d %d %d %d crosssect 1 mat 1\n'%(i+1,n1,n2,n3,n4))
f.write('SimpleCS 1 thick 1 width 1\n')
f.write('IsoLE 1 tAlpha 0.000012 d 100e5 E 100e4 n 0.2\n')
f.write('BoundaryCondition 1 loadTimeFunction 1 prescribedvalue 0\n')
# write nodal load for each node
for i,n in enumerate(fNodes):
	f.write('NodalLoad %d loadTimeFunction 1 Components 3 0 0 0\n'%(i+2))
f.write('ConstantFunction 1 f(t) 1.0\n')
f.close()
