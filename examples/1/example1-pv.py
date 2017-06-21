import os,sys
import subprocess
from paraview.simple import *

montage = True
doGif = True
doMovie = True
name = 'example1'
base = '/tmp/%s'%name

def runAndPrintCmd(cmd):
	print ' '.join(cmd)
	subprocess.Popen(cmd).wait()

def getTimes():
	fs = [f for f in os.listdir('/tmp') if f.startswith('example1-oofem.out.m0.') and f.endswith('.vtu')]
	ret = sorted([int(f.rpartition('.')[0].rpartition('.')[2]) for f in fs])
	return ret

def loadFEM(times,base=base):
	ret = XMLUnstructuredGridReader(FileName=['%s-oofem.out.m0.%d.vtu'%(base,t) for t in times])
	ret = WarpByVector(ret,Vectors='DisplacementVector',ScaleFactor=1)
	ret = ExtractSurface(ret)
	ret = GenerateSurfaceNormals(ret)
	return ret

def loadDEM(times,base=base):
	ret = LegacyVTKReader(FileNames=['%s-yade-spheres-%08d.vtk'%(base,t) for t in times])
	ret = Glyph(Input=ret,GlyphType='Sphere')
	ret.Scalars = ['POINTS', 'radius']
	ret.ScaleMode = 'scalar'
	ret.ScaleFactor = 1.0
	gt = ret.GlyphType
	gt.Radius = 1.
	gt.ThetaResolution = gt.PhiResolution = 24
	return ret

def color(fem,dem):
	Show(fem)
	dp = GetDisplayProperties(fem)
	lim = 1e5
	lut = MakeBlueToRedLT(-lim,lim)
	lut.VectorMode = 'Component'
	lut.VectorComponent = 8
	dp.LookupTable = lut
	dp.ColorArrayName = ('POINT_DATA','IST_StressTensor')
	#
	Show(dem)

def getView(viewSize=(640,480),focalPoint=(.5,.5,2.5),cameraRelativePosition=(20,0,0),cameraViewUp=(0,0,1)):
	view = GetRenderView()
	view.Background=(1,1,1)
	view.OrientationAxesVisibility = 0
	view.CenterAxesVisibility = 0
	view.ViewSize = viewSize
	view.CameraFocalPoint = focalPoint
	view.CameraPosition = [focalPoint[i]+cameraRelativePosition[i] for i in (0,1,2)]
	view.CameraViewUp = cameraViewUp
	Render()
	return view

def generatePicture(i,base=base):
	WriteImage('%s-%04d.png'%(base,i))
	

def main():
	times = getTimes()
	dem = loadDEM(times)
	fem = loadFEM(times)
	color(fem,dem)
	s1,f1 = 600,9
	s2,f2 = [v/3 for v in s1,f1]
	frame1 = '{0}x{0}+{1}+{1}'.format(f1,f1/3)
	frame2 = '{0}x{0}+{1}+{1}'.format(f2,f2/3)
	sizes = ((s1,s1),(s2,s2),(s2,s2),(s2,s2))
	poss = ((8,9,10),(-15,0,0),(0,-15,0),(0,0,15))
	ups = ((0,0,1),(0,0,1),(0,0,1),(1,0,0))
	labels = ('a','x','y','z')
	rtimes = xrange(len(times))
	rtiles = xrange(len(labels))
	getView(viewSize=sizes[0])
	for i,(size,pos,up,label) in enumerate(zip(sizes,poss,ups,labels)):
		view = getView(viewSize=size,cameraRelativePosition=pos,cameraViewUp=up)
		for j,t in enumerate(times):
			view.ViewTime = j
			generatePicture(j,base='%s-%d'%(base,i))
	if montage or doGif:
		for j,t in enumerate(times):
			#subprocess.Popen('montage -bordercolor white'.split() + sum((['-label',labels[i],'%s-%d-%04d.png'%(base,i,j)] for i in rtiles),[]) + ('-tile 2x2 -geometry %dx%d+10+10 -frame 5 -shadow'%(size[0],size[1])).split() + ['%s-%04d.png'%(base,j)]).wait()
			name = '%s-%04d.png'%(base,j)
			tmp = '/tmp/tmp.png'
			cmds = [
				'convert -size {0}x{1} xc:blue {2}'.format(s1+s2+2*(f1+f2),s1+2*f1,name),
				'convert {0} -frame {1} {2}'.format('{0}-{1}-{2:04d}.png'.format(base,0,j),frame1,tmp),
				'composite {0} {1} {1}'.format(tmp,name),
			]
			for i in (0,1,2):
				cmds.extend((
					'convert {0} -frame {1} {2}'.format('{0}-{1}-{2:04d}.png'.format(base,i+1,j),frame2,tmp),
					'composite {0} -geometry +{2}+{3} {1} {1}'.format(tmp,name,s1+2*f1,i*(s2+2*f2)),
				))
			for cmd in cmds:
				subprocess.Popen(cmd.split()).wait()
			#break
		if doGif:
			subprocess.Popen(['convert'] + ['%s-%04d.png'%(base,j) for j in rtimes] + '-loop 0 -delay 1'.split() + ['%s.gif'%(base)]).wait()
		if doMovie:
			name = '/tmp/example1.mp4'
			if os.path.exists(name):
				os.remove(name)
			subprocess.Popen('avconv -r 15 -i /tmp/example1-%04d.png -c:v libx264 {}'.format(name).split()).wait()

if __name__ == "__main__":
	main()
