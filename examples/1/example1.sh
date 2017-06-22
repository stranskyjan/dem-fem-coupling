NAME=example1

MESH=false   # create a mesh by salome (optional)
PROFILE=true # profile times spend on individual simulation parts
PV=false     # run python paraview postprocessing

if $MESH; then
	OOFEMBASE=/tmp/$NAME-oofem
	salome -t $NAME-unv.py
	python $NAME-unv2oofem.py $OOFEMBASE
	cp $OOFEMBASE.in $NAME-oofem.in
fi

if $PROFILE; then
	python -m cProfile -o /tmp/$NAME.pro $NAME.py
	#python -m cProfile $NAME.py > /tmp/aaa
	python example1-profile.py
else
	python $NAME.py
fi

if $PV; then
	PVEXE=pvbatch
	$PVEXE $NAME-pv.py
fi
