class RecordNotFoundError(Exception):
    """Exception raised when no record was found in the database for the input
    """
    def __init__(self, message):
        self.message = message

class MissingCarbonError(ValueError):
    """Exception raised when a chemical formula contains no carbon atoms
    """
    def __init__(self, message="Formula contains no carbon atoms."):
        self.message = message