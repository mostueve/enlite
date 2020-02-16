#!/bin/bash

main_directory=..

mkdir $main_directory/data
cd $main_directory/data

if [[ ! -d ModelSEED ]] || [[ ! -d BiGG ]] || [[ ! -d MetaCyc ]] ; then
	mkdir ModelSEED BiGG MetaCyc
else
	echo "Directories already exist:"
	echo ""
	ls -l
fi
