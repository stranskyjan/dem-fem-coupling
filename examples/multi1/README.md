A basic example of multiscale coupling - oedometric compression.
Overall the domain is modeled with FEM, constitutive law of selected integration points is modeled by DEM.

### What is here

| file name | description |
| --- | --- |
| [multi1.sh](multi1.sh) | main shell script to run the example |
| [multi1.py](multi1.py) | main python script |
| [multi1_yade.py](multi1_yade.py) | yade part of the simulation |
| [multi1_oofem.py](multi1_oofem.py) | oofem part of the simulation |
| [multi1_profile.py](multi1_profile.py) | script for profiling evaluation |
| [multi1_pv.py](multi1_pv.py) | script for postprocessing |

### Running the example
Run the example by `sh multi1.sh` shell command.

### Postprocessing
The postprocessing may be done by `pvpython multi1_pv.py`.
Or just open Paraview and then navigate to `Tools -> Python shell -> Run Script` and choose `multi1_pv.py` file.
