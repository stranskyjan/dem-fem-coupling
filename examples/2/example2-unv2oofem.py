def readUnvFile(fName):
	nodes,elems = [],[]
	#
	f = open(fName)
	line = 'false'
	while line.strip().rstrip()!='2411':
		line = f.readline()
	line = f.readline()
	while line.strip().rstrip()!='-1':
		line = f.readline()
		nodes.append([float(w) for w in line.split()])
		line = f.readline()
	while line.strip().rstrip()!='2412':
		line = f.readline()
	line = f.readline()
	while line.strip().rstrip()!='-1':
		elemType = int(line.split()[1])
		line = f.readline()
		if elemType in (11,):
			line = f.readline()
		elif elemType == 111:
			elems.append([int(w) for w in line.split()])
		line = f.readline()
	f.close()
	return nodes,elems

sNodes,sElems = readUnvFile('/tmp/example2-sleeper.unv')
gNodes,gElems = readUnvFile('/tmp/example2-ground.unv')
nodes = sNodes + gNodes

minZ = min(n[2] for n in nodes)

lines = [
	'/tmp/example2-oofem.out',
	'surface fem - dem coupling test',
	'nldeidynamic nsteps 2 dumpcoef 0.03 deltat 0.1 nmodules 1',
	'vtkxml 1 tstep_step 0 domain_all vars 2 1 4 primvars 1 1 cellvars 1 102',
	'domain 3d',
	'OutputManager tstep_all dofman_all element_all',
	'ndofman {} nelem {} ncrosssect 2 nmat 2 nbc {} nic 0 nltf 2'.format(len(nodes),len(sElems)+len(gElems),len(nodes)+2),
]
lines.extend('node {} coords 3 {} {} {} load 1 {}{}'.format(i+1,x,y,z,i+2,' bc 3 1 1 1' if z==minZ else '') for i,(x,y,z) in enumerate(nodes))
lines.extend('ltrspace {} nodes 4 {} {} {} {} mat 1 crosssect 1 bodyLoads 1 {}'.format(i+1,n1,n2,n3,n4,len(nodes)+2) for i,(n1,n2,n3,n4) in enumerate(sElems))
ne = len(sElems)
nn = len(sNodes)
lines.extend('ltrspace {} nodes 4 {} {} {} {} mat 2 crosssect 2'.format(i+1+ne,n1+nn,n2+nn,n3+nn,n4+nn) for i,(n1,n2,n3,n4) in enumerate(gElems))
lines.extend((
	'SimpleCS 1 thick 1 width 1',
	'SimpleCS 2 thick 1 width 1',
	'IsoLE 1 tAlpha 0.000012 d 500e7 E 550e5 n 0.2',
	'IsoLE 2 tAlpha 0.000012 d 550e7 E 500e5 n 0.2',
))
lines.append('BoundaryCondition 1 loadTimeFunction 1 prescribedValue 0')
lines.extend('NodalLoad {} loadTimeFunction 1 Components 3 0 0 0'.format(i+2) for i,n in enumerate(nodes))
lines.append('DeadWeight {} loadTimeFunction 2 Components 3 0 0 -1e-5'.format(len(nodes)+2))
lines.append('ConstantFunction 1 f(t) 1.0')
lines.append('ConstantFunction 2 f(t) 1.0')

f = open('/tmp/example2-oofem.in','w')
f.writelines(line+'\n' for line in lines)
f.close()
