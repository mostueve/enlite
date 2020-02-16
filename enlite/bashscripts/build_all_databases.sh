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



bigg_reaction_file=$main_directory/data/BiGG/bigg_models_reactions.txt
bigg_compound_file=$main_directory/data/BiGG/bigg_models_metabolites.txt
if [[ -f "$bigg_reaction_file" ]] && [[ -f "$bigg_compound_file" ]] ; then
	python bigg_create_insert.py
else
	echo "BiGG DB files not found, please check files and maybe run 'get_flatfiles.sh'"
fi


metacyc_reaction_file=$main_directory/data/MetaCyc/reactions.dat
metacyc_compound_file=$main_directory/data/MetaCyc/compounds.dat
if [[ -f "$metacyc_reaction_file" ]] && [[ -f "$metacyc_compound_file" ]] ; then
	python metacyc_create_insert.py
else
	echo "MetaCyc DB files not found, please check files and maybe run 'get_flatfiles.sh'"
fi

