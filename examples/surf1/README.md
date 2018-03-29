A very basic example of surface coupling - three DEM particles (either spheres or polyhedra) "bombarding" a FEM cantilever.
The spherical os polyhedral case is set in [surf1_yade.py](surf1_yade.py) by `usePolyhedra` variable.

### What is here

| file name | description |
| --- | --- |
| [surf1.sh](surf1.sh) | main shell script to run the example |
| [surf1.py](surf1.py) | main python script |
| [surf1_yade.py](surf1_yade.py)  | yade part of the simulation |
| [surf1_oofem.py](surf1_oofem.py)  | oofem part of the simulation |
| [surf1_profile.py](surf1_profile.py) | script for profiling evaluation |
| [surf1_pv_sphs.py](surf1_pv_sphs.py) | script for postprocessing (spherical case) |
| [surf1_pv_poly.py](surf1_pv_poly.py) | script for postprocessing (polyhedral case) |

### Running the example
Run the example by `sh surf1.sh` shell command.

### Postprocessing
The postprocessing may be done by `pvpython surf1_pv_sphs.py` or `pvpython surf1_pv_poly.py`, according to the chosen DEM shape.
Or just open Paraview and then navigate to `Tools -> Python shell -> Run Script` and use one of the two aforementioned python scripts.
