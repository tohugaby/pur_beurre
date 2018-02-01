# -*- coding: utf8 -*-
"""
Contains classes used for authentication. Especially User class.
"""

import getpass

from core.lazy_database import DEFAULT_DATABASE
from database_constructor.database_builder import Database


class User:
    """
    A row of User table representation
    """

    def __init__(self, username: str = '', password: str = '',
                 database_instance: Database = DEFAULT_DATABASE):
        self.database = database_instance
        self.username = ''
        self._password = ''
        self.set_username(username)
        self._set_password(password)
        print('Hello %s' % self.username)

    @property
    def id(self):
        """
        Get user id in database.
        :return: user id.
        """
        query = """SELECT * FROM User WHERE username='%s'""" % self.username
        results = self.database.execute_sql_requests([('select', 'User', query), ],
                                                     dictionary=True)
        return results[0][0]['id']

    def set_username(self, username):
        """
        Take username from provided parameter or ask it to program user until it is valid.
        :param username: Provided username
        :return: None
        """
        self.username = username
        while not self.username_is_valid:
            self.username = input("username : ")

    def _get_password(self):
        """
        A getter that prevent program user from displaying password in clear.
        :return: None
        """
        print("Oh no! you can't see this information. What a pity...")
        return

    def _set_password(self, password):
        """
        Take password from provided parameter or ask it to program user until it is valid.
        :param password: Provided password
        :return: None
        """
        self._password = password
        while not self.password_is_valid:
            self._password = getpass.getpass()

    @property
    def username_is_valid(self):
        """
        Confirms validity of username by checking if it exists in database.
        :return: True or False
        """
        query = """SELECT count(*) FROM User WHERE username='%s' """ % self.username
        results = self.database.execute_sql_requests([('select', 'User', query)])
        return results[0][0][0] == 1

    @property
    def password_is_valid(self):
        """
        Confirms validity of password  by checking if it match with those in database for given username.
        :return: True or False
        """
        query = """SELECT password FROM User WHERE username='%s'""" % self.username
        results = self.database.execute_sql_requests([('select', 'User', query)])
        return results[0][0][0] == self._password

    password = property(_get_password, _set_password)
