# [Open source FEM-DEM coupling](https://github.com/stranskyjan/dem-fem-coupling)
Open source codes for coupling of Finite Element Method and Discrete Element Method using
[YADE](http://yade-dem.org),
and
[OOFEM](http://www.oofem.org)
softwares.

## Compatibility
Compilation and examples were tested on [Ubuntu 18.04 LTS](http://www.ubuntu.com/) system,
using OOFEM 2.5
and
YADE 2019.01a.
Postprocessing was done using [Paraview 5.4.1](https://www.paraview.org/).

## Installation
There is [Makefile](installation/Makefile), which downloads, compiles and installs all necessary softwares.
It also modifies some part of source codes to make them all compatible.
Run `make help` for more info.

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
- [W. Song, B. Huang, X. Shu, J. Stránský. Interaction between Railroad Ballast and Sleeper: A DEM-FEM Approach. Int. J. Geomech. 19, 2019](https://ascelibrary.org/doi/abs/10.1061/%28ASCE%29GM.1943-5622.0001388)

## Acknowledgement
- To
[Weimin Song](https://www.researchgate.net/profile/Weimin_Song),
[De Zhang](https://www.researchgate.net/profile/De_Zhang13)
and others for testing and feedback.

## TODO
- comments of the source code
