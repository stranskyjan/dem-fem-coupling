A basic example of multiscale coupling - oedometric compression.
Overall the domain is modeled with FEM, constitutive law of selected integration points is modeled by DEM.

### What is here

| file name | description |
| --- | --- |
| [Makefile](Makefile) | makefile for the example |
| [multi1.py](multi1.py) | main python script |
| [multi1_yade.py](multi1_yade.py) | yade part of the simulation |
| [multi1_oofem.py](multi1_oofem.py) | oofem part of the simulation |
| [multi1_profile.py](multi1_profile.py) | script for profiling evaluation |
| [multi1_pv.py](multi1_pv.py) | script for postprocessing |

### Running the example
Run the example by `make all` (or run `make help` for more options)

### Postprocessing
The postprocessing may be done by `pvpython multi1_pv.py` or `make pv`.
Or just open Paraview and then navigate to `Tools -> Python shell -> Run Script` and choose `multi1_pv.py` file.
