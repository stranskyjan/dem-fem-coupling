NAME=example1
OOFEMBASE=/tmp/$NAME-oofem
RUN=true
PV=true
PROFILE=true
MESH=false
if $MESH; then
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
