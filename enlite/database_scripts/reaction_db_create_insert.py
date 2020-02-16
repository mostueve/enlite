import json

import sqlite3

from enlite.classes.DataHandlers import DBLConfigLoader
from . sqlite_statements import (
reaction_db_creation,
creation_stmt_metacyc_reaction_aliases,
creation_stmt_metacyc_reaction_links,
creation_stmt_kegg_reaction_aliases,
creation_stmt_kegg_reaction_links,
creation_stmt_bigg_reaction_aliases,
creation_stmt_bigg_reaction_links,
creation_stmt_ec_aliases,
creation_stmt_ecnumber_links,
insert_stmt_reactions,
insert_stmt_ec_aliases,
insert_stmt_ec_links,
insert_stmt_metacyc_reaction_aliases,
insert_stmt_metacyc_reaction_links,
insert_stmt_kegg_reaction_aliases,
insert_stmt_kegg_reaction_links,
insert_stmt_bigg_reaction_aliases,
insert_stmt_bigg_reaction_links
)


def parse_aliases(alias_list):
	"""
	example data:
	"aliases": [
            "AraCyc: CATAL-RXN",
            "BiGG: CAT; CATp; CTA1; CTT1",
            "BrachyCyc: CATAL-RXN",
            "KEGG: R00009",
            "MetaCyc: CATAL-RXN; RXN-12121",

	"""
	db_names = ['KEGG', 'BiGG', 'MetaCyc']
	db_alias_dict = {}
	for db in db_names:
		tmp_list = []
		for entry in alias_list:
			if db in entry:
				if ";" not in entry:
					# we can assume that there is only
					# one alias if no semicolon is present
					db_record = entry.split(" ")[1].strip()
					tmp_list.append(db_record)
				else:
					# remove the db name and colon from the string
					entry = entry.replace(db, "").replace(":", "")
					# split at the semicolon separator
					db_record = entry.split(";")
					# remove any leftover whitespace
					# and build tmp_list
					tmp_list = [alias.strip() for alias in db_record]
		db_alias_dict[db] = tmp_list
	return db_alias_dict


def change_identifier(identifier, db_type):
	if db_type == "compound":
		prefix = "c_"
	elif db_type == "reaction":
		prefix = "v_"
	id_new = identifier
	if id_new[0].isdigit():
		id_new = ''.join((prefix, id_new))
	id_new = id_new.replace('.', '_').replace('-', '__').replace('+', '')
	return id_new


reaction_fields_list = [
'id',
'abbreviation',
'name',
'ec_numbers',
'direction',
'reversibility',
'deltag',
'definition',
'source',
'status',
'compound_ids',
'deltagerr',
'code',
'equation',
'stoichiometry',
'is_obsolete',
'is_transport',
'linked_reaction',
'abstract_reaction',
'notes',
'ontology',
'aliases',
'pathways'
]

conf = DBLConfigLoader(config_root="../config", project_root="..")

db_path = conf.get_database_path()
print(db_path)
conn = sqlite3.connect(db_path)
c = conn.cursor()
c.execute("PRAGMA foreign_keys = 1")

# for the statements, see sqlite_statements.py
reactions_creation_stmts = [
	reaction_db_creation,
	creation_stmt_metacyc_reaction_aliases,
	creation_stmt_metacyc_reaction_links,
	creation_stmt_kegg_reaction_aliases,
	creation_stmt_kegg_reaction_links,
	creation_stmt_bigg_reaction_aliases,
	creation_stmt_bigg_reaction_links,
	creation_stmt_ec_aliases,
	creation_stmt_ecnumber_links
]

# create the main tables
for stmt in reactions_creation_stmts:
	c.execute(stmt)

conn.commit()

alias_stmt_dict = {
	'MetaCyc': [insert_stmt_metacyc_reaction_aliases, insert_stmt_metacyc_reaction_links],
	'KEGG': [insert_stmt_kegg_reaction_aliases, insert_stmt_kegg_reaction_links],
	'BiGG': [insert_stmt_bigg_reaction_aliases, insert_stmt_bigg_reaction_links]
}


reac_json = conf.get_modelseed_reactions()

with open(reac_json, 'r') as rea_data:
	reaction_list = json.load(rea_data)
	
	reaction_data_list = []
	for record in reaction_list:
		record_list = []
		for field in reaction_fields_list:
			if field in {'aliases', 'ec_numbers', 'notes', 'pathways'}:
				if record[field] is None:
					data = "null"
				elif record[field] == []:
					data = record[field][0]
				elif len(record[field]) == 1:
					data = record[field][0]
				else:
					data = "|#|".join(record[field])
			else:
				if record[field] is None:
					data = "null"
				else:
					# some other fields could be lists or dictionaries
					# such as "ontology"
					if isinstance(record[field], list):
						if len(record[field]) == 1:
							data = record[field][0]
						else:
							data = "|#|".join(record[field])
					elif isinstance(record[field], dict):
						entry_dict = record[field]
						# turn the dictionary into a list and join it
						tmp = [str(key) + str(entry_dict[key]) for key in entry_dict]
						data = "|#|".join(tmp)
					else:
						data = record[field]
			record_list.append(data)
		reaction_data_list.append(record_list)
		
		c.execute(insert_stmt_reactions, record_list)
		
		# get the rowid of the last insert in the main table
		reaction_record_rowid = c.lastrowid
		
		# if there are aliases, fill the linking tables
		if record['aliases'] is not None:
			alias_dict = parse_aliases(record['aliases'])
			for db in alias_dict:
				for alias in alias_dict[db]:
					if db == "MetaCyc":
					# add the altered id
						alias_list = [alias, change_identifier(alias, "reaction")]
					else:
						alias_list = [alias]
					c.execute(alias_stmt_dict[db][0], alias_list)
					# have to get the primary key from the last insert
					# for usage in the many-to-many table
					alias_primary_key_rowid = c.lastrowid
					c.execute(alias_stmt_dict[db][1], [reaction_record_rowid, alias_primary_key_rowid, record_list[0], alias])
		
		# fill the linking table for ec numbers
		if record['ec_numbers'] is not None:
			ec_list = record['ec_numbers']
			for ec_number in ec_list:
				#print(ec_number)
				c.execute(insert_stmt_ec_aliases, [ec_number])
				ecnumber_rowid = c.lastrowid
				c.execute(insert_stmt_ec_links, [reaction_record_rowid, ecnumber_rowid, record_list[0], ec_number])
	
	conn.commit()

