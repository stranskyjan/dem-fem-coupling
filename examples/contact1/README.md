A very basic example of contact coupling - thre elastic polyhedral particles interacting with each other.
Bodies are simulated by FEM, their contacts is evaluated by DEM.

### What is here

| file name | description |
| --- | --- |
| [Makefile](Makefile) | makefile for the example |
| [contact1.py](contact1.py) | main python script |
| [contact1_yade.py](contact1_yade.py)  | yade part of the simulation |
| [contact1_oofem.py](contact1_oofem.py)  | oofem part of the simulation |
| [contact1_profile.py](contact1_profile.py) | script for profiling evaluation |
| [contact1_pv.py](contact1_pv.py) | script for postprocessing (spherical case) |

### Running the example
Run the example by `make all` (or run `make help` for more options)

### Postprocessing
The postprocessing may be done by `pvpython contact1_pv.py` or `make pv`.
Or just open Paraview and then navigate to `Tools -> Python shell -> Run Script` and choose `contact1_pv.py` file.
