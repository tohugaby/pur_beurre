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
    prod.page_getter_limit = 1
    prod.write_file()

    # =================================================================================================
    # TRANSLATE DATA TO SQL QUERY
    # =================================================================================================
    # Insert Categories
    categories_json_file = os.path.join(JSON_DIR_PATH, 'Category.json')
    category_fields_translations = [
        FieldTranslator('id', 'id'), FieldTranslator('name', 'cat_name')]
    category_sql_insert_query = JSONDataToInsertQueryTranslator(DATABASE_NAME,
                                                                categories_json_file,
                                                                category_fields_translations,
                                                                'Category')
    category_insert_query = [
        ('insert', 'Category', category_sql_insert_query.translate_object_to_sql_query()), ]
    new_database.execute_sql_requests(category_insert_query)

    # Insert Products
    products_json_file = os.path.join(JSON_DIR_PATH, 'Product.json')
    product_fields_translations = [
        FieldTranslator('code', 'open_food_facts_id'),
        FieldTranslator('product_name', 'product_name'),
        FieldTranslator('generic_name', 'description'),
        FieldTranslator('url', 'open_food_facts_link'),
        FieldTranslator('stores', 'first_seller'),
        FieldTranslator('nutrition_grade_fr', 'nutrition_grade_fr')
    ]
    products_sql_insert_query = JSONDataToInsertQueryTranslator(DATABASE_NAME, products_json_file,
                                                                product_fields_translations,
                                                                table_name='Product')

    product_insert_query = [(
        'insert', 'Product', products_sql_insert_query.translate_object_to_sql_query()), ]
    new_database.execute_sql_requests(product_insert_query)

    # =================================================================================================
    # DATABASE DELETE
    # =================================================================================================

    # new_database.drop_database()


if __name__ == '__main__':
    main()
