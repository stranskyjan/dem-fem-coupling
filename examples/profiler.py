from pstats import Stats

class Stat:
	def __init__(self,nCalls,totTime):
		self.nCalls = int(nCalls)
		self.totTime = float(totTime)
	def __str__(self):
		return '{:6d}  {:.4e}'.format(self.nCalls,self.totTime)

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
	def getKeyByNameAndLine(self,name,line):
		ks = [k for k in self.stats.iterkeys() if any(name in kk for kk in k if isinstance(kk,str))]
		ks = [k for k in ks if line in k]
		assert len(ks) == 1
		k = ks[0]
		v = self.stats[k]
		return Stat(v[0],v[3])
		
class StatsPrinter:
	def __init__(self,totalTime,ljust=30):
		self.totalTime = totalTime
		self.ljust = ljust
		self.items = []
	def add(self,description,time):
		self.items.append((description,time))
	def pprint(self):
		print
		for desc,time in self.items:
			desc = "{}:".format(desc).ljust(self.ljust)
			print '{} {:10.4f} s  ({:6.2f} %)'.format(desc,time,100.*time/self.totalTime)
