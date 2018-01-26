# -*- coding: utf8 -*-
import getpass

from database_constructor.database_builder import Database
from pur_beurre.settings import HOST, DATABASE_NAME

DEFAULT_DATABASE = Database(host=HOST, database=DATABASE_NAME, database_exist=True)


class User:
    """
    A row of User table representation
    """

    def __init__(self, username: str = '', password: str = '',
                 database_instance: Database = DEFAULT_DATABASE):
        self.database = database_instance

        self.set_username(username)
        self._set_password(password)
        print('Hello %s' % self.username)

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


class Session:
    """
    A session of use of the app
    """

    def __init__(self, user: User = None):
        self.user = user if isinstance(user, User) else User()
        self.previous_menu = None



class ChoiceMenu:
    """
    Represent a menu which proposes choices to user.
    """

    def __init__(self, text='', choices: list = list()):
        """
        :param text: description of action
        :param choices: a list of tuple with text description and linked Class nam
        """

        self.text = text if text != '' else self.get_text()
        self.choices = choices if choices != [] else self.get_choices()

    def __call__(self, *args, **kwargs):
        """ Always proposes choices to user and return next action and its params as a result"""
        self.print_choices()
        self.collect_choice()
        return self.choices[self.decision][1]()

    def print_choices(self):
        print(self.text)
        for choice in self.choices:
            print(choice[0])

    def collect_choice(self):
        self.decision = int(input("Votre choix :")) - 1

    def get_text(self):
        return NotImplemented

    def get_choices(self):
        """a choice is always a tuple with text description and linked Class name.
        'choices' is a list of tuple"""
        return NotImplemented


class SqlChoiceMenu(ChoiceMenu):
    """
    Represent a menu whose choices are getted from sql query result
    """
    query = ""
    query_parameters = list()

    def __init__(self, text='', choices: list = list(),
                 database_instance: Database = DEFAULT_DATABASE, **kwargs):
        self.database = database_instance
        self.kwargs = kwargs
        super(SqlChoiceMenu, self).__init__(text, choices)

    def __call__(self, *args, **kwargs):
        """ Always proposes choices to user and return next action and its params as a result"""
        self.print_choices()
        self.collect_choice()
        return self.choices[self.decision][1](**self.next_kwargs)

    def get_query(self):
        values = [self.kwargs[field] for field in self.query_parameters]
        query = self.query % tuple(values)
        return [('select', '', query), ]

    def execute_query(self, dictionary=True):
        return self.database.execute_sql_requests(self.get_query(), dictionary=dictionary)

    def get_choices(self):
        results = self.execute_query(dictionary=True)
        choices = []
        for i, result in enumerate(results[0]):
            choices.append(((i + 1, result), self.get_next_class()))
        return choices

    def get_next_class(self):
        return NotImplemented

    @property
    def next_kwargs(self):
        return self.choices[self.decision][0][1]


class SqlData:
    """
    Represent a sql data
    """
    printed_fields = list()

    def __init__(self, database_instance, table, primary_key, **kwargs):
        self.database = database_instance
        self.table = table
        self.primary_key = primary_key
        self.kwargs =kwargs

    def __str__(self):
        return str(self.primary_key)
