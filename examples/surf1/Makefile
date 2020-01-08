######################################################################
# surf1 Makefile
# run 'make help' for more info
######################################################################
# options
no-profile =
poly       =
pvexe      = pvpython

#constants
name = surf1

#targets
help:
	@echo
	@echo ==============
	@echo surf1 Makefile
	@echo ==============
	@echo
	@echo Options:
	@echo "   no-profile ... do not run profiler"
	@echo "   poly       ... use polyhedrons instead of spheres"
	@echo "   pvexe      ... pvpython executable"
	@echo
	@echo Targets:
	@echo "   all     ... runs example, profile and pv target"
	@echo "   example ... runs example"
	@echo "   profile ... prints profiler info (if no-profile is not set)"
	@echo "   pv      ... runs paraview (pvpython) postprocessing"
	@echo
	@echo Example usage:
	@echo "   make all                     # default usage (spherical particles)"
	@echo "   make all poly=true           # default usage (polyhedral particles)"
	@echo "   make example no-profile=true # runs example without profiling"
	@echo "   make pv poly=true            # runs pvpython considering polyhedral particles"
	@echo

all: example profile pv

example:
	# set usePolyhedra=True if poly option is set
ifdef poly
	sed -i 's/^usePolyhedra *=.*/usePolyhedra = True/' $(name)_yade.py
endif
	# use profiler or not
ifdef no-profile
	python $(name).py
else
	python -m cProfile -o /tmp/$(name).pro $(name).py
endif
	# reset _yade.py script after running
	sed -i 's/^usePolyhedra *=.*/usePolyhedra = False/' $(name)_yade.py

profile:
ifndef no-profile
	python $(name)_profile.py
endif

pv:
ifndef poly
	$(pvexe) $(name)_pv_sphs.py
else
	$(pvexe) $(name)_pv_poly.py
endif
