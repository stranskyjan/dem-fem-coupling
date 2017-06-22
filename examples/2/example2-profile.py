from pstats import Stats

class Stat:
	def __init__(self,nCalls,totTime):
		self.nCalls = int(nCalls)
		self.totTime = float(totTime)
	def __str__(self):
		return '%6d  %.4e'%(self.nCalls,self.totTime)

class StatsWrapper:
	def __init__(self,fName):
		self.stats = Stats(fName).stats
	def getKeyByName(self,*names):
		ks = [k for k in self.stats.iterkeys() if all(any(n in kk for kk in k if isinstance(kk,str)) for n in names)]
		if len(ks) > 1:
			ks = [k for k in ks if all(n in k for n in names)]
		if len(ks) != 1:
			for k in ks: print k
			raise RuntimeError
		assert len(ks) == 1
		k = ks[0]
		v = self.stats[k]
		return Stat(v[0],v[3])

stats = StatsWrapper('/tmp/example2.pro')
tot = stats.getKeyByName('solveAt','example2.py')
oofemSolve           = stats.getKeyByName('solve','oofem')
oofemUpdateField     = stats.getKeyByName('updateField','oofem')
oofemUpdateFromField = stats.getKeyByName('updateFromField','oofem')
yadeSolve           = stats.getKeyByName('solve','yade')
yadeUpdateField     = stats.getKeyByName('updateField','yade')
yadeUpdateFromField = stats.getKeyByName('updateFromField','yade')
print
print 'total time for solution: %g s'%tot.totTime
print 'oofem solve:             %g s'%oofemSolve.totTime
print 'oofem exchange:          %g s'%sum(s.totTime for s in (oofemUpdateField,oofemUpdateFromField))
print 'yade solve:              %g s'%yadeSolve.totTime
print 'yade exchange:           %g s'%sum(s.totTime for s in (yadeUpdateField,yadeUpdateFromField))
