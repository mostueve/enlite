import re

from enlite.classes.CustomExceptions import MissingCarbonError, RecordNotFoundError


class Enliter:
    def __init__(self, db_handler, filehandler):
        self._db_handler = db_handler
        self._filehandler = filehandler

    @staticmethod
    def get_number_of_carbons(formula):
        """
        From a chemical sum formula, extract the number of carbon atoms.
        :raises MissingCarbonError: if there are no carbon atoms in the formula
        :param formula: a chemical sum formula, e.g. CO2, C6H12O6, N2O etc
        :type formula: str
        :return: the number of carbon atoms
        :rtype: int
        """
        if "C" not in formula:
            raise MissingCarbonError
        simple_carbon_pattern = "C[0-9]*"
        # () define groups
        # ?! is a negative lookahead -> do not match this
        # C[a-z] means one capital C followed by one lowercase letter
        # C[0-9]* means one capital C followed by none or many digits
        carbon_pattern = "(?!C[a-z])(C[0-9]*)"
        # for all occurrences:
        occurrence_list = re.findall(carbon_pattern, formula)
        # for the first occurrence:
        match_object = re.match(carbon_pattern, formula)
        carbons_found = match_object[0]
        if len(occurrence_list) > 1:
            carbon_count = 0
            for entry in occurrence_list:
                if entry != "C":
                    entry = entry.lstrip('C')
                    carbon_count += int(entry)
                elif len(entry) == 1 and entry == "C":
                    carbon_count += 1
            return carbon_count
        else:
            if carbons_found == "C":
                return 1
            else:
                return int(carbons_found.lstrip('C'))

    def find_compound_alias_single(self, compound_id, db_name_in, db_name_out, metacyc_id_is_altered=False):
        try:
            cpd_alias_records = self._db_handler.fetch_compound_alias(compound_id, db_name_in, metacyc_id_is_altered)
        except RecordNotFoundError as no_record_error:
            print(no_record_error.message)
            return
        records_dict = self.handle_multiple_occurrences_compounds(cpd_alias_records)
        if db_name_out == 'all':
            return records_dict
        else:
            alias_key = f"{db_name_out}_aliases"
            alias_list = records_dict[alias_key]
            return alias_list[0]

    def find_compound_alias_multi(self, compound_list, db_name_in, db_name_out, metacyc_id_is_altered=False):
        aliases_dict = {}
        for compound_id in compound_list:
            try:
                cpd_alias_records = self._db_handler.fetch_compound_alias(compound_id, db_name_in, metacyc_id_is_altered)
            except RecordNotFoundError as no_record_error:
                print(no_record_error.message)
                continue
            records_dict = self.handle_multiple_occurrences_compounds(cpd_alias_records)
            alias_key = f"{db_name_out}_aliases"
            alias_list = records_dict[alias_key]
            aliases_dict[compound_id] = alias_list
        return aliases_dict

    def find_reaction_alias_single(self, reaction_id, db_name_in, db_name_out, metacyc_id_is_altered=False):
        try:
            rxn_alias_records = self._db_handler.fetch_reaction_alias(reaction_id, db_name_in, metacyc_id_is_altered)
        except RecordNotFoundError as no_record_error:
            print(no_record_error.message)
            return
        records_dict = self.handle_multiple_occurrences_reactions(rxn_alias_records)
        if db_name_out == 'all':
            return records_dict
        else:
            alias_key = f"{db_name_out}_aliases"
            alias_list = records_dict[alias_key]
            return alias_list[0]

    def find_reaction_alias_multi(self, reaction_list, db_name_in, db_name_out, metacyc_id_is_altered=False):
        aliases_dict = {}
        for reaction_id in reaction_list:
            try:
                cpd_alias_records = self._db_handler.fetch_reaction_alias(reaction_id, db_name_in,
                                                                          metacyc_id_is_altered)
            except RecordNotFoundError as no_record_error:
                print(no_record_error.message)
                continue
            records_dict = self.handle_multiple_occurrences_reactions(cpd_alias_records)
            alias_key = f"{db_name_out}_aliases"
            alias_list = records_dict[alias_key]
            aliases_dict[reaction_id] = alias_list
        return aliases_dict

    @staticmethod
    def handle_multiple_occurrences_compounds(records):
        """
        Pass in a query result from the left_outer_join statement
        :param records: a list of sqlite3.Row objects from one of the fetch_all_aliases methods
        :type records: list of sqlite3.Row objects
        :return: dictionary of lists holding the respective aliases for each database
        :rtype: dict
        """
        modelseed_alias_list = []
        metacyc_alias_list = []
        bigg_alias_list = []
        kegg_alias_list = []
        for subrecord in records:
            # due to the row_factory option, columns can be accessed by name
            mod_al = subrecord['cpd_id']
            met_al = subrecord['linked_id_metacyc']
            big_al = subrecord['linked_id_bigg']
            keg_al = subrecord['linked_id_kegg']
            if mod_al not in modelseed_alias_list:
                modelseed_alias_list.append(mod_al)
            if met_al not in metacyc_alias_list:
                metacyc_alias_list.append(met_al)
            if big_al not in bigg_alias_list:
                bigg_alias_list.append(big_al)
            if keg_al not in kegg_alias_list:
                kegg_alias_list.append(keg_al)
        return {
            'modelseed_aliases': modelseed_alias_list,
            'metacyc_aliases': metacyc_alias_list,
            'bigg_aliases': bigg_alias_list,
            'kegg_aliases': kegg_alias_list
        }

    @staticmethod
    def handle_multiple_occurrences_reactions(records):
        """
        Pass in a query result from the left_outer_join statement
        :param records: a list of sqlite3.Row objects from one of the fetch_all_aliases methods
        :type records: list of sqlite3.Row objects
        :return: dictionary of lists holding the respective aliases for each database
        :rtype: dict
        """
        modelseed_alias_list = []
        metacyc_alias_list = []
        bigg_alias_list = []
        kegg_alias_list = []
        for subrecord in records:
            # due to the row_factory option, columns can be accessed by name
            mod_al = subrecord['rxn_id']
            met_al = subrecord['linked_id_metacyc']
            big_al = subrecord['linked_id_bigg']
            keg_al = subrecord['linked_id_kegg']
            if mod_al not in modelseed_alias_list:
                modelseed_alias_list.append(mod_al)
            if met_al not in metacyc_alias_list:
                metacyc_alias_list.append(met_al)
            if big_al not in bigg_alias_list:
                bigg_alias_list.append(big_al)
            if keg_al not in kegg_alias_list:
                kegg_alias_list.append(keg_al)
        return {
            'modelseed_aliases': modelseed_alias_list,
            'metacyc_aliases': metacyc_alias_list,
            'bigg_aliases': bigg_alias_list,
            'kegg_aliases': kegg_alias_list
        }