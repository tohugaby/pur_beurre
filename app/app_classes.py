from app.core import ChoiceMenu, SqlChoiceMenu, SqlData


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


class BaseProduct(SqlData):
    """
    Base
    """

    def __call__(self, *args, **kwargs):
        print(self)

    def __str__(self):
        return self.show_product(**self.data)

    def show_product(self, **data):
        product_card = """
        code: {id}    nom: {product_name}
        categories: {categories}  
        note nutritionnelle: {nutrition_grade_fr} 
        description: {description}
        magasin: {first_seller}
        url: {open_food_facts_url}
        """.format(**data)

        return product_card

    @property
    def data(self):
        query = [
            ("select",
             "Product",
             """
            SELECT 
            DISTINCT P.id,P.product_name,P.description,P.nutrition_grade_fr,P.first_seller,
            P.open_food_facts_url , GROUP_CONCAT(DISTINCT(C.cat_name) ORDER BY cat_name SEPARATOR ' | ') as 
            categories
            FROM Product P
            INNER JOIN Product_category Pc ON P.id = Pc.product_id
            INNER JOIN Category C ON Pc.category_id = C.id
            WHERE P.id='%s'""" % self.primary_key), ]

        return self.database.execute_sql_requests(query, dictionary=True)[0][0]


class Product(BaseProduct):
    """
    Represent a product
    """

    def __call__(self, *args, **kwargs):
        print(self)
        self.print_substitute()
        self.save_to_favorites(self.get_best_substitute()['id'])

    def category_name(self):
        query = [
            (
                'select',
                'Category',
                """SELECT cat_name FROM Category WHERE id='%s'""" % self.kwargs['category_id']
            ),
        ]
        return self.database.execute_sql_requests(query, dictionary=True)[0][0]

    def get_best_substitute(self):
        query_str = """
                 SELECT 
                 DISTINCT P.id,P.product_name,P.description,P.nutrition_grade_fr,P.first_seller,
                 P.open_food_facts_url , 
                 GROUP_CONCAT(DISTINCT(C.cat_name) ORDER BY cat_name SEPARATOR ' | ') AS categories
                 FROM Product P
                 INNER JOIN Product_category Pc ON P.id = Pc.product_id
                 INNER JOIN Category C ON Pc.category_id = C.id
                 WHERE P.id<>'%s' 
                 AND C.id='%s' 
                 AND P.nutrition_grade_fr < '%s' 
                 AND P.nutrition_grade_fr <> '%s'
 """

        query = [('select',
                  'Product',
                  query_str % (
                      self.primary_key,
                      self.kwargs['category_id'],
                      self.data['nutrition_grade_fr'],
                      self.data['nutrition_grade_fr'])),
                 ]

        return self.database.execute_sql_requests(query, dictionary=True)[0][0]

    def print_substitute(self):
        data = {'substitute': self.show_product(**self.get_best_substitute()),
                **self.category_name()}
        print("""
        Meilleur produit de remplacement trouvé dans la catégorie {cat_name}
        {substitute}
        """.format(**data))

    def save_to_favorites(self, product_id):
        """
        Save substitute product in provided user favorites
        :param user_id: user primary key value in User table
        :param product_id: product primary key in Product table
        :return: favorite id
        """
        user_id = self.__class__.SESSION_CLASS.ACTUAL_INSTANCE.user.id
        choice = str()
        while choice not in ("y", "n"):
            choice = input(
                "Voulez-vous sauvegarder ce produit de remplacement dans vos favoris?[y/n]")
        if choice == "y":
            query = [
                (
                    'insert',
                    'Favorites',
                    """
                    INSERT INTO Favorite(user_id, product_id) VALUES ('%s','%s')
                    """ % (user_id, product_id)
                ),
            ]
            self.database.execute_sql_requests(query)
        else:
            return
