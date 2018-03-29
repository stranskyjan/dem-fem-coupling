#!/bin/bash
#
# A script to download, compile and install all necessary software
# (OOFEM, YADE) to be used for FEM-DEM coupling 
#
# prerequisites: wget, unzip, cmake, tar, patch
#
# Tested on Ubuntu 16.04 LTS system
# enjoy
# Jan Stransky <jan.stransky@fsv.cvut.cz>
#

#=====================================================================
# INPUTS
#=====================================================================
#
top=$HOME/femdem         # where to put all downloaded and installed files
include_dir=$top/include # include directory
tmp=/tmp                 # temporary directory
# OOFEM
oofem=true           # process OOFEM or not
oofem_dir=$top/oofem # OOFEM directory
oofem_j=1            # how many cores to us for OOFEM compilation
# YADE
yade=true          # process YADE or not
yade_dir=$top/yade # YADE directory
yade_j=1           # how many cores to us for YADE compilation
# end of inputs
#=====================================================================

# -e = exit after error
# -x = print all command before execution
set -e -x

script_dir=`dirname $0`
script_dir=`realpath $script_dir`

#=====================================================================
# checking prerequisites
#=====================================================================
echo Checking prerequisites ...
for cmd in wget unzip patch cmake tar patch; do
	hash $cmd 2>/dev/null || {
		echo
		echo missing command: $cmd
		echo
		exit 1
	}
done

[ -d $include_dir ] || mkdir -p $include_dir

#=====================================================================
# OOFEM
#=====================================================================
if $oofem; then
	oofemtmp=$tmp/oofem-2.4
	rm -rf $oofemtmp $oofemtmp.zip $oofem_dir
	# download and unzip oofem-2.3.zip
	wget http://www.oofem.org/cgi-bin/OOFEM/download.cgi?download=oofem-2.4.zip -O $oofemtmp.zip
	cd $tmp
	unzip -q $oofemtmp.zip
	# modifiy the source code
	patch -s -p0 < $script_dir/oofem.diff
	#
	mkdir -p $oofem_dir
	mv $oofemtmp $oofem_dir/source
	# compile oofem
	mkdir -p $oofem_dir/build
	cd $oofem_dir/build
	cmake -DUSE_PYTHON_BINDINGS=ON $oofem_dir/source
	echo
	echo "Compiling oofem, takes some time..."
	echo
	make -j $oofem_j
	# create symbolic link
	rm -f $include_dir/liboofem.so
	ln -s $oofem_dir/build/liboofem.so $include_dir/liboofem.so
	rm -rf $oofemtmp $oofemtmp.zip
fi

#=====================================================================
#YADE
#=====================================================================
if $yade; then
	#
	yadeversion=2017.01a
	yadetmp=$tmp/yade-$yadeversion
	rm -rf $yadetmp $yadetmp.tar.gz $yade_dir
	# download and extract yade
	wget https://launchpad.net/yade/trunk/yade-1.00.0/+download/yade-$yadeversion.tar.gz -O $yadetmp.tar.gz
	cd $tmp
	tar xfz $yadetmp.tar.gz
	mv trunk-$yadeversion $yadetmp
	# modifiy the source code
	patch -s -p0 < $script_dir/yade.diff
	#
	mkdir -p $yade_dir
	mv $yadetmp $yade_dir/source
	# compile YADE
	cd $yade_dir/source
	mkdir -p $yade_dir/build $yade_dir/install
	cd $yade_dir/build
	cmake \
		-DINSTALL_PREFIX=$yade_dir/install \
		-DENABLE_LINSOLV=OFF \
		-DENABLE_PFVFLOW=OFF \
		-DENABLE_LBMFLOW=OFF \
		-DNOSUFFIX=ON \
		$yade_dir/source
	echo
	echo "Compiling yade, takes a lot of time..."
	echo
	make -j $yade_j install
	# create symbolic link
	rm -f $include_dir/libyade.py
	ln -s $yade_dir/install/bin/yade $include_dir/libyade.py
	rm -rf $yadetmp $yadetmp.tar.gz
fi

#=====================================================================
# other
#=====================================================================
ln -s $script_dir/../src/demfemcoupling.py $include_dir/demfemcoupling.py
# export PYTHONPATH in .bashrc file
exp="export PYTHONPATH=$include_dir:\$PYTHONPATH"
echo $exp >> $HOME/.bashrc

set +x

echo
echo ======================================================================
echo Now everything should be compiled and prepared for use.
echo Try out some examples :-\)
echo
echo There is no need to run this script any more
echo
echo If you want to run examples directly in this terminal, execute the
echo following command:
echo $exp
echo ======================================================================
echo
