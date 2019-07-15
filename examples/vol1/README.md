A basic example of strong volume coupling - a simply supported beam subjected to an impact.
FEM is modeled by linear elastic material, central part (subjected to the impact) is modeled by a DEM model with damage and plasticity.

### What is here

| file name | description |
| --- | --- |
| [Makefile](Makefile) | makefile for the example |
| [vol1.py](vol1.py) | main python script |
| [vol1_yade.py](vol1_yade.py) | yade part of the simulation |
| [vol1_oofem.py](vol1_oofem.py) | oofem part of the simulation |
| [vol1_profile.py](vol1_profile.py) | script for profiling evaluation |
| [vol1_pv.py](vol1_pv.py) | script for postprocessing |

### Running the example
Run the example by `make all` (or run `make help` for more options)

### Postprocessing
The postprocessing may be done by `pvpython vol1_pv.py` or `make pv`.
Or just open Paraview and then navigate to `Tools -> Python shell -> Run Script` and choose `vol1_pv.py` file.
