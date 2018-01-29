from core.authenthication import User
from database_constructor.database_builder import Database
from pur_beurre.settings import HOST, DATABASE_NAME

DEFAULT_DATABASE = Database(host=HOST, database=DATABASE_NAME, database_exist=True)


class Session:
    """
    A session of use of the app
    """
    ACTUAL_INSTANCE = None

    def __init__(self, database_instance: Database = DEFAULT_DATABASE, user: User = None):
        self.database_instance = database_instance
        if isinstance(user, User) and user.database == self.database_instance:
            self.user = user
        else:
            self.user = User(database_instance=self.database_instance)
        self.first_menu = None
        self.previous_menu = None

    @classmethod
    def add_instance(cls, instance):
        cls.ACTUAL_INSTANCE = instance

    def __enter__(self):
        self.__class__.add_instance(self)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.__class__.add_instance(None)
