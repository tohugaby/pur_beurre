# -*- coding: utf8 -*-
"""
Contains classes that allows to create a program session.
"""
from core.authenthication import User
from core.lazy_database import DEFAULT_DATABASE
from database_constructor.database_builder import Database


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

    def __str__(self):
        return self.get_session_status()


    def get_session_status(self):
        """
        Actual state of the session.
        :return: a dict containing actual state information
        """
        return {
            'database': self.database_instance.database,
            'user': self.user.username,
            'first_menu': self.first_menu,
            'previous_menu': self.previous_menu
        }

    @classmethod
    def add_instance(cls, instance):
        """
        Set actual instance in class attribute ACTUAL instance.
        :param instance: instance of Session class.
        :return: None
        """
        cls.ACTUAL_INSTANCE = instance

    def __enter__(self):
        self.__class__.add_instance(self)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.__class__.add_instance(None)
