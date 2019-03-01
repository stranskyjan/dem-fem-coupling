# [Open source FEM-DEM coupling](https://github.com/stranskyjan/dem-fem-coupling)
Open source codes for coupling of Finite Element Method and Discrete Element Method using
[YADE](http://yade-dem.org),
and
[OOFEM](http://www.oofem.org)
softwares.

## Compatibility
Compilation and examples were tested on [Ubuntu 16.04 LTS](http://www.ubuntu.com/) system.
Postprocessing was done using [Paraview 5.0.1](https://www.paraview.org/).

On Ubuntu 18.04, there were some compilation issues and postprocessing issues.
Currently I am out of time to fix it..

## Installation
There is [downloadAndInstall shell script](installation/downloadAndInstall.sh), which downloads, compiles and installs all necessary softwares.
It also modifies some part of source codes to make them all compatible.

## Examples
See [examples](examples) directory.

## Contribution
#### Pull Requests
Are welcome.

#### Bug reporting
In case of any question or problem, please leave an issue at the [githup page of the project](https://github.com/stranskyjan/dem-fem-coupling).

#### Contributors
- [Jan Stránský](https://github.com/stranskyjan)

## References
- [J. Stranský, M. Jirásek. Open source FEM-DEM coupling. Engineering Mechanics 2012](http://www.engmech.cz/2012/proceedings/pdf/018_Stransky_J-FT.pdf)
- [J. Stranský. FEM – DEM coupling and MuPIF framework. Engineering Mechanics 2013](http://www.engmech.cz/2013/im/doc/Book_of_EAi.pdf)
- [J. Stranský. Open source DEM–FEM coupling, Particles 2013](http://congress.cimne.com/particles2013/proceedings/full/p182.pdf)
- [J. Stranský. Combination of FEM and DEM with application to railway ballast-sleeper interaction, Engineering Mechanics 2014](http://www.engmech.cz/2014/im/doc/EM2014_proceedings.pdf)
- [J. Stranský. Mesoscale Discrete Element Model for Concrete and Its Combination with FEM, Ph.D. thesis](https://github.com/stranskyjan/phd-thesis)

## Acknowledgement
- To [Weimin Song](https://www.researchgate.net/profile/Weimin_Song)
for testing some of the codes.
