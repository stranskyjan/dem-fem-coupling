import os
from paraview.simple import *
paraview.simple._DisableFirstRenderCameraReset()

directory = "/tmp"

renderView = GetActiveViewOrCreate('RenderView')

# FEM
fem = [os.path.join(directory,f) for f in os.listdir(directory) if f.startswith("multi1_oofem.out.m1.") and f.endswith(".vtu")]
fem.sort(key=lambda f: int(os.path.splitext(f)[0].rpartition(".")[2]))
fem = XMLUnstructuredGridReader(FileName=fem)

Show(fem, renderView)
warpByVector1 = WarpByVector(Input=fem)
warpByVector1Display = Show(warpByVector1, renderView)
Hide(fem, renderView)
warpByVector1Display.SetRepresentationType('Surface With Edges')
ColorBy(warpByVector1Display, ('CELLS', 'IST_ElementNumber'))

iSTElementNumberLUT = GetColorTransferFunction('ISTElementNumber')
iSTElementNumberLUT.RGBPoints = [1.0, 0.0, 0.0, 1.0, 3.0, 1.0, 0.0, 0.0]
iSTElementNumberLUT.ColorSpace = 'HSV'
iSTElementNumberLUT.NanColor = [0.498039215686, 0.498039215686, 0.498039215686]
iSTElementNumberLUT.ScalarRangeInitialized = 1.0

iSTElementNumberPWF = GetOpacityTransferFunction('ISTElementNumber')
iSTElementNumberPWF.Points = [1.0, 0.0, 0.5, 0.0, 3.0, 1.0, 0.5, 0.0]
iSTElementNumberPWF.ScalarRangeInitialized = 1

# DEM
scale = 10
sNumbers = (0,15)
colors = ([0,1,0],[1,0,0])
translates = (
	[1.6,0,1.5],
	[1.6,0,0],
)
for si,color,translate in zip(sNumbers,colors,translates):
	dem = [os.path.join(directory,f) for f in os.listdir(directory) if f.startswith("multi1_yade_{:02d}-spheres-".format(si)) and f.endswith(".vtk")]
	dem.sort(key=lambda f: int(os.path.splitext(f)[0].rpartition("-")[2]))
	dem = LegacyVTKReader(FileNames=dem)

	Show(dem, renderView)
	transform = Transform(Input=dem)
	transform.Transform.Translate = translate
	transform.Transform.Scale = [scale, scale, scale]
	Show(transform, renderView)
	Hide(dem, renderView)
	warpByVector = WarpByVector(Input=transform)
	warpByVector1Display = Show(warpByVector, renderView)
	Hide(transform, renderView)

	glyph = Glyph(Input=warpByVector, GlyphType='Sphere')
	glyph.ScaleMode = 'scalar'
	glyph.ScaleFactor = 1.0
	glyph.GlyphMode = 'All Points'
	glyph.GlyphType.Radius = scale
	glyphDisplay = Show(glyph, renderView)

	ColorBy(glyphDisplay, None)
	glyphDisplay.DiffuseColor = color

#
animationScene1 = GetAnimationScene()
animationScene1.UpdateAnimationUsingDataTimeSteps()

renderView.ResetCamera()
renderView.OrientationAxesVisibility = False
renderView.Background = [1.0, 1.0, 1.0]
renderView.ViewSize = [428, 548]
renderView.CameraPosition = [3.6558879766724983, -5.2106182818586655, 5.193735858419548]
renderView.CameraFocalPoint = [0.27976130263734367, 2.5505922718539926, 0.06878277453619042]
renderView.CameraViewUp = [-0.26032674849797094, 0.4506222789831797, 0.8539142496178874]
renderView.CameraParallelScale = 2.59498903919

RenderAllViews()
out = '/tmp/multi1.png'
WriteAnimation(out)
print 'animation saved to {}'.format(out)
print
