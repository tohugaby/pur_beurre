from core.sessions import Session


class SqlData:
    """
    Represent a sql data
    """
    SESSION_CLASS = Session
    printed_fields = list()

    def __init__(self, database_instance, table, primary_key, **kwargs):
        self.database = database_instance
        self.table = table
        self.primary_key = primary_key
        self.kwargs = kwargs

    def __str__(self):
        return str(self.primary_key)
