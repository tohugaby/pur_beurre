import getpass

from core.sessions import DEFAULT_DATABASE
from database_constructor.database_builder import Database


class User:
    """
    A row of User table representation
    """

    def __init__(self, username: str = '', password: str = '',
                 database_instance: Database = DEFAULT_DATABASE):
        self.database = database_instance
        self.username = ''
        self.password = ''
        self.set_username(username)
        self._set_password(password)
        print('Hello %s' % self.username)

    @property
    def id(self):
        query = """SELECT * FROM User WHERE username='%s'""" % self.username
        results = self.database.execute_sql_requests([('select', 'User', query), ],
                                                     dictionary=True)
        return results[0][0]['id']

    def set_username(self, username):
        self.username = username
        while not self.username_is_valid:
            self.username = input("username : ")

    def _get_password(self):
        print("Oh no! you can't see this information. What a pity...")
        return

    def _set_password(self, password):
        self._password = password
        while not self.password_is_valid:
            self._password = getpass.getpass()

    @property
    def username_is_valid(self):
        query = """SELECT count(*) FROM User WHERE username='%s' """ % self.username
        results = self.database.execute_sql_requests([('select', 'User', query)])
        return results[0][0][0] == 1

    @property
    def password_is_valid(self):
        query = """SELECT password FROM User WHERE username='%s'""" % self.username
        results = self.database.execute_sql_requests([('select', 'User', query)])
        return results[0][0][0] == self._password

    password = property(_get_password, _set_password)
