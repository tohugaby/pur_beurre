from app.sql_objects import BaseProduct, Product
from core.menus import ChoiceMenu, SqlChoiceMenu


class ActivityChoiceMenu(ChoiceMenu):
    """
    First Menu to choose between finding a product substitute or a ask for a favorite
    """

    def get_text(self):
        return 'Choisissez une action (or q for quit) : '

    def get_choices(self):
        first_menu_choices = [
            ("1 - Remplacer un aliment.", CategoryChoiceMenu),
            ("2 - Retrouver mes aliments substitués.", FavoriteChoiceMenu),
        ]
        return first_menu_choices


class CategoryChoiceMenu(SqlChoiceMenu):
    """
    Menu which proposes choices within categories
    """
    query = """SELECT PC.category_id, C.cat_name FROM Product_category PC 
INNER JOIN Category C ON PC.category_id = C.id
INNER JOIN Product P ON PC.product_id = P.id  
WHERE PC.category_id = C.id AND P.nutrition_grade_fr<>''
GROUP BY PC.category_id, C.cat_name HAVING count(*)> 15"""

    def get_text(self):
        return "Choisissez une catégorie (or q for quit/ p for previous choice menu) : "

    def print_choices(self):
        print(self.text)
        for choice in self.choices:
            print(choice[0][0], choice[0][1]['cat_name'])

    def get_next_class(self):
        return ProductChoiceMenu


class ProductChoiceMenu(SqlChoiceMenu):
    """
    Menu which proposes choices within product attached to provided category
    """
    query = """SELECT * FROM Product_category PC 
INNER JOIN Product P ON PC.product_id = P.id 
WHERE PC.category_id='%s' AND P.nutrition_grade_fr<>''"""
    query_parameters = ['category_id', ]

    def get_text(self):
        return "Choisissez un produit (or q for quit/ p for previous choice menu) : "

    def print_choices(self):
        print(self.text)
        for choice in self.choices:
            print(choice[0][0], choice[0][1]['product_name'])

    def get_next_class(self):
        return Product

    @property
    def next_kwargs(self):
        next_kwargs = dict()
        next_kwargs['database_instance'] = self.database
        next_kwargs['table'] = 'Product'
        next_kwargs['primary_key'] = self.choices[self.decision][0][1]['id']
        next_kwargs['category_id'] = self.choices[self.decision][0][1]['category_id']
        return next_kwargs


class FavoriteChoiceMenu(SqlChoiceMenu):
    """
    Menu which proposes choices within user favorites
    """
    query = """SELECT * FROM Favorite F 
INNER JOIN Product P ON F.product_id = P.id 
WHERE F.user_id='%s'"""
    query_parameters = ['user_id', ]

    def __init__(self, text='', choices: list = list(), **kwargs):
        """
        :param text: description of action
        :param choices: a list of tuple with text description and linked Class nam
        """
        # self.kwargs must be define before self.choices because it calls self.get_choices
        # method which uses self.kwargs
        kwargs['user_id'] = self.__class__.SESSION_CLASS.ACTUAL_INSTANCE.user.id
        super(FavoriteChoiceMenu, self).__init__(text=text, choices=choices, **kwargs)

    def get_text(self):
        return "Choisissez un favori : "

    def print_choices(self):
        print(self.text)
        for choice in self.choices:
            print(choice[0][0], choice[0][1]['product_name'])

    def get_next_class(self):
        return BaseProduct

    @property
    def next_kwargs(self):
        next_kwargs = dict()
        next_kwargs['database_instance'] = self.database
        next_kwargs['table'] = 'Product'
        next_kwargs['primary_key'] = self.choices[self.decision][0][1]['product_id']
        return next_kwargs