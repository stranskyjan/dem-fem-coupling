#!/bin/bash
set -e

name=surf1

profile=true   # profile times spend on individual simulation parts
pvpostpro=true # run python paraview postprocessing
pvexe=pvpython # command to run python paraview

echo
echo "Running simulation"
echo "=================="
echo
if $profile; then
	python -m cProfile -o /tmp/$name.pro $name.py
	echo
	echo "Running profiler"
	echo "================"
	echo
	python ${name}_profile.py
else
	python $name.py
fi

if $pvpostpro; then
	echo
	echo "Running postprocessing"
	echo "======================"
	echo
	$pvexe ${name}_pv_sphs.py # or use surf1_pv_poly.py in case usePolyhedra=True in surf1_yade.py
fi
