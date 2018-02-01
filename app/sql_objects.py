# -*- coding: utf8 -*-
"""
Describe classes representing pur_beurre database objects
"""
from core.sql_objects import SqlData


class BaseProduct(SqlData):
    """
    A base product.
    """

    def __call__(self, *args, **kwargs):
        print(self)

    def __str__(self):
        return self.show_product(**self.data)

    @staticmethod
    def show_product(**data):
        """
        Generate a product presentation text.
        :param data: data used to fill product presentation text
        :return: a product presentation text
        """
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
        """
        Constructs and launch query to get product data
        :return: a dict of product data
        """
        query = [
            ("select", "Product", """
SELECT DISTINCT P.id,P.product_name,P.description,P.nutrition_grade_fr,P.first_seller,P.open_food_facts_url,
GROUP_CONCAT(DISTINCT(C.cat_name) ORDER BY cat_name SEPARATOR ' | ') as categories 
FROM Product P 
INNER JOIN Product_category Pc ON P.id = Pc.product_id 
INNER JOIN Category C ON Pc.category_id = C.id 
WHERE P.id='%s'""" % self.primary_key), ]

        return self.database.execute_sql_requests(query, dictionary=True)[0][0]


class Product(BaseProduct):
    """
    Represent a product and allow to get its best substitute.
    """

    def __call__(self, *args, **kwargs):
        print(self)
        self.print_substitute()
        self.save_to_favorites(self.get_best_substitute()['id'])

    def category_name(self):
        """
        Get the category name with provided category_id in kwargs.
        :return: a dictionary containing category name
        """
        query = [
            (
                'select',
                'Category',
                """SELECT cat_name FROM Category WHERE id='%s'""" % self.kwargs['category_id']
            ),
        ]
        return self.database.execute_sql_requests(query, dictionary=True)[0][0]

    def get_best_substitute(self):
        """
        Get the best substitute of a product. Choice is based on nutrition_grade_fr field.
        :return: Substitue as a dictionnary
        """
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

        query = [
            ('select',
             'Product',
             query_str % (
                 self.primary_key,
                 self.kwargs['category_id'],
                 self.data['nutrition_grade_fr'],
                 self.data['nutrition_grade_fr'])),
        ]

        return self.database.execute_sql_requests(query, dictionary=True)[0][0]

    def print_substitute(self):
        """
        Print substitute description text
        :return:
        """
        data = {'substitute': self.show_product(**self.get_best_substitute()),
                **self.category_name()}
        print("""
        Meilleur produit de remplacement trouvé dans la catégorie {cat_name}
        {substitute}
        """.format(**data))

    def save_to_favorites(self, product_id):
        """
        Save substitute product in provided user favorites;
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
