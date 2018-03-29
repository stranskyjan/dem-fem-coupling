import os
from paraview.simple import *
paraview.simple._DisableFirstRenderCameraReset()

directory = "/tmp"

renderView = GetActiveViewOrCreate('RenderView')

# FEM
fem = [os.path.join(directory,f) for f in os.listdir(directory) if f.startswith("vol1_oofem.out.m1.") and f.endswith(".vtu")]
fem.sort(key=lambda f: int(os.path.splitext(f)[0].rpartition(".")[2]))
fem = XMLUnstructuredGridReader(FileName=fem)

Show(fem, renderView)
warpByVector1 = WarpByVector(Input=fem)
warpByVector1Display = Show(warpByVector1, renderView)
Hide(fem, renderView)
warpByVector1Display.SetRepresentationType('Surface With Edges')

# DEM
dem = [os.path.join(directory,f) for f in os.listdir(directory) if f.startswith("vol1_yade-spheres-") and f.endswith(".vtk")]
dem.sort(key=lambda f: int(os.path.splitext(f)[0].rpartition("-")[2]))
dem = LegacyVTKReader(FileNames=dem)

Show(dem, renderView)
glyph1 = Glyph(Input=dem, GlyphType='Sphere')
glyph1.ScaleMode = 'scalar'
glyph1.ScaleFactor = 1.0
glyph1.GlyphType.Radius = 1.0
glyph1.GlyphType.ThetaResolution = 16
glyph1.GlyphType.PhiResolution = 16
glyph1.GlyphMode = 'All Points'

glyph1Display = Show(glyph1, renderView)
ColorBy(glyph1Display, ('POINTS', 'dmg'))

dmgLUT = GetColorTransferFunction('dmg')
dmgLUT.ApplyPreset('Blue to Red Rainbow', True)
dmgLUT.RescaleTransferFunction(0,.5)

dmgPWF = GetOpacityTransferFunction('dmg')
dmgPWF.RescaleTransferFunction(0,.5)

#
animationScene1 = GetAnimationScene()
animationScene1.UpdateAnimationUsingDataTimeSteps()

renderView.ResetCamera()
renderView.OrientationAxesVisibility = False
renderView.Background = [1.0, 1.0, 1.0]
renderView.ViewSize = [989, 322]
renderView.CameraPosition = [0.0, 0.0665725152939558, -1.9729839408780194]
renderView.CameraFocalPoint = [0.0, 0.0665725152939558, 0.0]
renderView.CameraViewUp = [0.0, 1.0, 0.0]
renderView.CameraParallelProjection = True
renderView.CameraParallelScale = 0.169536833167

RenderAllViews()
out = '/tmp/vol1.png'
WriteAnimation(out)
print 'animation saved to {}'.format(out)
print
