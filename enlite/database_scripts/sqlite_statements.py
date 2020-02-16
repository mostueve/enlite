compound_list_fields = [
'id',
'abbreviation',
'name',
'charge',
'formula',
'mass',
'pka',
'pkb',
'deltag',
'source',
'is_cofactor',
'is_core',
'is_obsolete',
'linked_compound',
'deltagerr',
'inchikey',
'abstract_compound',
'aliases',
'smiles',
'comprised_of',
'notes',
'ontology'
]

reaction_list_fields = [
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


compound_db_creation = """
CREATE TABLE IF NOT EXISTS modelseed_compounds (
id INTEGER PRIMARY KEY,
cpd_id TEXT,
abbreviation TEXT,
name TEXT,
charge TEXT,
formula TEXT,
mass REAL,
pka REAL,
pkb REAL,
deltag REAL,
source TEXT,
is_cofactor TEXT,
is_core TEXT,
is_obsolete TEXT,
linked_compound TEXT,
deltagerr REAL,
inchikey TEXT,
abstract_compound TEXT,
aliases TEXT,
smiles TEXT,
comprised_of TEXT,
notes TEXT,
ontology TEXT
)
"""

reaction_db_creation = """
CREATE TABLE IF NOT EXISTS modelseed_reactions (
id INTEGER PRIMARY KEY,
rxn_id TEXT,
abbreviation TEXT,
name TEXT,
ec_numbers TEXT,
direction TEXT,
reversibility TEXT,
deltag REAL,
definition TEXT,
source TEXT,
status TEXT,
compound_ids TEXT,
deltagerr REAL,
code TEXT,
equation TEXT,
stoichiometry TEXT,
is_obsolete TEXT,
is_transport TEXT,
linked_reaction TEXT,
abstract_reaction TEXT,
notes TEXT,
ontology TEXT,
aliases TEXT,
pathways TEXT
)
"""

biggreactions_db_creation = """
CREATE TABLE IF NOT EXISTS biggreactions (
	id INTEGER PRIMARY KEY,
	biggreaction_id TEXT,
	name TEXT,
	reaction_string TEXT,
	model_list TEXT,
	database_links TEXT,
	old_bigg_ids TEXT
);
"""

biggcompounds_db_creation = """
CREATE TABLE IF NOT EXISTS biggcompounds (
	id INTEGER PRIMARY KEY,
	biggcompound_id TEXT,
	universal_bigg_id TEXT,
	name TEXT,
	model_list TEXT,
	database_links TEXT,
	old_bigg_ids TEXT
);
"""
insert_biggreactions = """
INSERT INTO biggreactions (
'biggreaction_id',
'name',
'reaction_string',
'model_list',
'database_links',
'old_bigg_ids'
)
VALUES (?, ?, ?, ?, ?, ?)"""

insert_biggcompounds = """
INSERT INTO biggcompounds (
'biggcompound_id',
'universal_bigg_id',
'name',
'model_list',
'database_links',
'old_bigg_ids'
)
VALUES (?, ?, ?, ?, ?, ?)"""



insert_stmt_ec_aliases = """
					INSERT INTO ec_numbers (
					'ec_number')
					VALUES (?)"""
					
insert_stmt_ec_links = """
					INSERT INTO ec_numbers_linked_reactions (
					'id_reaction',
					'id_ecnumber',
					'rxn_id',
					'ec_number')
					VALUES (?, ?, ?, ?)"""

creation_stmt_ec_aliases = """
CREATE TABLE IF NOT EXISTS ec_numbers (
id INTEGER PRIMARY KEY,
ec_number TEXT
);
"""

creation_stmt_ecnumber_links = """
CREATE TABLE IF NOT EXISTS ec_numbers_linked_reactions (
id_reaction INTEGER,
id_ecnumber INTEGER,
rxn_id TEXT,
ec_number TEXT,
FOREIGN KEY(id_reaction) REFERENCES modelseed_reactions(id),
FOREIGN KEY(id_ecnumber) REFERENCES ec_numbers(id)
);
"""


creation_stmt_metacyc_reaction_aliases = """
CREATE TABLE IF NOT EXISTS metacyc_reaction_ids (
id INTEGER PRIMARY KEY,
linked_id_metacyc TEXT,
altered_id TEXT
);
"""

creation_stmt_metacyc_reaction_links = """
CREATE TABLE IF NOT EXISTS metacyc_reaction_aliases (
id_reaction INTEGER,
id_metacyc INTEGER,
rxn_id TEXT,
linked_id_metacyc TEXT,
FOREIGN KEY(id_reaction) REFERENCES modelseed_reactions(id),
FOREIGN KEY(id_metacyc) REFERENCES metacyc_reaction_ids(id)
);
"""

creation_stmt_kegg_reaction_aliases = """
CREATE TABLE IF NOT EXISTS kegg_reaction_ids (
id INTEGER PRIMARY KEY,
linked_id_kegg TEXT
);
"""

creation_stmt_kegg_reaction_links = """
CREATE TABLE IF NOT EXISTS kegg_reaction_aliases (
id_reaction INTEGER,
id_kegg INTEGER,
rxn_id TEXT,
linked_id_kegg TEXT,
FOREIGN KEY(id_reaction) REFERENCES modelseed_reactions(id),
FOREIGN KEY(id_kegg) REFERENCES kegg_reaction_ids(id)
);
"""

creation_stmt_bigg_reaction_aliases = """
CREATE TABLE IF NOT EXISTS bigg_reaction_ids (
id INTEGER PRIMARY KEY,
linked_id_bigg TEXT
);
"""

creation_stmt_bigg_reaction_links = """
CREATE TABLE IF NOT EXISTS bigg_reaction_aliases (
id_reaction INTEGER,
id_bigg INTEGER,
rxn_id TEXT,
linked_id_bigg TEXT,
FOREIGN KEY(id_reaction) REFERENCES modelseed_reactions(id),
FOREIGN KEY(id_bigg) REFERENCES bigg_reaction_ids(id)
);
"""

insert_stmt_metacyc_reaction_links = """
					INSERT INTO metacyc_reaction_aliases (
					'id_reaction',
					'id_metacyc',
					'rxn_id',
					'linked_id_metacyc')
					VALUES (?, ?, ?, ?)"""
insert_stmt_metacyc_reaction_aliases = """
					INSERT INTO metacyc_reaction_ids (
					'linked_id_metacyc',
					'altered_id'
					)
					VALUES (?, ?)"""

insert_stmt_kegg_reaction_links = """
					INSERT INTO kegg_reaction_aliases (
					'id_reaction',
					'id_kegg',
					'rxn_id',
					'linked_id_kegg')
					VALUES (?, ?, ?, ?)"""
					
insert_stmt_kegg_reaction_aliases = """
					INSERT INTO kegg_reaction_ids (
					'linked_id_kegg'
					)
					VALUES (?)"""

insert_stmt_bigg_reaction_links = """
					INSERT INTO bigg_reaction_aliases (
					'id_reaction',
					'id_bigg',
					'rxn_id',
					'linked_id_bigg')
					VALUES (?, ?, ?, ?)"""
					
insert_stmt_bigg_reaction_aliases = """
					INSERT INTO bigg_reaction_ids (
					'linked_id_bigg'
					)
					VALUES (?)"""


creation_stmt_metacyc_compound_aliases = """
CREATE TABLE IF NOT EXISTS metacyc_compound_ids (
id INTEGER PRIMARY KEY,
linked_id_metacyc TEXT,
altered_id TEXT
);
"""

creation_stmt_metacyc_compound_links = """
CREATE TABLE IF NOT EXISTS metacyc_compound_aliases (
id_compound INTEGER,
id_metacyc INTEGER,
cpd_id TEXT,
linked_id_metacyc TEXT,
FOREIGN KEY(id_compound) REFERENCES modelseed_compounds(id),
FOREIGN KEY(id_metacyc) REFERENCES metacyc_compound_ids(id)
);
"""

creation_stmt_kegg_compound_aliases = """
CREATE TABLE IF NOT EXISTS kegg_compound_ids (
id INTEGER PRIMARY KEY,
linked_id_kegg TEXT
);
"""

creation_stmt_kegg_compound_links = """
CREATE TABLE IF NOT EXISTS kegg_compound_aliases (
id_compound INTEGER,
id_kegg INTEGER,
cpd_id TEXT,
linked_id_kegg TEXT,
FOREIGN KEY(id_compound) REFERENCES modelseed_compounds(id),
FOREIGN KEY(id_kegg) REFERENCES kegg_compound_ids(id)
);
"""

creation_stmt_bigg_compound_aliases = """
CREATE TABLE IF NOT EXISTS bigg_compound_ids (
id INTEGER PRIMARY KEY,
linked_id_bigg TEXT
);
"""

creation_stmt_bigg_compound_links = """
CREATE TABLE IF NOT EXISTS bigg_compound_aliases (
id_compound INTEGER,
id_bigg INTEGER,
cpd_id TEXT,
linked_id_bigg TEXT,
FOREIGN KEY(id_compound) REFERENCES modelseed_compounds(id),
FOREIGN KEY(id_bigg) REFERENCES bigg_compound_ids(id)
);
"""

insert_stmt_metacyc_compound_links = """
					INSERT INTO metacyc_compound_aliases (
					'id_compound',
					'id_metacyc',
					'cpd_id',
					'linked_id_metacyc')
					VALUES (?, ?, ?, ?)"""
insert_stmt_metacyc_compound_aliases = """
					INSERT INTO metacyc_compound_ids (
					'linked_id_metacyc',
					'altered_id'
					)
					VALUES (?, ?)"""

insert_stmt_kegg_compound_links = """
					INSERT INTO kegg_compound_aliases (
					'id_compound',
					'id_kegg',
					'cpd_id',
					'linked_id_kegg')
					VALUES (?, ?, ?, ?)"""
					
insert_stmt_kegg_compound_aliases = """
					INSERT INTO kegg_compound_ids (
					'linked_id_kegg')
					VALUES (?)"""

insert_stmt_bigg_compound_links = """
					INSERT INTO bigg_compound_aliases (
					'id_compound',
					'id_bigg',
					'cpd_id',
					'linked_id_bigg')
					VALUES (?, ?, ?, ?)"""
					
insert_stmt_bigg_compound_aliases = """
					INSERT INTO bigg_compound_ids (
					'linked_id_bigg')
					VALUES (?)"""
					
insert_stmt_compounds = """
INSERT INTO modelseed_compounds (
'cpd_id',
'abbreviation',
'name',
'charge',
'formula',
'mass',
'pka',
'pkb',
'deltag',
'source',
'is_cofactor',
'is_core',
'is_obsolete',
'linked_compound',
'deltagerr',
'inchikey',
'abstract_compound',
'aliases',
'smiles',
'comprised_of',
'notes',
'ontology'
)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
"""

insert_stmt_reactions = """
INSERT INTO modelseed_reactions (
'rxn_id',
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
) 
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
"""


create_metacyccompounds = """
CREATE TABLE IF NOT EXISTS metacyccompounds (
	id INTEGER PRIMARY KEY,
	unique_id TEXT,
	types TEXT,
	common_name TEXT,
	abbrev_name TEXT,
	accession_1 TEXT,
	anticodon TEXT,
	atom_charges TEXT,
	atom_isotopes TEXT,
	catalyzes TEXT,
	cfg_icon_color TEXT,
	chemical_formula TEXT,
	citations TEXT,
	coding_segments TEXT,
	codons TEXT,
	cofactors_of TEXT,
	comment TEXT,
	component_coefficients TEXT,
	component_of TEXT,
	components TEXT,
	consensus_sequence TEXT,
	copy_number TEXT,
	credits TEXT,
	data_source TEXT,
	dblinks TEXT,
	dna_footprint_size TEXT,
	documentation TEXT,
	enzyme_not_used_in TEXT,
	expression_mechanism TEXT,
	fast_equilibrating_instances TEXT,
	features TEXT,
	functional_assignment_comment TEXT, 
	functional_assignment_status TEXT,
	gene TEXT,
	gibbs_0 TEXT,
	go_terms TEXT,
	group_coords_2d TEXT,
	group_internals TEXT,
	has_no_structure TEXT,
	hide_slot TEXT,
	in_mixture TEXT,
	inchi TEXT,
	inchi_key TEXT,
	instance_name_template TEXT,
	internals_of_group TEXT,
	isozyme_sequence_similarity TEXT,
	left_end_position TEXT,
	locations TEXT,
	member_sort_fn TEXT,
	modified_form TEXT,
	molecular_weight TEXT,
	molecular_weight_exp TEXT,
	molecular_weight_kd TEXT,
	molecular_weight_seq TEXT,
	monoisotopic_mw TEXT,
	n_plus_1_name TEXT,
	n_1_name TEXT,
	n_name TEXT,
	neidhardt_spot_number TEXT,
	non_standard_inchi TEXT,
	pathologic_name_matcher_evidence TEXT,
	pathologic_pwy_evidence TEXT,
	pi TEXT,
	pka1 TEXT,
	pka2 TEXT,
	pka3 TEXT,
	radical_atoms TEXT,
	regulated_by TEXT,
	regulates TEXT,
	right_end_position TEXT,
	smiles TEXT,
	species TEXT,
	splice_form_introns TEXT,
	structure_groups TEXT,
	structure_links TEXT,
	superatoms TEXT,
	symmetry TEXT,
	synonyms TEXT,
	systematic_name TEXT,
	tautomers TEXT,
	unmodified_form TEXT
);
"""


create_metacycreactions = """
CREATE TABLE IF NOT EXISTS metacycreactions (
	id INTEGER PRIMARY KEY,
	unique_id TEXT,
	types TEXT,
	common_name TEXT,
	atom_mappings TEXT,
	cannot_balance TEXT,
	citations TEXT,
	comment TEXT,
	credits TEXT,
	data_source TEXT,
	dblinks TEXT,
	documentation TEXT,
	ec_number TEXT,
	enzymatic_reaction TEXT,
	enzymes_not_used TEXT,
	equilibrium_constant TEXT,
	gibbs_0 TEXT,
	hide_slot TEXT,
	in_pathway TEXT,
	instance_name_template TEXT,
	left TEXT,
	member_sort_fn TEXT,
	orphan TEXT,
	pathologic_name_matcher_evidence TEXT,
	pathologic_pwy_evidence TEXT,
	physiologically_relevant TEXT,
	predecessors TEXT,
	primaries TEXT,
	reaction_balance_status TEXT,
	reaction_direction TEXT,
	reaction_list TEXT,
	regulated_by TEXT,
	requirements TEXT,
	right TEXT,
	rxn_locations TEXT,
	signal TEXT,
	species TEXT,
	spontaneous TEXT,
	std_reduction_potential TEXT,
	synonyms TEXT,
	systematic_name TEXT,
	taxonomic_range TEXT
);
"""

metacyc_reactions_insert = """
	INSERT INTO metacycreactions (
	'unique_id',
	'types',
	'common_name',
	'atom_mappings',
	'cannot_balance',
	'citations',
	'comment',
	'credits',
	'data_source',
	'dblinks',
	'documentation',
	'ec_number',
	'enzymatic_reaction',
	'enzymes_not_used',
	'equilibrium_constant',
	'gibbs_0',
	'hide_slot',
	'in_pathway',
	'instance_name_template',
	'left',
	'member_sort_fn',
	'orphan',
	'pathologic_name_matcher_evidence',
	'pathologic_pwy_evidence',
	'physiologically_relevant',
	'predecessors',
	'primaries',
	'reaction_balance_status',
	'reaction_direction',
	'reaction_list',
	'regulated_by',
	'requirements',
	'right',
	'rxn_locations',
	'signal',
	'species',
	'spontaneous',
	'std_reduction_potential',
	'synonyms',
	'systematic_name',
	'taxonomic_range'
	)
	VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
"""


metacyc_compounds_insert = """
	INSERT INTO metacyccompounds (
	'unique_id',
	'types',
	'common_name',
	'abbrev_name',
	'accession_1',
	'anticodon',
	'atom_charges',
	'atom_isotopes',
	'catalyzes',
	'cfg_icon_color',
	'chemical_formula',
	'citations',
	'coding_segments',
	'codons',
	'cofactors_of',
	'comment',
	'component_coefficients',
	'component_of',
	'components',
	'consensus_sequence',
	'copy_number',
	'credits',
	'data_source',
	'dblinks',
	'dna_footprint_size',
	'documentation',
	'enzyme_not_used_in',
	'expression_mechanism',
	'fast_equilibrating_instances',
	'features',
	'functional_assignment_comment', 
	'functional_assignment_status',
	'gene',
	'gibbs_0',
	'go_terms',
	'group_coords_2d',
	'group_internals',
	'has_no_structure',
	'hide_slot',
	'in_mixture',
	'inchi',
	'inchi_key',
	'instance_name_template',
	'internals_of_group',
	'isozyme_sequence_similarity',
	'left_end_position',
	'locations',
	'member_sort_fn',
	'modified_form',
	'molecular_weight',
	'molecular_weight_exp',
	'molecular_weight_kd',
	'molecular_weight_seq',
	'monoisotopic_mw',
	'n_plus_1_name',
	'n_1_name',
	'n_name',
	'neidhardt_spot_number',
	'non_standard_inchi',
	'pathologic_name_matcher_evidence',
	'pathologic_pwy_evidence',
	'pi',
	'pka1',
	'pka2',
	'pka3',
	'radical_atoms',
	'regulated_by',
	'regulates',
	'right_end_position',
	'smiles',
	'species',
	'splice_form_introns',
	'structure_groups',
	'structure_links',
	'superatoms',
	'symmetry',
	'synonyms',
	'systematic_name',
	'tautomers',
	'unmodified_form'
	)
	VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
"""
