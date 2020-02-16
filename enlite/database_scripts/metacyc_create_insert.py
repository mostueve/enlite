import traceback
import re
import sqlite3

from enlite.classes.DataHandlers import DBLConfigLoader
from . sqlite_statements import create_metacyccompounds, create_metacycreactions, metacyc_compounds_insert, metacyc_reactions_insert


def meta_parser(filename):
	"""	takes a filename as argument
		return a list of lists, with each list containing one metacyc record
		no fields are merged yet
	"""
	# this stores each entry for one iteration of the inner parser loop
	# because annotations to entries come after the entry
	annotation_tmp = ""
	
	with open(filename, mode='r', encoding='ISO-8859-1') as infile:
		file_block_list = []
		for line in infile:
			record_list = []
			
			# check comment lines for db fields
			if line.startswith("#"):
				# parse databasefields:
				if line.startswith("# Attributes:"):
					databasefields = []
					print("Database fields:")
					for line in infile:
						if line == "#\n":
							break
						db_field = line.lstrip("#")
						db_field = db_field.strip()
						print(db_field)
						databasefields.append(db_field)
				# when not dealing with the Attributes block,
				# ignore the comment lines
				continue
				
			if line.startswith("UNIQUE"):
				line = line.strip()
				record_list.append(line)
				for k in infile:
					if k.startswith("//"):
						# reached end of record
						annotation_tmp = ""
						break
					elif k.startswith("/"):
						# take care of entries which span
						# more than one line
						old_rec = record_list.pop()
						new_rec = k.strip() + old_rec
						record_list.append(new_rec)
						annotation_tmp = new_rec
						continue
					elif k.startswith("^COEFFICIENT"):
						# ignore coefficients
						continue
					k = k.strip()
					record_list.append(k)
					annotation_tmp = k
				file_block_list.append(record_list)
	
	return databasefields, file_block_list

	
def build_formula(form_parts):
	"""creates a standard chemical formula
	input from the parsing looks like e.g. (O 12), (C 6)
	joins the elements and factors
	"""
	formula_return = ""
	# form_parts is a list containing (O 12), (C 6) e.g.
	for i in form_parts:
		form_elem = re.sub(r'\s', '', string=i)
		form_elem = form_elem.replace("(", "").replace(")", "")
		formula_return = formula_return + form_elem
	return formula_return


def field_merger(record_list, mapping):
	"""based on a list of database fields,
	merge the entries of the input list, such that
	all entries belonging to the same field are merged
	"""
	return_dict = {}
	# cand is the database field as specified
	# in the "Attributes" block of the input files
	for cand in mapping:
		tmp_list = []
		for item in record_list:
			if item.startswith(cand):
				store = item.strip().split(" - ")[1]
				tmp_list.append(store)
		return_dict[cand] = tmp_list

	return return_dict


def dict_transform(d):
	output_dict = {}
	inner_dict = {}
	unique_id = d['UNIQUE-ID'][0]
	for k in d:
		tmp_field = ""
		if k == 'UNIQUE-ID':
			continue
		if k == 'CHEMICAL-FORMULA' and len(d[k]) > 0:
			tmp_field = build_formula(d[k])
		elif len(d[k]) == 0:
			tmp_field = "null"
		else:
			tmp_field = ' |##| '.join(d[k])
		inner_dict[k] = tmp_field
	output_dict[unique_id] = inner_dict
	return output_dict
	

def dict_list_transform(d):
	output_list = []
	inner_list = []
	for k in d:
		tmp_field = ""
		if k == 'CHEMICAL-FORMULA' and len(d[k]) > 0:
			tmp_field = build_formula(d[k])
		elif len(d[k]) == 0:
			tmp_field = "null"
		else:
			tmp_field = ' |##| '.join(d[k])
		inner_list.append(tmp_field)
	return inner_list


def change_identifiers(identifier, db_type):
	if db_type == "compound":
		prefix = "c_"
	elif db_type == "reaction":
		prefix = "v_"
	id_new = identifier
	if id_new[0].isdigit() == True:
		id_new = ''.join((prefix, id_new))
	id_new = id_new.replace('.', '_').replace('-', '__').replace('+', '')
	return id_new



dbl_config = DBLConfigLoader(config_root="../config", project_root="..")

meta_compounds = dbl_config.get_metacyc_compounds()
meta_reactions = dbl_config.get_metacyc_reactions()


cpd_databasefields, compounds_as_list = meta_parser(meta_compounds)
rxn_databasefields, reactions_as_list = meta_parser(meta_reactions)



compounds_big_output = []
for x in compounds_as_list:
	# use the mapping list for compounds here
	try:
		tmp_dict = field_merger(x, cpd_databasefields)
	except Exception:
		print("an error occurred:")
		traceback.print_exc()

	tmp_list = dict_list_transform(tmp_dict)
	compounds_big_output.append(tmp_list)
	

reactions_big_output = []
for t in reactions_as_list:
	# use the mapping list for reactions here
	try:
		tmp_dict = field_merger(t, rxn_databasefields)
	except Exception:
		print("an error occurred:")
		traceback.print_exc()

	tmp_list = dict_list_transform(tmp_dict)
	reactions_big_output.append(tmp_list)



db_path = dbl_config.get_database_path()
conn = sqlite3.connect(db_path)
c = conn.cursor()
c.execute("PRAGMA foreign_keys = 1")


try:
	
	c.execute(create_metacyccompounds)
	c.execute(create_metacycreactions)
	
	c.executemany(metacyc_compounds_insert, compounds_big_output)
	c.executemany(metacyc_reactions_insert, reactions_big_output)
		
except Exception:
	print("an error occurred:")
	traceback.print_exc()
finally:
	conn.commit()
	
conn.close()

