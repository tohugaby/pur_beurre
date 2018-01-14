# -*- coding: utf8 -*-
import json


class FieldTranslator:
    """
    A class to translate a source field name to sql field name
    """

    def __init__(self, source_field_name, sql_field_name):
        self.source_field_name = source_field_name
        self.sql_field_name = sql_field_name


class BaseDataToInsertQueryTranslator:
    """
    A base class to translate data from a text file to sql insert requests
    """
    field_translation_class = FieldTranslator

    def __init__(self, database_name, file_path, fields_translations: list, table_name=None):
        """

        :param database_name: a database_name
        :param file_path: a path to file containing data to translate
        :param table_name: the name of the table concerned by insert query.
        :param fields_translations: a list of FieldTranslator class instance
        """
        self.database = database_name
        self.file = file_path
        self.table = table_name
        self.fields_translations = fields_translations

    def filtered_values(self):
        """
        remove useless keys,values from data_dict
        :return:
        """
        filtered_value = []
        for row in self.translate_data_to_object():
            filtered_value.append({field: value for (field, value) in row.items() if field in
                                   self.ordered_sql_fields_names[0]})
        return filtered_value

    def translate_data_to_object(self):
        """
        create an object from provided data structure
        :return: an object
        """
        return NotImplemented

    def translate_object_to_sql_query(self):
        """
        create an insert sql query from provided object
        :return: a string containing sql query
        """

        #TODO: rewrite sql query with %s syntax and pass parameter to
        sql_query = "INSERT INTO {} ( ".format(self.table)
        filtered_values = self.filtered_values()

        sql_query += ' , '.join(self.ordered_sql_fields_names[1]) + ") VALUES "

        for new_row in filtered_values:
            sql_query += "("
            for i in range(len(self.fields_translations)):

                sql_query += "'{}'".format(new_row[self.ordered_sql_fields_names[0][i]].replace(
                    "'", " "))
                if i < len(self.fields_translations) - 1:
                    sql_query += ","
            sql_query += ")"
            # uncomment to test on one line
            # break
            if not new_row == filtered_values[-1]:
                sql_query += ","

        return sql_query

    @property
    def file_reader(self):
        """
        open the file with appropriate python lib
        :return: an file context manager
        """
        return open(self.file, 'r')

    @property
    def ordered_sql_fields_names(self):
        """
        from list of fields_translates get an ordered list of sql field names
        :return: a list of tuple
        """

        fields_translations_list = [
            (field_translation.source_field_name, field_translation.sql_field_name)
            for field_translation in self.fields_translations]
        zipped_fields_translations_list = zip(*fields_translations_list)

        return list(zipped_fields_translations_list)


class JSONDataToInsertQueryTranslator(BaseDataToInsertQueryTranslator):
    """
        A class to translate data from JSON file to sql insert requests
    """

    def translate_data_to_object(self):
        """
        create an object from provided data structure
        :return: an object
        """
        with self.file_reader as readed_file:
            json_dict = json.loads(readed_file.read())
        return json_dict
