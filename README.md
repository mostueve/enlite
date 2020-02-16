# enlite

A lightweight python package for querying a local SQLite version of the ModelSEED database for compound and reaction data. The main intention is to make the search for ID aliases easy (for example, find all aliases of any MetaCyc or ModelSEED ID).
This software is published under the GNU General Public License v3, free to use for anyone, in the hope that it will be helpful in navigating the jungle of identifiers. 

## installation

You can use [the anaconda python distribution](https://docs.conda.io/projects/conda/en/latest/user-guide/install/), but the package will work with standard Python (tested for Python >= 3.7) just as well.

Setup for creation of an anaconda virtual environment:

```bash
conda create -n enlite_conda pip json PyYAML
conda activate enlite_conda
```

Clone the repository:

```bash
git clone https://gitlab.com/mostueve/enlite
```

Install using

```bash
pip -e /path/to/cloned/repo
```
The only files necessary to work with the package are the [compounds](https://raw.githubusercontent.com/ModelSEED/ModelSEEDDatabase/dev/Biochemistry/compounds.json) and [reactions](https://raw.githubusercontent.com/ModelSEED/ModelSEEDDatabase/dev/Biochemistry/reactions.json) json files from [ModelSEED](https://github.com/ModelSEED) ([main website](http://modelseed.org/)), but they do not contain all the information. So depending on your needs, you can get a free subscription to MetaCyc (BiGG is free anyway).
I cannot provide the flatfiles of ModelSEED, BiGG and MetaCyc here, but you can easily download them using the provided bashscript. It needs a specific directory structure to work. The structure of the entire repository is as follows:

enlite  
├── bashscripts  
├── classes  
├── config  
├── data  
│   ├── BiGG  
│   ├── MetaCyc  
│   └── ModelSEED  
└── database_scripts  

**Please make sure to use bash to run the scripts!**

The `prepare_directories.sh` script will generate the subdirectories in the "data" folder.

```bash
bash prepare_directories.sh
bash get_modelseed_flatfiles.sh
```

Now, create the SQLite database using 
```bash
bash build_main_database.sh
```
(remember, you do not need the extra BiGG and MetaCyc tables for this software to work, so just ignore potential errors)

if you have all the files available, you can also create SQLite tables for metacyc and bigg. Their usage is not implemented in the software, but you can query them nonetheless.
```bash
bash prepare_directories.sh
bash get_all_flatfiles.sh
bash build_all_databases.sh
```


## usage

The file db_lookup.py contains a command-line utility.
You can run it using python for example like this:
```bash
python db_lookup.py --help
```

The available subcommands are:

	cpd_info            find information on one or more compound IDs
    rxn_info            find information on one or more reaction IDs
    cpd_single          find one alias of one or more compound IDs
    cpd_multi           find all aliases of one or more compound IDs
    rxn_single          find one alias of one or more reaction IDs
    rxn_multi           find all aliases of one or more reaction IDs


To look up information on a metacyc compound, you would use:
```bash
python db_lookup.py cpd_info <compound id> -i c
```

To look up compound or reaction aliases, use one of the "single" or "multi" subcommands.

For example:
```bash

# compound alias lookups:
python db_lookup.py cpd_single <cpd_list_modelseed> -i m -o c -l
python db_lookup.py cpd_multi g6p -i b -o c
python db_lookup.py cpd_multi cpd00001 -i m -o k

# reaction alias lookups:
python db_lookup.py rxn_multi <rxn_list_kegg> -i k -o m -l
python db_lookup.py rxn_multi rxn00001 -i m -o c

# compound or reaction information:
python db_lookup.py cpd_info -i m cpd00001
python db_lookup.py cpd_info -i c OH
python db_lookup.py rxn_info -i b h2o
python db_lookup.py rxn_info -i k C00001
```
