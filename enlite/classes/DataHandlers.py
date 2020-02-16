import os
import re
import sqlite3
import pickle
from datetime import datetime

from yaml import load
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

from . CustomExceptions import RecordNotFoundError


class DatabaseHandler:
    def __init__(self, db_path):
        if os.path.isfile(db_path):
            self.db_path = db_path
            try:
                self.conn = sqlite3.connect(self.db_path)
                # enable named access for data returned
                self.conn.row_factory = sqlite3.Row
                self.c = self.conn.cursor()
            except sqlite3.DatabaseError:
                print("There was an error connecting to the database.")
        else:
            print("Database not found. Make sure you created it according to the requirements.")

        self.db_names_dict = {
            'm': 'modelseed',
            'c': 'metacyc',
            'b': 'bigg',
            'k': 'kegg'
        }

    def connect_db(self):
        self.conn = sqlite3.connect(self.db_path)
        self.c = self.conn.cursor()

    def close_connection(self):
        self.conn.close()

    def dictionary_factory(self, row_object):
        """
        Out of a sqlite3.Row object, build a dictionary
        :param row_object: any Row object fetched from the database
        :type row_object: sqlite3.Row
        :return: a dictionary holding the values of the Row object
        :rtype: dict
        """
        data_dict = {}
        for key in row_object.keys():
            data_dict[key] = row_object[key]
        return data_dict

    @staticmethod
    def build_id_table_name(db_name, db_type):
        if db_name not in {'bigg', 'kegg', 'metacyc'} and db_type not in {'reaction', 'compound'}:
            raise ValueError('db name and db type need to be specific!', db_name, db_type)
        return f"{db_name}_{db_type}_ids"

    @staticmethod
    def build_alias_table_name(db_name, db_type):
        if db_name not in {'bigg', 'kegg', 'metacyc'} and db_type not in {'reaction', 'compound'}:
            raise ValueError('db name and db type need to be specific!', db_name, db_type)
        return f"{db_name}_{db_type}_aliases"

    def query_db_fetchall(self, stmt, query_args, commit=False):
        self.c.execute(stmt, (query_args,))
        query_result = self.c.fetchall()
        if commit:
            self.conn.commit()
        return query_result

    def query_db_fetchone(self, stmt, query_args, commit=False):
        self.c.execute(stmt, (query_args,))
        query_result = self.c.fetchone()
        if commit:
            self.conn.commit()
        return query_result

    def fetch_modelseed_cpd_inchikey(self, compound_id):
        """fetch and return an InCHI Key from the modelseed db
        :param compound_id: a ModelSEED compound ID
        :type compound_id: str
        :return: The InCHI Key of the compound
        :rtype: str
        """
        stmt = "SELECT inchikey FROM modelseed_compounds WHERE cpd_id == ?"
        self.c.execute(stmt, (compound_id,))
        inchi_record = self.c.fetchone()
        if inchi_record is None:
            raise RecordNotFoundError(message=f"record for {compound_id} not found")
        inchikey = inchi_record['inchikey']
        return inchikey

    def fetch_modelseed_cpd_info(self, compound_id):
        stmt = "SELECT cpd_id, abbreviation, name, formula, inchikey, mass, charge FROM modelseed_compounds WHERE cpd_id == ?"
        self.c.execute(stmt, (compound_id,))
        compound_info = self.c.fetchone()
        if compound_info is None:
            raise RecordNotFoundError(message=f"record for {compound_id} not found")
        return compound_info

    def fetch_modelseed_rxn_info(self, reaction_id):
        stmt = "SELECT rxn_id, name, stoichiometry, equation, deltag FROM modelseed_reactions WHERE rxn_id == ?"
        self.c.execute(stmt, (reaction_id,))
        reaction_info = self.c.fetchone()
        if reaction_info is None:
            raise RecordNotFoundError(message=f"record for {reaction_id} not found")
        return reaction_info

    def fetch_compound_alias(self, database_id, db_name_in, metacyc_id_is_altered=False):
        if db_name_in == "modelseed":
            linked_modelseed_id = database_id
        elif db_name_in == "metacyc" and metacyc_id_is_altered:
            database_id = self.get_normal_metacyc_cpd_id(database_id)
            linked_modelseed_id = self.fetch_linked_modelseed_cpd_id(db_name_in, database_id)
        else:
            linked_modelseed_id = self.fetch_linked_modelseed_cpd_id(db_name_in, database_id)
        # get linked id based on the modelseed ID
        # run one of the fetch_all_aliases functions
        # based on the output called for, generate the print/return values
        try:
            all_aliases = self.fetch_all_compound_aliases(linked_modelseed_id)
        except RecordNotFoundError:
            return [{'cpd_id': None, 'linked_id_metacyc': None, 'linked_id_bigg': None, 'linked_id_kegg': None}]
        return all_aliases

    def fetch_reaction_alias(self, database_id, db_name_in, metacyc_id_is_altered=False):
        if db_name_in == "modelseed":
            linked_modelseed_id = database_id
        elif db_name_in == "metacyc" and metacyc_id_is_altered:
            database_id = self.get_normal_metacyc_rxn_id(database_id)
            linked_modelseed_id = self.fetch_linked_modelseed_rxn_id(db_name_in, database_id)
        else:
            linked_modelseed_id = self.fetch_linked_modelseed_rxn_id(db_name_in, database_id)
        # get linked id based on the modelseed ID
        # run one of the fetch_all_aliases functions
        # based on the output called for, generate the print/return values
        try:
            all_aliases = self.fetch_all_reaction_aliases(linked_modelseed_id)
        except RecordNotFoundError:
            return [{'rxn_id': None, 'linked_id_metacyc': None, 'linked_id_bigg': None, 'linked_id_kegg': None}]
        return all_aliases

    def fetch_linked_modelseed_cpd_id(self, db_name_in, compound_id):
        """

        :param db_name_in: one of metacyc, bigg, kegg
        :type db_name_in: str
        :param compound_id:
        :type compound_id:
        :return:
        :rtype:
        :raises RecordNotFoundError: when None is returned from the query
        """
        link_table = self.build_alias_table_name(db_name_in, 'compound')
        stmt = f"SELECT cpd_id FROM {link_table} WHERE linked_id_{db_name_in} == ?"
        query_result = self.query_db_fetchone(stmt, compound_id)
        if query_result is None:
            raise RecordNotFoundError(message=f"record for {compound_id} not found")
        modelseed_cpd_id = query_result['cpd_id']
        return modelseed_cpd_id

    def fetch_linked_modelseed_rxn_id(self, db_name_in, reaction_id):
        """

        :param db_name_in: one of metacyc, bigg, kegg
        :type db_name_in: str
        :param reaction_id:
        :type reaction_id:
        :return:
        :rtype:
        :raises RecordNotFoundError: when None is returned from the query
        """
        link_table = self.build_alias_table_name(db_name_in, 'reaction')
        stmt = f"SELECT rxn_id FROM {link_table} WHERE linked_id_{db_name_in} == ?"
        query_result = self.query_db_fetchone(stmt, reaction_id)
        if query_result is None:
            raise RecordNotFoundError(message=f"record for {reaction_id} not found")
        modelseed_rxn_id = query_result['rxn_id']
        return modelseed_rxn_id

    def get_normal_metacyc_cpd_id(self, altered_cpd_id):
        """

        :param altered_cpd_id:
        :type altered_cpd_id:
        :return:
        :rtype:
        :raises RecordNotFoundError: when None is returned from the query
        """
        altered_id_stmt = """SELECT linked_id_metacyc FROM metacyc_compound_ids WHERE altered_id == ?"""
        self.c.execute(altered_id_stmt, (altered_cpd_id,))
        query_for_id_result = self.c.fetchone()
        if query_for_id_result is None:
            raise RecordNotFoundError(message=f"record for {altered_cpd_id} not found")
        return query_for_id_result['linked_id_metacyc']

    def get_normal_metacyc_rxn_id(self, altered_rxn_id):
        """

        :param altered_rxn_id:
        :type altered_rxn_id:
        :return:
        :rtype:
        :raises RecordNotFoundError: when None is returned from the query
        """
        altered_id_stmt = """SELECT linked_id_metacyc FROM metacyc_reaction_ids WHERE altered_id == ?"""
        self.c.execute(altered_id_stmt, (altered_rxn_id,))
        query_for_id_result = self.c.fetchone()
        if query_for_id_result is None:
            raise RecordNotFoundError(message=f"record for {altered_rxn_id} not found")
        return query_for_id_result['linked_id_metacyc']

    def get_altered_metacyc_cpd_id(self, normal_cpd_id):
        """

        :param normal_cpd_id:
        :type normal_cpd_id:
        :return:
        :rtype:
        :raises RecordNotFoundError: when None is returned from the query
        """
        normal_id_stmt = """SELECT altered_id FROM metacyc_compound_ids WHERE linked_id_metacyc == ?"""
        self.c.execute(normal_id_stmt, (normal_cpd_id,))
        query_for_id_result = self.c.fetchone()
        if query_for_id_result is None:
            raise RecordNotFoundError(message=f"record for {normal_cpd_id} not found")
        return query_for_id_result['altered_id']

    def get_altered_metacyc_rxn_id(self, normal_rxn_id):
        """

        :param normal_rxn_id:
        :type normal_rxn_id:
        :return:
        :rtype:
        :raises RecordNotFoundError: when None is returned from the query
        """
        normal_id_stmt = """SELECT altered_id FROM metacyc_reaction_ids WHERE linked_id_metacyc == ?"""
        self.c.execute(normal_id_stmt, (normal_rxn_id,))
        query_for_id_result = self.c.fetchone()
        if query_for_id_result is None:
            raise RecordNotFoundError(message=f"record for {normal_rxn_id} not found")
        return query_for_id_result['altered_id']

    def fetch_metacyc_inchikey(self, altered_cpd_id):
        """
        fetch compound inchikey from a metacyc altered ID
        :param altered_cpd_id: a metacyc compound ID formatted by the metabolism framework
        :type altered_cpd_id: str
        :return: inchikey
        :rtype: str
        :raises RecordNotFoundError: when the altered ID is not found in the db
        """
        altered_id_stmt = """SELECT linked_id_metacyc FROM metacyc_compound_ids WHERE altered_id == ?"""
        self.c.execute(altered_id_stmt, (altered_cpd_id,))
        query_for_id_result = self.c.fetchone()
        if query_for_id_result is None:
            raise RecordNotFoundError(message=f"record for {altered_cpd_id} not found")
        linked_id_metacyc = query_for_id_result['linked_id_metacyc']
        inchikey_select_stmt = """
        SELECT cpd_id, inchikey FROM modelseed_compounds
        WHERE cpd_id in 
        (SELECT cpd_id FROM metacyc_compound_aliases WHERE linked_id_metacyc == ?)
        AND is_obsolete != "1";
        """
        self.c.execute(inchikey_select_stmt, (linked_id_metacyc,))
        record_data = self.c.fetchone()
        compound_info_dict =  self.dictionary_factory(record_data)
        inchikey = compound_info_dict['inchikey']
        return inchikey

    def fetch_metacyc_cpd_info(self, altered_cpd_id):
        """
        fetch compound info based on metacyc altered ID
        :param altered_cpd_id: a metacyc compound ID formatted by the framework
        :type altered_cpd_id: str
        :return: metacyc_id, altered_metacyc_id, modelseed_id, abbrev, name, formula, charge, mass
        :rtype: dict
        :raises RecordNotFoundError: when the altered ID is not found in the db
        """
        altered_id_stmt = """SELECT linked_id_metacyc FROM metacyc_compound_ids WHERE altered_id == ?"""
        self.c.execute(altered_id_stmt, (altered_cpd_id,))
        query_for_id_result = self.c.fetchone()
        if query_for_id_result is None:
            raise RecordNotFoundError(message=f"record for {altered_cpd_id} not found")
        linked_id_metacyc = query_for_id_result['linked_id_metacyc']
        combined_select_stmt = """
        SELECT cpd_id, abbreviation, name, formula, inchikey, charge, mass FROM modelseed_compounds
        WHERE cpd_id in 
        (SELECT cpd_id FROM metacyc_compound_aliases WHERE linked_id_metacyc == ?)
        AND is_obsolete != "1";
        """
        self.c.execute(combined_select_stmt, (linked_id_metacyc,))
        record_data = self.c.fetchone()
        compound_info_dict =  self.dictionary_factory(record_data)
        compound_info_dict['altered_id'] = altered_cpd_id
        compound_info_dict['linked_id_metacyc'] = linked_id_metacyc
        return compound_info_dict

    def fetch_metacyc_rxn_info(self, altered_rxn_id):
        """
        fetch reaction info based on metacyc altered ID
        :param altered_rxn_id: a metacyc reaction ID formatted by the framework
        :type altered_rxn_id: str
        :return: metacyc_id, altered_metacyc_id, modelseed_id, name, deltag, stoichiometry
        :rtype: dict
        :raises RecordNotFoundError: when the altered ID is not found in the db
        """
        altered_id_stmt = """SELECT linked_id_metacyc FROM metacyc_reaction_ids WHERE altered_id == ?"""
        self.c.execute(altered_id_stmt, (altered_rxn_id,))
        query_for_id_result = self.c.fetchone()
        if query_for_id_result is None:
            raise RecordNotFoundError(message=f"record for {altered_rxn_id} not found")
        linked_id_metacyc = query_for_id_result['linked_id_metacyc']
        combined_select_stmt = """
        SELECT rxn_id, name, deltag, stoichiometry FROM modelseed_reactions
        WHERE rxn_id in 
        (SELECT rxn_id FROM metacyc_reaction_aliases WHERE linked_id_metacyc == ?)
        AND is_obsolete != "1";
        """
        self.c.execute(combined_select_stmt, (linked_id_metacyc,))
        record_data = self.c.fetchone()
        reaction_info_dict = self.dictionary_factory(record_data)
        reaction_info_dict['altered_id'] = altered_rxn_id
        reaction_info_dict['linked_id_metacyc'] = linked_id_metacyc
        return reaction_info_dict

    def fetch_all_compound_aliases(self, modelseed_compound_id):
        """
        Based on a ModelSEED compound ID, get all aliases from the other databases.
        Results most likely include duplicates, so this function serves as a base for getting the data
        :param modelseed_compound_id: a modelseed copound id
        :type modelseed_compound_id: str
        :return: a list of database fields: modelseed id, metacyc unique id, bigg id, kegg id, name
        :rtype: list of sqlite3.Row objects
        :raises RecordNotFoundError: when None is returned from the query
        """
        compound_left_join_stmt = """
        SELECT modelseed_compounds.cpd_id, metacyc_compound_aliases.linked_id_metacyc, bigg_compound_aliases.linked_id_bigg, kegg_compound_aliases.linked_id_kegg, modelseed_compounds.name FROM modelseed_compounds 
        	LEFT JOIN metacyc_compound_aliases ON modelseed_compounds.cpd_id = metacyc_compound_aliases.cpd_id
        	LEFT JOIN bigg_compound_aliases ON modelseed_compounds.cpd_id = bigg_compound_aliases.cpd_id
        	LEFT JOIN kegg_compound_aliases ON modelseed_compounds.cpd_id = kegg_compound_aliases.cpd_id
        	WHERE modelseed_compounds.cpd_id == ? AND modelseed_compounds.is_obsolete != "1";
        """
        self.c.execute(compound_left_join_stmt, (modelseed_compound_id,))
        data = self.c.fetchall()
        if not data:
            raise RecordNotFoundError(message="no aliases found")
        return data

    def fetch_all_reaction_aliases(self, modelseed_reaction_id):
        """
        Based on a ModelSEED reaction ID, get all aliases from the other databases.
        Results most likely include duplicates, so this function serves as a base for getting the data
        :param modelseed_reaction_id: a modelseed reaction id
        :type modelseed_reaction_id: str
        :return: a list of database fields: modelseed id, metacyc unique id, bigg id, kegg id, name
        :rtype: list of sqlite3.Row objects
        :raises RecordNotFoundError: when None is returned from the query
        """
        reaction_left_join_stmt = """
        SELECT modelseed_reactions.rxn_id, metacyc_reaction_aliases.linked_id_metacyc, bigg_reaction_aliases.linked_id_bigg, kegg_reaction_aliases.linked_id_kegg, modelseed_reactions.name FROM modelseed_reactions 
        	LEFT JOIN metacyc_reaction_aliases ON modelseed_reactions.rxn_id = metacyc_reaction_aliases.rxn_id
        	LEFT JOIN bigg_reaction_aliases ON modelseed_reactions.rxn_id = bigg_reaction_aliases.rxn_id
        	LEFT JOIN kegg_reaction_aliases ON modelseed_reactions.rxn_id = kegg_reaction_aliases.rxn_id
        	WHERE modelseed_reactions.rxn_id == ? AND modelseed_reactions.is_obsolete != "1";
        """
        self.c.execute(reaction_left_join_stmt, (modelseed_reaction_id,))
        data = self.c.fetchall()
        if not data:
            raise RecordNotFoundError(message="no aliases found")
        return data

    def fetch_bigg_cpd_info(self, bigg_cpd_id):
        """
        fetch compound info based on bigg compound ID
        :param bigg_cpd_id: a metacyc compound ID
        :type bigg_cpd_id: str
        :return: bigg_id, modelseed_id, abbrev, name, formula, charge, mass
        :rtype: dict
        :raises RecordNotFoundError: when None is returned from the query
        """
        combined_select_stmt = """
         SELECT cpd_id, abbreviation, name, formula, inchikey, charge, mass FROM modelseed_compounds
         WHERE cpd_id in 
         (SELECT cpd_id FROM bigg_compound_aliases WHERE linked_id_bigg == ?)
         AND is_obsolete != "1";
         """
        self.c.execute(combined_select_stmt, (bigg_cpd_id,))
        record_data = self.c.fetchone()
        if record_data is None:
            raise RecordNotFoundError(message=f"record for {bigg_cpd_id} not found")
        compound_info_dict = self.dictionary_factory(record_data)
        compound_info_dict['linked_id_bigg'] = bigg_cpd_id
        return compound_info_dict

    def fetch_bigg_rxn_info(self, bigg_rxn_id):
        """
        fetch reaction info based on bigg reaction ID
        :param bigg_rxn_id: a bigg reaction ID
        :type bigg_rxn_id: str
        :return: bigg_id, modelseed_id, name, deltag, stoichiometry
        :rtype: dict
        :raises RecordNotFoundError: when None is returned from the query
        """
        combined_select_stmt = """
         SELECT rxn_id, name, deltag, stoichiometry FROM modelseed_reactions
         WHERE rxn_id in 
         (SELECT rxn_id FROM bigg_reaction_aliases WHERE linked_id_bigg == ?)
         AND is_obsolete != "1";
         """
        self.c.execute(combined_select_stmt, (bigg_rxn_id,))
        record_data = self.c.fetchone()
        if record_data is None:
            raise RecordNotFoundError(message=f"record for {bigg_rxn_id} not found")
        reaction_info_dict = self.dictionary_factory(record_data)
        reaction_info_dict['linked_id_bigg'] = bigg_rxn_id
        return reaction_info_dict

    def fetch_kegg_cpd_info(self, kegg_cpd_id):
        """
        fetch compound info based on a kegg compound ID
        :param kegg_cpd_id: a metacyc compound ID
        :type kegg_cpd_id: str
        :return: kegg_id, modelseed_id, abbrev, name, formula, charge, mass
        :rtype: dict
        :raises RecordNotFoundError: when None is returned from the query
        """
        combined_select_stmt = """
         SELECT cpd_id, abbreviation, name, formula, inchikey, charge, mass FROM modelseed_compounds
         WHERE cpd_id in 
         (SELECT cpd_id FROM kegg_compound_aliases WHERE linked_id_kegg == ?)
         AND is_obsolete != "1";
         """
        self.c.execute(combined_select_stmt, (kegg_cpd_id,))
        record_data = self.c.fetchone()
        if record_data is None:
            raise RecordNotFoundError(message=f"record for {kegg_cpd_id} not found")
        compound_info_dict = self.dictionary_factory(record_data)
        compound_info_dict['linked_id_kegg'] = kegg_cpd_id
        return compound_info_dict

    def fetch_kegg_rxn_info(self, kegg_rxn_id):
        """
        fetch reaction info based on kegg reaction ID
        :param kegg_rxn_id: a kegg reaction ID
        :type kegg_rxn_id: str
        :return: kegg_id, modelseed_id, name, deltag, stoichiometry
        :rtype: dict
        :raises RecordNotFoundError: when None is returned from the query
        """
        combined_select_stmt = """
         SELECT rxn_id, name, deltag, stoichiometry FROM modelseed_reactions
         WHERE rxn_id in 
         (SELECT rxn_id FROM kegg_reaction_aliases WHERE linked_id_kegg == ?)
         AND is_obsolete != "1";
         """
        self.c.execute(combined_select_stmt, (kegg_rxn_id,))
        record_data = self.c.fetchone()
        if record_data is None:
            raise RecordNotFoundError(message=f"record for {kegg_rxn_id} not found")
        reaction_info_dict = self.dictionary_factory(record_data)
        reaction_info_dict['linked_id_kegg'] = kegg_rxn_id
        return reaction_info_dict

    @staticmethod
    def get_number_of_carbons(formula):
        carbon_pattern = "C[0-9]*"
        # for all occurrences:
        occurrence_list = re.findall(carbon_pattern, formula)
        # for the first occurrence:
        match_object = re.match(carbon_pattern, formula)
        carbons_found = match_object[0]
        if len(occurrence_list) > 1:
            carbon_count = 0
            for entry in occurrence_list:
                entry = entry.lstrip('C')
                carbon_count += int(entry)
            return  carbon_count
        else:
            return int(carbons_found.lstrip('C'))


class DBLConfigLoader:

    def __init__(self, config_root, project_root):
        if not os.path.isabs(config_root) or not os.path.isabs(project_root):
            self._config_root = os.path.abspath(config_root)
            self._project_root = os.path.abspath(project_root)
        else:
            self._config_root = config_root
            self._project_root = project_root

        if not self._config_root.endswith("/"):
            self._config_root = self._config_root + "/"
        if not self._project_root.endswith("/"):
            self._project_root = self._project_root + "/"

        with open("".join((self._config_root, "dbl_config.yaml")), 'r') as self._config_file:
            self._configdata = load(self._config_file, Loader=Loader)

    @property
    def config_root(self):
        return self._config_root

    @property
    def project_root(self):
        return self._project_root

    def get_data_path(self):
        return self.project_root + self._configdata['data_path']

    def get_database_path(self):
        return self.project_root + self._configdata['database_path']

    def get_bigg_reactions(self):
        return self.get_data_path() + self._configdata['bigg']['reactions']

    def get_bigg_compounds(self):
        return self.get_data_path() + self._configdata['bigg']['compounds']

    def get_modelseed_reactions(self):
        return self.get_data_path() + self._configdata['modelseed']['reactions']

    def get_modelseed_compounds(self):
        return self.get_data_path() + self._configdata['modelseed']['compounds']

    def get_metacyc_reactions(self):
        return self.get_data_path() + self._configdata['metacyc']['reactions']

    def get_metacyc_compounds(self):
        return self.get_data_path() + self._configdata['metacyc']['compounds']


class Filehandler:

    def __init__(self, root_directory=os.getcwd()):
        if root_directory.endswith("/"):
            self._root_directory = root_directory
        else:
            self._root_directory = root_directory + "/"

    @property
    def root_directory(self):
        return self._root_directory

    @root_directory.setter
    def root_directory(self, new_root_dir):
        self._root_directory = new_root_dir

    def build_list(self, file_path):
        """converts an input file to a list
        input file should contain one entry per line
        :param file_path: path to file
        """
        self.return_list = []
        with open(file_path, 'r') as self.file_object:
            for line in self.file_object:
                line = line.strip()
                self.return_list.append(line)
        return self.return_list

    def build_nested_list(self, file_path, sep="\t"):
        """converts an input file to a list of lists, with each line represented by a list
        :param file_path: path to file
        :param sep: separator
        """
        return_list = []
        with open(file_path, 'r') as self.file_object:
            for line in self.file_object:
                line = line.strip()
                line_splitted = line.split(sep)
                return_list.append(line_splitted)
        return return_list

    def list_to_file(self, input_list, file_path, sep="\t"):
        with open(file_path, 'w') as out_file:
            for item in input_list:
                out_file.write(item)

    def get_all_files(self, directory):
        return os.listdir(directory)

    def create_folder(self, target_dir):
        try:
            os.mkdir(target_dir)
        except FileExistsError:
            print(f"dir {str(target_dir)} already exists.")

    def save_serialized_to_file(self, data, filename):
        file_path = "".join((self._root_directory, filename))
        with open(file_path, 'ab') as binary_file:
            pickle.dump(data, binary_file, protocol=pickle.HIGHEST_PROTOCOL)

    def load_serialzed_from_file(self, filename):
        with open(filename, 'rb') as file_source:
            return pickle.load(file_source)

    def create_serialized_object(self, data_object):
        return pickle.dumps(data_object, protocol=pickle.HIGHEST_PROTOCOL)

    def load_serialized_object(self, serialized_object):
        return pickle.loads(serialized_object)

    @property
    def make_datetime_dir(self):
        """create a directory name containing the current date and time
        :return: full path to directory
        :rtype: str
        """
        current_date = str(datetime.now()).split('.')[0]
        current_date.replace(' ', '_')
        working_dir = os.getcwd()
        return '/'.join((working_dir, "arch_extract_" + current_date))

