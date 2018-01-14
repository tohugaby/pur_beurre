import json
import os

from database_constructor.data_translator import JSONDataToInsertQueryTranslator, FieldTranslator
from database_constructor.database_builder import DatabaseBuilder
from database_constructor.openfoodfacts_data_getter import CategoryDataGetter, ProductDataGetter
from pur_beurre.settings import HOST, DATABASE_NAME, SQL_REQUESTS, JSON_DIR_PATH


def main():
    # =================================================================================================
    # DATABASE CREATION
    # =================================================================================================
    new_database = DatabaseBuilder(host=HOST, database=DATABASE_NAME, sql_requests=SQL_REQUESTS)
    new_database.create_database()
    new_database.execute_sql_requests()

    # =================================================================================================
    # GETTING JSON DATA FROM OPENFOODFACTS WEB API
    # =================================================================================================

    cat = CategoryDataGetter()
    cat.write_file()

    prod = ProductDataGetter()
    # prod.page_getter_limit = 10
    prod.write_file()

    # =================================================================================================
    # TEST JSON DATA
    # =================================================================================================

    # json_file = os.path.join(JSON_DIR_PATH,'Product.json')
    #
    # with open(json_file, 'r') as file:
    #     json_list = json.loads(file.read())
    #     print(len(json_list))
    #     for key in json_list[0].keys():
    #         print(key)
    #
    #     new_list = [dict(code=product['code'], product_name=product['product_name']) for
    #                 product in json_list]
    #     print(new_list[:3])

    # =================================================================================================
    # TRANSLATE DATA TO SQL QUERY
    # =================================================================================================
    json_file = os.path.join(JSON_DIR_PATH, 'Category.json')

    category_fields_translations = (FieldTranslator('id', 'id'), FieldTranslator('name',
                                                                                 'cat_name'))

    sql_insert_query = JSONDataToInsertQueryTranslator(DATABASE_NAME, json_file,
                                                       category_fields_translations, 'Category')

    category_insert_query = [
        ('insert', 'Category', sql_insert_query.translate_object_to_sql_query()), ]

    new_database.execute_sql_requests(category_insert_query)

    # =================================================================================================
    # DATABASE DELETE
    # =================================================================================================

    # new_database.drop_database()


if __name__ == '__main__':
    main()
