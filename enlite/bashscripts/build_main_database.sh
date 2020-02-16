#!/bin/bash

cd ../database_scripts/
main_directory=../

modelseed_reaction_file=$main_directory/data/ModelSEED/reactions.json
modelseed_compound_file=$main_directory/data/ModelSEED/compounds.json
if [[ -f "$modelseed_reaction_file" ]] && [[ -f "$modelseed_compound_file" ]] ; then
	python reaction_db_create_insert.py
	python compound_db_create_insert.py
else
	echo "ModelSEED DB files not found, please check files and maybe run 'get_flatfiles.sh'"
fi
