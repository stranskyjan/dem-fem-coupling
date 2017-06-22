NAME=example2
OOFEMBASE=/tmp/$NAME-oofem
YADE=yade-trunk
PREPROC=true
MESH=false
RUN=true
PROFILE=true

if $PREPROC; then
	$YADE -x $NAME-yade-preproc.py
	cp /tmp/$NAME-spheres.dat .
	cp /tmp/$NAME-sleeper.dat .
fi

if $MESH; then
	salome -t $NAME-unv.py
	python $NAME-unv2oofem.py $OOFEMBASE
	cp /tmp/$NAME-oofem.in .
fi

if $RUN; then
	if $PROFILE; then
		python -m cProfile -o /tmp/$NAME.pro $NAME.py
		python example2-profile.py
	else
		python $NAME.py
	fi
fi
