# -*- coding: utf8 -*-

import json
import logging
import os

from database_constructor.data_getter import DataGetter
from database_constructor.data_translator import JSONDataToInsertQueryTranslator, FieldTranslator
from database_constructor.database_builder import Database
from pur_beurre.settings import HOST, DATABASE_NAME, SQL_REQUESTS, JSON_DIR_PATH, \
    DATA_GETTER_PARAMETERS, JSON_FILES_PATH

logger = logging.getLogger(__name__)


def main():
    # =============================================================================================
    # DATABASE BUILDER INSTANCE CREATION
    # =============================================================================================
    new_database = Database(host=HOST, database=DATABASE_NAME, sql_requests=SQL_REQUESTS)

    # =============================================================================================
    # DATABASE DELETE
    # =============================================================================================

    new_database.drop_database()

    # =============================================================================================
    # DATABASE CREATION
    # =============================================================================================
    new_database.create_database()
    new_database.execute_sql_requests()

    # =============================================================================================
    # GETTING JSON DATA FROM OPENFOODFACTS WEB API
    # =============================================================================================

    categories = DataGetter(**DATA_GETTER_PARAMETERS['category'])
    categories.write_file()

    products = DataGetter(**DATA_GETTER_PARAMETERS['product'])
    products.write_file()

    # =============================================================================================
    # TRANSLATE DATA TO SQL QUERY
    # =============================================================================================

    # =============================================================================================
    # Insert Categories
    # =============================================================================================

    category_fields_translations = [
        FieldTranslator('id', 'id'), FieldTranslator('name', 'cat_name')]
    category_translator = JSONDataToInsertQueryTranslator(DATABASE_NAME,
                                                          JSON_FILES_PATH['category'],
                                                          category_fields_translations,
                                                          'Category')
    category_insert_query = [category_translator.translate_object_to_sql_query(
        save_query_to_file=True), ]
    new_database.execute_sql_requests(category_insert_query)

    # =============================================================================================
    # Insert Products
    # =============================================================================================

    product_fields_translations = [
        FieldTranslator('code', 'id'),
        FieldTranslator('product_name', 'product_name'),
        FieldTranslator('generic_name', 'description'),
        FieldTranslator('url', 'open_food_facts_url'),
        FieldTranslator('stores', 'first_seller'),
        FieldTranslator('nutrition_grade_fr', 'nutrition_grade_fr')
    ]
    products_translator = JSONDataToInsertQueryTranslator(DATABASE_NAME,
                                                          JSON_FILES_PATH['product'],
                                                          product_fields_translations,
                                                          table_name='Product')

    product_insert_query = [products_translator.translate_object_to_sql_query(), ]
    new_database.execute_sql_requests(product_insert_query)

    # =============================================================================================
    # Insert product categories
    # =============================================================================================

    product_category_links = []
    valid_ids = {
        'Category': [],
        'Product': []
    }

    # =============================================================================================
    # Getting valid ids for Categories and Product
    # =============================================================================================

    for table in valid_ids.keys():
        result = new_database.execute_sql_requests([('select', table, "SELECT id FROM %s" %
                                                     table), ])
        valid_ids[table] = [row[0] for row in result[0]]

    # =============================================================================================
    # Getting category associated to product id
    # =============================================================================================

    products_json_file = os.path.join(JSON_DIR_PATH, 'Product.json')
    with open(products_json_file, 'r') as json_products:
        products_list = json.loads(json_products.read())

    categories_by_product = [(product_dict['code'], product_dict['categories'].split(',')) for
                             product_dict
                             in products_list if 'categories' in product_dict.keys()]
    for product_id, categories in categories_by_product:
        for category in categories:
            if category in valid_ids['Category']:
                logger.info("Added Category %s" % category)
                product_category_links.append({'product_id': product_id, 'category_id': category})
            else:
                logger.info("Unused Category %s" % category)

    # =============================================================================================
    # Creating insert request
    # =============================================================================================

    product_category_fields_translations = [
        FieldTranslator('product_id', 'product_id'),
        FieldTranslator('category_id', 'category_id'),
    ]

    product_category_translator = JSONDataToInsertQueryTranslator(DATABASE_NAME,
                                                                  data_provider=product_category_links,
                                                                  fields_translations=product_category_fields_translations,
                                                                  table_name='Product_category')

    product_category_insert_query = [product_category_translator.translate_object_to_sql_query(), ]

    new_database.execute_sql_requests(product_category_insert_query)


if __name__ == '__main__':
    main()
