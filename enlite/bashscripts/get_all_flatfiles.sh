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

	cd ../BiGG/

	wget http://bigg.ucsd.edu/static/namespace/bigg_models_metabolites.txt --restrict-file-names=nocontrol
	wget http://bigg.ucsd.edu/static/namespace/bigg_models_reactions.txt --restrict-file-names=nocontrol
	
	echo ""
	echo "Please note:"
	echo "There can be some falsely placed newlines in the BiGG metabolites file,"
	echo "due to the download process and the way the server provides the files."
	echo "Please remove the additional newlines before proceding."
	echo "the lines have to contain 6 entries, all separated by a tab."
	echo ""
	echo ""
	echo "all done"
	echo ""
	echo ""
	echo "Concerning MetaCyc flatfiles:"
	echo ""
	echo "MetaCyc files cannot be obtained in this way."
	echo "please visit metacyc.org and https://biocyc.org/download-bundle.shtml"
	echo ""
fi


