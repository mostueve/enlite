#!/bin/bash

main_directory=../

if [[ ! -d $main_directory/data/ModelSEED ]] && [[ ! -d $main_directory/data/BiGG ]] && [[ ! -d $main_directory/data/MetaCyc ]] ; then
	echo "Correct directory structure not found."
	echo ""
	echo "Please run 'bash prepare_directories.sh'"
else
	cd $main_directory/data/ModelSEED/

	wget https://raw.githubusercontent.com/ModelSEED/ModelSEEDDatabase/dev/Biochemistry/compounds.json
	wget https://raw.githubusercontent.com/ModelSEED/ModelSEEDDatabase/dev/Biochemistry/reactions.json
