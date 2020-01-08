from __future__ import print_function
import os
from paraview.simple import *
paraview.simple._DisableFirstRenderCameraReset()

directory = "/tmp"

renderView = GetActiveViewOrCreate('RenderView')

# FEM
fem = [os.path.join(directory,f) for f in os.listdir(directory) if f.startswith("contact1_oofem.out.m1.") and f.endswith(".vtu")]
fem.sort(key=lambda f: int(os.path.splitext(f)[0].rpartition(".")[2]))
fem = XMLUnstructuredGridReader(FileName=fem)

femDisplay = Show(fem, renderView)
warpByVector1 = WarpByVector(Input=fem)
warpByVector1Display = Show(warpByVector1, renderView)
Hide(fem, renderView)

calculator1 = Calculator(Input=warpByVector1)
calculator1.ResultArrayName = 'MeanStress'
calculator1.Function = '(IST_StressTensor_0+IST_StressTensor_4+IST_StressTensor_8)/3'
calculator1Display = Show(calculator1, renderView)
Hide(warpByVector1, renderView)

meanStressLUT = GetColorTransferFunction('MeanStress')
meanStressLUT.ApplyPreset('Warm to Cool', True)
meanStressLUT.RescaleTransferFunction(-6e5, 6e5)

meanStressPWF = GetOpacityTransferFunction('MeanStress')
meanStressPWF.RescaleTransferFunction(-6e5, 6e5)


#
animationScene1 = GetAnimationScene()
animationScene1.UpdateAnimationUsingDataTimeSteps()

renderView.ResetCamera()
renderView.OrientationAxesVisibility = False
renderView.Background = [1.0, 1.0, 1.0]
renderView.ViewSize = [645, 548]
renderView.CameraPosition = [-12.237086971409381, 4.004962731028556, 10.085512231642257]
renderView.CameraFocalPoint = [2.4882931081962423, -0.5202588198537746, -1.426566096388525]
renderView.CameraViewUp = [0.41902160369138325, -0.5235980778928168, 0.7417991294594847]
renderView.CameraParallelScale = 4.86666879848

RenderAllViews()
out = '/tmp/contact1.png'
WriteAnimation(out)
print('animation saved to {}'.format(out))
print()
