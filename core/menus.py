# -*- coding: utf8 -*-
"""
Contains classes that reprensent base choice menu.
"""
import sys

from core.sessions import Session


class ChoiceMenu:
    """
    Represent a menu which proposes choices to user.
    """
    SESSION_CLASS = Session

    def __init__(self, text='', choices: list = None, **kwargs):
        """
        :param text: description of action
        :param choices: a list of tuple with text description and linked Class nam
        """
        # self.kwargs must be define before self.choices because it calls self.get_choices
        # method which uses self.kwargs
        self.decision = None
        self.kwargs = kwargs
        self.text = text if text != '' else self.get_text()
        self.choices = choices if choices is not None else self.get_choices()

    def __call__(self, *args, **kwargs):
        """
         Always proposes choices to user and return next action and its params as a result.
        :param args:
        :param kwargs:
        :return: instance of next_class
        """
        if not self.base_call_process():
            return self.__class__.SESSION_CLASS.ACTUAL_INSTANCE.previous_menu()
        return self.choices[self.decision][1](**self.next_kwargs)

    def update_session(self):
        """
        Update SESSION_CLASS actual instance with first and previous menu.
        :return: None
        """
        self.__class__.SESSION_CLASS.ACTUAL_INSTANCE.previous_menu = self
        if self.__class__.SESSION_CLASS.ACTUAL_INSTANCE.first_menu is None:
            self.__class__.SESSION_CLASS.ACTUAL_INSTANCE.first_menu = self

    def base_call_process(self):
        """
        Base action to process in __call__ method.
        :return: True
        """
        self.print_choices()
        self.collect_choice()
        if self.decision == 'q':
            print('Exiting program')
            sys.exit(0)
        if self.decision == 'p':
            print('going to previous menu')
            return False
        self.update_session()
        return True

    def print_choices(self):
        """
        Print explanation text and possible choices.
        :return: None
        """
        print(self.text)
        for choice in self.choices:
            print(choice[0])

    def collect_choice(self):
        """
        Collect user choice input.
        :return: None
        """
        self.decision = None
        possible_choice = list(range(len(self.choices))) + ['q']
        if self.__class__.SESSION_CLASS.ACTUAL_INSTANCE.previous_menu is not None:
            possible_choice.append('p')
        while self.decision not in possible_choice:
            decision = input("Votre choix :")
            try:
                self.decision = int(decision) - 1
            except ValueError:
                print(self.decision)
                self.decision = decision

    def get_text(self):
        """
        Choice explanation text.
        :return: An explanation text
        """
        return NotImplemented

    def get_choices(self):
        """
        A choice is always a tuple with text description and linked Class name.'choices' is a list of tuple.
        :return: A list of choice.
        """
        return NotImplemented

    @property
    def next_kwargs(self):
        """
        Determines kwargs needed by next class instance.
        :return: a dict of next kwargs
        """
        return dict()


class SqlChoiceMenu(ChoiceMenu):
    """
    Represent a menu whose choices are getted from sql query result
    """
    query = ""
    query_parameters = list()

    def get_query(self):
        """
        Generate query used to list choices.
        :return: a list of tuple containing query
        """
        values = [self.kwargs[field] for field in self.query_parameters]
        query = self.query % tuple(values)
        return [('select', '', query), ]

    def execute_query(self, dictionary=True):
        """
        Execute object query and return results.
        :param dictionary: indicates if query result should be a list of dict or of tuples
        :return: list of dict or of tuples
        """
        return self.database.execute_sql_requests(self.get_query(), dictionary=dictionary)

    def get_choices(self):
        """
        A choice is always a tuple with text description and linked Class name.'choices' is a list of tuple.
        :return: A list of choice.
        """
        results = self.execute_query(dictionary=True)
        choices = []
        for i, result in enumerate(results[0]):
            choices.append(((i + 1, result), self.get_next_class()))
        return choices

    def get_next_class(self):
        """
        Indicate the next class instances to return with __call__ method
        :return: A class name.
        """
        return NotImplemented

    @property
    def database(self):
        """
        Determines database used to execute query
        :return: A database instance
        """
        return self.__class__.SESSION_CLASS.ACTUAL_INSTANCE.database_instance

    @property
    def next_kwargs(self):
        """
        Determines kwargs used to instanciates next class in __call__ method return.
        :return: a dict of next kwargs
        """
        return self.choices[self.decision][0][1]
