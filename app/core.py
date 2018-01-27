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


class ChoiceMenu:
    """
    Represent a menu which proposes choices to user.
    """
    SESSION_CLASS = Session

    def __init__(self, text='', choices: list = list(), **kwargs):
        """
        :param text: description of action
        :param choices: a list of tuple with text description and linked Class nam
        """
        # self.kwargs must be define before self.choices because it calls self.get_choices
        # method which uses self.kwargs
        self.kwargs = kwargs
        self.text = text if text != '' else self.get_text()
        self.choices = choices if choices != [] else self.get_choices()

    def __call__(self, *args, **kwargs):
        """ Always proposes choices to user and return next action and its params as a result"""
        self.base_call_process()
        return self.choices[self.decision][1](**self.next_kwargs)

    def update_session(self):
        """ Update SESSION_CLASS actual instance with first and previous menu"""
        self.__class__.SESSION_CLASS.ACTUAL_INSTANCE.previous_menu = self
        if self.__class__.SESSION_CLASS.ACTUAL_INSTANCE.first_menu is None:
            self.__class__.SESSION_CLASS.ACTUAL_INSTANCE.first_menu = self

    def base_call_process(self):
        """Base action to process in __call__ method"""
        self.print_choices()
        self.collect_choice()
        self.update_session()

    def print_choices(self):
        """Print explanation text and possible choices """
        print(self.text)
        for choice in self.choices:
            print(choice[0])

    def collect_choice(self):
        """ collect inputed user choice"""
        # TODO: need to make more reliable by managing bad inputs and propose to quit or go back
        self.decision = int(input("Votre choix :")) - 1

    def get_text(self):
        """return choice explanation text"""
        return NotImplemented

    def get_choices(self):
        """a choice is always a tuple with text description and linked Class name.
        'choices' is a list of tuple"""
        return NotImplemented

    @property
    def next_kwargs(self):
        """ kwargs needed by next class """
        return dict()


class SqlChoiceMenu(ChoiceMenu):
    """
    Represent a menu whose choices are getted from sql query result
    """
    query = ""
    query_parameters = list()

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
    def database(self):
        return self.__class__.SESSION_CLASS.ACTUAL_INSTANCE.database_instance

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
        self.kwargs = kwargs

    def __str__(self):
        return str(self.primary_key)
