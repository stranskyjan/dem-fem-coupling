A very basic example of surface coupling - three DEM particles (either spheres or polyhedra) "bombarding" a FEM cantilever.
The spherical or polyhedral case is set in [surf1_yade.py](surf1_yade.py) by `usePolyhedra` variable or (not) using `poly=true` option for `make`.

### What is here
| file name | description |
| --- | --- |
| [Makefile](Makefile) | makefile for the example |
| [surf1.py](surf1.py) | main python script |
| [surf1_yade.py](surf1_yade.py)  | yade part of the simulation |
| [surf1_oofem.py](surf1_oofem.py)  | oofem part of the simulation |
| [surf1_profile.py](surf1_profile.py) | script for profiling evaluation |
| [surf1_pv_sphs.py](surf1_pv_sphs.py) | script for postprocessing (spherical case) |
| [surf1_pv_poly.py](surf1_pv_poly.py) | script for postprocessing (polyhedral case) |

### Running the example
Run the example by `make all` (or run `make help` for more options)

### Postprocessing
The postprocessing may be done by `pvpython surf1_pv_sphs.py` or `make pv` for spherical case of `pvpython surf1_pv_poly.py` or `make pv poly=true` for polyhedral case.
Or just open Paraview and then navigate to `Tools -> Python shell -> Run Script` and use one of the two aforementioned python scripts.
