import sys

from core.sessions import Session


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
        if not self.base_call_process():
            return self.__class__.SESSION_CLASS.ACTUAL_INSTANCE.previous_menu()
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
        if self.decision == 'q':
            print('Exiting program')
            sys.exit(0)
        if self.decision == 'p':
            print('going to previous menu')
            return False
        self.update_session()
        return True

    def print_choices(self):
        """Print explanation text and possible choices """
        print(self.text)
        for choice in self.choices:
            print(choice[0])

    def collect_choice(self):
        """ collect inputed user choice"""
        self.decision = None
        possible_choice = list(range(len(self.choices))) + ['q']
        if self.__class__.SESSION_CLASS.ACTUAL_INSTANCE.previous_menu is not None:
            possible_choice.append('p')
        while self.decision not in possible_choice:
            decision = input("Votre choix :")
            try:
                self.decision = int(decision) - 1
            except ValueError as e:
                print(self.decision)
                self.decision = decision

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