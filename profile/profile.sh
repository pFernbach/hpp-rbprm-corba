#!/bin/bash         

gepetto-viewer-server & 
hpp-rbprm-server &
ipython ../script/scenarios/$1

pkill -f  'gepetto-viewer-server'
pkill -f  'hpp-rbprm-server'
