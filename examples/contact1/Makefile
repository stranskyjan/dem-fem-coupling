######################################################################
# contact1 Makefile
# run 'make help' for more info
######################################################################
# options
no-profile =
pvexe      = pvpython

#constants
name = contact1

#targets
help:
	@echo
	@echo =================
	@echo contact1 Makefile
	@echo =================
	@echo
	@echo Options:
	@echo "   no-profile ... do not run profiler"
	@echo "   pvexe      ... pvpython executable"
	@echo
	@echo Targets:
	@echo "   all     ... runs example, profile and pv target"
	@echo "   example ... runs example"
	@echo "   profile ... prints profiler info (if no-profile is not set)"
	@echo "   pv      ... runs paraview (pvpython) postprocessing"
	@echo
	@echo Example usage:
	@echo "   make all                     # default usage"
	@echo "   make example no-profile=true # runs example without profiling"
	@echo "   make pv                      # runs pvpython"
	@echo

all: example profile pv

example:
ifdef no-profile
	python $(name).py
else
	python -m cProfile -o /tmp/$(name).pro $(name).py
endif

profile:
ifndef no-profile
	python $(name)_profile.py
endif

pv:
	$(pvexe) $(name)_pv.py
