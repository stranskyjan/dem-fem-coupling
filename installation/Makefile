######################################################################
# Open source FEM-DEM coupling installation Makefile
#
# run 'make help' for more info
######################################################################

######################################################################
# OPTIONS
######################################################################
top-dir = _build
j       = 1
j-oofem = $(j)
j-yade  = $(j)
######################################################################

######################################################################
# CONSTANTS
######################################################################
# oofem
oofem-dir = $(top-dir)/oofem
oofem-zip = $(oofem-dir)/oofem.zip
oofem-dir-source = $(oofem-dir)/source
oofem-dir-source-orig = $(oofem-dir)/source-orig
oofem-dir-build = $(oofem-dir)/build
liboofem-cmake-flags = $(oofem-dir-build)/CMakeFiles/liboofem.dir/flags.make
# yade
yade-dir = $(top-dir)/yade
yade-tar = $(yade-dir)/yade.tar.bz2
yade-dir-source = $(yade-dir)/source
yade-dir-source-orig = $(yade-dir)/source-orig
yade-dir-build = $(yade-dir)/build
yade-dir-install = $(yade-dir)/install
# install
install-dir = $(top-dir)/install
export-cmd = 'export PYTHONPATH=''$$''PYTHONPATH:$(install-dir):'

######################################################################
# TARGETS
######################################################################
default: help

######################################################################
# help
######################################################################
help:
	@echo
	@echo ==================================================
	@echo Open source FEM-DEM coupling installation Makefile
	@echo ==================================================
	@echo Downloads, compiles and installs all necessary software \(OOFEM, YADE\) to be used for FEM-DEM coupling
	@echo Prerequisites: wget, unzip, cmake, tar, patch, YADE prerequisites
	@echo Tested on Ubuntu 18.04 LTS system
	@echo
	@echo Options:
	@echo "   top-dir ... top directory for download, compilation ..."
	@echo "   j       ... global -j option (number of cores) for compilation"
	@echo "   j-oofem ... -j option (number of cores) for oofem compilation"
	@echo "   j-yade  ... -j option (number of cores) for yade compilation"
	@echo
	@echo Main targets:
	@echo "   all         ... runs directories, oofem, yade and install targets"
	@echo "   directories ... creates oofem, yade and istall directories in top-dir"
	@echo "   oofem       ... downloads, modifies source code and compile OOFEM"
	@echo "   yade        ... downloads, modifies source code and compile YADE"
	@echo "   intall      ... copy relevant files into top-dir/install directory"
	@echo
	@echo Sub targets \(for advanced usage\):
	@echo "   oofem-download, oofem-modify, oofem-build, oofem-cmakem oofem-make"
	@echo "   yade-download, yade-modify, yade-build, yade-cmake, yade-make"
	@echo "   install-oofem, install-yade, install-demfemcoupling, install-export"
	@echo "   end-message"
	@echo
	@echo Example usage:
	@echo "   - show this message"
	@echo "         make help"
	@echo "   - just default usage (downloads, compiles and installs everything)"
	@echo "         make all"
	@echo "   - 'my' command, specifying top-dir and j-oofem, leaving j-yade equal to 1"
	@echo "         make all top-dir=""$$""HOME/programs/demfem j-oofem=4"
	@echo "   - only run yade target (download, modify, build)"
	@echo "         make yade"
	@echo "   - only downloads and modify source code of oofem"
	@echo "         make oofem-download oofem-modify"
	@echo

######################################################################
# all
######################################################################
all: directories oofem yade install

######################################################################
# directories
######################################################################
directories:
	mkdir -p $(oofem-dir)
	mkdir -p $(yade-dir)
	mkdir -p $(install-dir)

######################################################################
# oofem
######################################################################
oofem: oofem-download oofem-modify oofem-build

oofem-download:
	rm -rf $(oofem-dir-source-orig)
	wget http://www.oofem.org/cgi-bin/OOFEM/download.cgi?download=oofem-2.5.zip -O $(oofem-zip)
	unzip -q -o $(oofem-zip)
	mv oofem-2.5 $(oofem-dir-source-orig)

oofem-modify:
	rm -rf $(oofem-dir-source)
	cp -r $(oofem-dir-source-orig) $(oofem-dir-source)
	cd $(oofem-dir-source) && \
		patch -s -p0 < $(CURDIR)/oofem.diff

oofem-build: oofem-cmake oofem-make

oofem-cmake:
	mkdir -p $(oofem-dir-build)
	cd $(oofem-dir-build) && \
		cmake -DUSE_PYTHON_BINDINGS=ON $(oofem-dir-source)
	# remove compilation flags causing ImportError before running make
	sed -i 's/-fvisibility=hidden//' $(liboofem-cmake-flags)
	sed -i 's/-fvisibility-inlines-hidden//' $(liboofem-cmake-flags)

oofem-make:
	$(MAKE) -C $(oofem-dir-build) -j $(j-oofem)

######################################################################
# yade
######################################################################
yade: yade-download yade-modify yade-build

yade-download:
	rm -rf $(yade-dir-source-orig)
	wget https://launchpad.net/yade/trunk/yade-1.00.0/+download/yade_2019.01a.tar.bz2 -O $(yade-tar)
	tar xfj $(yade-tar)
	mv trunk-2019.01a $(yade-dir-source-orig)

yade-modify:
	rm -rf $(yade-dir-source)
	cp -r $(yade-dir-source-orig) $(yade-dir-source)
	cd $(yade-dir-source) && \
		patch -s -p0 < $(CURDIR)/yade.diff

yade-build: yade-cmake yade-make

yade-cmake:
	mkdir -p $(yade-dir-build)
	cd $(yade-dir-build) && \
		cmake \
			-DCMAKE_INSTALL_PREFIX=$(yade-dir-install) \
			-DENABLE_LINSOLV=OFF \
			-DENABLE_PFVFLOW=OFF \
			-DENABLE_LBMFLOW=OFF \
			-DENABLE_TWOPHASEFLOW=OFF \
			-DENABLE_GL2PS=OFF \
			-DNOSUFFIX=ON \
			$(yade-dir-source)
	
yade-make:
	$(MAKE) -C $(yade-dir-build) -j $(j-yade)
	$(MAKE) -C $(yade-dir-build) install

######################################################################
# install
######################################################################
install: install-oofem install-yade install-demfemcoupling install-export end-message

install-oofem:
	rm -f $(install-dir)/liboofem.so
	ln -s $(oofem-dir-build)/liboofem.so $(install-dir)/liboofem.so

install-yade:
	rm -f $(install-dir)/libyade.py
	ln -s $(yade-dir-install)/bin/yade $(install-dir)/libyade.py

install-demfemcoupling:
	rm -f $(install-dir)/demfemcoupling.py
	ln -s $(CURDIR)/../src/demfemcoupling.py $(install-dir)/demfemcoupling.py

install-export:
	echo $(export-cmd) >> $(HOME)/.bashrc

end-message:
	@echo
	@echo ======================================================================
	@echo Now everything should be compiled and prepared for use.
	@echo Try out some examples :-\)
	@echo
	@echo There is no need to run this script any more
	@echo
	@echo If you want to run examples directly in this terminal, execute the
	@echo following command:
	@echo $(export-cmd)
	@echo ======================================================================
	@echo
