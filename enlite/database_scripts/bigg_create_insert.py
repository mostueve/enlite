import traceback

import sqlite3

from classes.DataHandlers import DBLConfigLoader, Filehandler
from . sqlite_statements import biggcompounds_db_creation, biggreactions_db_creation, insert_biggcompounds, insert_biggreactions


filehandler = Filehandler()

dbl_config = DBLConfigLoader(config_root="../config", project_root="..")
db_path = dbl_config.get_database_path()
conn = sqlite3.connect(db_path)
c = conn.cursor()
c.execute("PRAGMA foreign_keys = 1")

list_bigg_reactions = filehandler.build_nested_list(dbl_config.get_bigg_reactions())
list_bigg_compounds = filehandler.build_nested_list(dbl_config.get_bigg_compounds())

try:
	c.execute(biggreactions_db_creation)
	c.execute(biggcompounds_db_creation)
	c.executemany(insert_biggreactions, list_bigg_reactions)
	# might have to manually fix the newlines in the records on lines 6378 and 12959
	# the newlines inserted vary!
	c.executemany(insert_biggcompounds, list_bigg_compounds)
except Exception:
	print("an error occurred:")
	traceback.print_exc()
finally:
	conn.commit()
	
conn.close()
