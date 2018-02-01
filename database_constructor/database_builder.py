# -*- coding: utf8 -*-
"""
Managers and classes to create a database instance and execute query into this mysql database.
"""
import getpass
import logging

import mysql.connector
from mysql.connector import errorcode

from pur_beurre import settings

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel('INFO')


class ConnectionManager(object):
    """
    Context manager for mysql connection
    """

    def __init__(self, host, user, password, **kwargs):
        self.host = host
        self.user = user
        self.password = password
        if 'database' in kwargs.keys():
            self.database = kwargs['database']
        self.connection = None

    def __enter__(self):
        if hasattr(self, 'database'):
            self.connection = mysql.connector.connect(user=self.user, password=self.password,
                                                      host=self.host, database=self.database)
        else:
            self.connection = mysql.connector.connect(user=self.user, password=self.password,
                                                      host=self.host)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.connection.commit()
        self.connection.close()


class CursorManager(object):
    """
    Context manager for mysql cursor
    """

    def __init__(self, connection, dictionary=False):
        self.connection = connection
        self.dictionary = dictionary
        self.cursor = None

    def __enter__(self):
        self.cursor = self.connection.cursor(dictionary=self.dictionary)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cursor.close()


class Database:
    """
    Database builder class
    """
    connection_manager = ConnectionManager
    cursor_manager = CursorManager

    def __init__(self, host, database, sql_requests: list = None, database_exist=False):
        self.host = host
        self.database = database
        self.sql_requests = sql_requests

        self.user = input(
            'mysql username : ') if settings.MYSQL_USERNAME == '' else settings.MYSQL_USERNAME
        self.password = getpass.getpass() if settings.MYSQL_PASSWORD == '' else settings.MYSQL_PASSWORD

        self.database_created = database_exist

    def get_connection(self):
        """
        get connection to mysql using a context manager with or without database
        :return: a connection context manager instance
        """
        if self.database_created:
            return self.connection_manager(user=self.user, password=self.password,
                                           host=self.host, database=self.database,
                                           test=self.database)
        else:
            try:
                connection = self.connection_manager(user=self.user, password=self.password,
                                                     host=self.host, database=self.database,
                                                     test=self.database)
                self.database_created = True
                return connection
            except mysql.connector.Error as err:
                if err.errno == errorcode.ER_BAD_DB_ERROR:
                    LOGGER.error('ERROR Bad or not existing database: %s', err)
                else:
                    LOGGER.error("ERROR: %s", err)
                LOGGER.warning(
                    "Database %s is not created. Connection without database.", self.database)
            finally:
                return self.connection_manager(user=self.user, password=self.password,
                                               host=self.host)

    def get_cursor(self, connection, dictionary=False):
        """
        create a cursor context manager on provided connection.
        :param connection:
        :return: a cursor context manager instance
        """
        return self.cursor_manager(connection, dictionary)

    def create_database(self):
        """
        Method to create database.
        :return: None
        """

        # open connection with a context manager
        with self.get_connection() as connection_context:
            connection = connection_context.connection
            # create cursor with a context manager
            with self.get_cursor(connection) as cursor_context:
                cursor = cursor_context.cursor
                try:
                    cursor.execute(
                        "CREATE DATABASE {} DEFAULT CHARACTER SET 'utf8'".format(self.database)
                    )
                    self.database_created = True

                except mysql.connector.errors.DatabaseError as err:
                    LOGGER.warning("WARNING Failed creating database: %s", err)
                    self.database_created = True

                except mysql.connector.Error as err:
                    LOGGER.error("ERROR Failed creating database: %s", err)

            try:
                connection.database = self.database
                self.database_created = True
            except mysql.connector.Error as err:
                if err.errno == errorcode.ER_BAD_DB_ERROR:
                    LOGGER.error('ERROR Bad or not existing database : %s', err)
                else:
                    LOGGER.error('ERROR: %s', err)

    def drop_database(self):
        """
        Method to drop database.
        :return: None
        """
        # open connection with a context manager
        with self.get_connection() as cnx_context:
            connection = cnx_context.connection
            # create cursor with a context manager
            with self.get_cursor(connection) as cursor_context:
                cursor = cursor_context.cursor
                try:
                    cursor.execute(
                        "DROP DATABASE {}".format(self.database)
                    )

                    self.database_created = False
                    return cursor

                except mysql.connector.errors.DatabaseError as err:
                    LOGGER.warning("WARNING Failed deleting database: %s", err)

                except mysql.connector.Error as err:
                    LOGGER.error("ERROR Failed creating database: %s", err)

    def execute_sql_requests(self, requests: list = None, **kwargs):
        """
        Execute all requests from instance attribute sql_requests or specific provided requests.
        :return: a list of results
        """
        dictionary = False
        if 'dictionary' in kwargs.keys():
            dictionary = kwargs['dictionary']
        results = []
        sql_requests = requests if requests else self.sql_requests
        # open connection with a context manager
        with self.get_connection() as connection_context:
            connection = connection_context.connection
            # create cursor with a context manager
            with self.get_cursor(connection, dictionary=dictionary) as cursor_context:
                cursor = cursor_context.cursor
                for query in sql_requests:
                    LOGGER.info("Execute query %s %s :%s", query[0], query[1], query[2])
                    try:
                        if query[2]:
                            cursor.execute(query[2])
                            results.append(list(cursor))

                    except mysql.connector.errors.InternalError as err:
                        print(err.msg)
                        if err.msg == 'Unread result found':
                            pass
                        else:
                            raise err
                    except Exception as error:
                        LOGGER.error(error)
        return results
