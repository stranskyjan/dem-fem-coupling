import os
from paraview.simple import *
paraview.simple._DisableFirstRenderCameraReset()

directory = "/tmp"

renderView = GetActiveViewOrCreate('RenderView')

# FEM
fem = [os.path.join(directory,f) for f in os.listdir(directory) if f.startswith("surf1_oofem.out.m1.") and f.endswith(".vtu")]
fem.sort(key=lambda f: int(os.path.splitext(f)[0].rpartition(".")[2]))
fem = XMLUnstructuredGridReader(FileName=fem)

Show(fem, renderView)
warpByVector1 = WarpByVector(Input=fem)
warpByVector1Display = Show(warpByVector1, renderView)
Hide(fem, renderView)

warpByVector1Display.SetRepresentationType('Surface With Edges')
ColorBy(warpByVector1Display, ('POINTS', 'IST_StressTensor', '8'))

iSTStressTensorLUT = GetColorTransferFunction('IST_StressTensor')
iSTStressTensorLUT.ApplyPreset('Warm to Cool', True)
iSTStressTensorLUT.RescaleTransferFunction(-300000.0, 300000.0)

iSTStressTensorPWF = GetOpacityTransferFunction('IST_StressTensor')
iSTStressTensorPWF.RescaleTransferFunction(-300000.0, 300000.0)

# DEM
dem = [os.path.join(directory,f) for f in os.listdir(directory) if f.startswith("surf1_yade-polyhedra-") and f.endswith(".vtk")]
dem.sort(key=lambda f: int(os.path.splitext(f)[0].rpartition("-")[2]))
dem = LegacyVTKReader(FileNames=dem)

demDisplay = Show(dem, renderView)
demDisplay.DiffuseColor = [0.0, 1.0, 0.0]

#
animationScene1 = GetAnimationScene()
animationScene1.UpdateAnimationUsingDataTimeSteps()

renderView.ResetCamera()
renderView.OrientationAxesVisibility = False
renderView.Background = [1.0, 1.0, 1.0]
renderView.ViewSize = [474, 548]
renderView.CameraPosition = [7.8029616470500915, 8.858484987384191, 9.945675581791892]
renderView.CameraFocalPoint = [-1.8370059490306845, -3.5367321192680237, 0.2949642841787113]
renderView.CameraViewUp = [-0.38150589364577026, -0.36463260906762174, 0.8494093909994647]
renderView.CameraParallelScale = 0

RenderAllViews()
out = '/tmp/surf1.png'
WriteAnimation(out)
print 'animation saved to {}'.format(out)
print
