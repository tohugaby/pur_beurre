# -*- coding: utf8 -*-
import getpass
import logging

import mysql.connector
from mysql.connector import errorcode

from database_constructor.settings import HOST, DATABASE_NAME, SQL_REQUESTS

logger = logging.getLogger(__name__)
logger.setLevel('INFO')


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

    def __enter__(self):
        if hasattr(self, 'database'):
            self.connection = mysql.connector.connect(user=self.user, password=self.password,
                                                      host=self.host, database=self.database)
        else:
            self.connection = mysql.connector.connect(user=self.user, password=self.password,
                                                      host=self.host)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.connection.close()


class CursorManager(object):
    """
    Context manager for mysql cursor
    """

    def __init__(self, connection):
        self.connection = connection

    def __enter__(self):
        self.cursor = self.connection.cursor()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cursor.close()


class DatabaseBuilder:
    """
    Database builder class
    """
    connection_manager = ConnectionManager
    cursor_manager = CursorManager

    def __init__(self, host, database, sql_requests: dict):
        self.host = host
        self.database = database
        self.sql_requests = sql_requests
        self.user = input('mysql username : ')
        self.password = getpass.getpass()
        self.database_created = False

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
                return self.connection_manager(user=self.user, password=self.password,
                                               host=self.host, database=self.database,
                                               test=self.database)
                self.database_created = True
            except mysql.connector.Error as err:
                if err.errno == errorcode.ER_BAD_DB_ERROR:
                    logger.error('ERROR Bad or not existing database :%s')
                else:
                    logger.error('ERROR:%s' % err)
                logger.warning(
                    "Database %s is not created. Connection without database." % self.database)
            finally:
                return self.connection_manager(user=self.user, password=self.password,
                                               host=self.host)

    def get_cursor(self, connection):
        """
        create a cursor context manager on provided connection.
        :param connection:
        :return: a cursor context manager instance
        """
        return self.cursor_manager(connection)

    def create_database(self):
        """Method to create database"""

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
                    logger.warning("WARNING Failed creating database: {}".format(err))
                    self.database_created = True

                except mysql.connector.Error as err:
                    logger.error("ERROR Failed creating database: {}".format(err))

            try:
                connection.database = self.database
                self.database_created = True
            except mysql.connector.Error as err:
                if err.errno == errorcode.ER_BAD_DB_ERROR:
                    logger.error('ERROR Bad or not existing database :%s')
                else:
                    logger.error('ERROR:%s' % err)

    def drop_database(self):
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

                except mysql.connector.errors.DatabaseError as err:
                    logger.warning("WARNING Failed deleting database: {}".format(err))

                except mysql.connector.Error as err:
                    logger.error("ERROR Failed creating database: {}".format(err))

    def load_requests_list(self):
        """
        make a list of tuple from sql_requests_dict
        :return:
        """
        return NotImplemented

    # TODO: to rewrite to take one or several request. Make it enougth generic to be used in
    # other methods (like create database or drop database)
    def execute_sql_requests(self, requests_dict: dict = None):
        """
        Execute all requests from instance attribute sql_requests or specific provided requests
        :return:
        """

        # open connection with a context manager
        with self.get_connection() as connection_context:
            connection = connection_context.connection
            # create cursor with a context manager
            with self.get_cursor(connection) as cursor_context:
                cursor = cursor_context.cursor
                for query_type, queries in self.sql_requests.items():
                    for query in queries:
                        logger.info("Execute query %s %s :%s" % (query_type, query[0], query[1]))
                        try:
                            if query:
                                cursor.execute(query[1])
                                for res in cursor:
                                    print(res)

                        except mysql.connector.errors.InternalError as err:
                            print(err.msg)
                            if err.msg == 'Unread result found':
                                pass
                            else:
                                raise err
                        except Exception as e:
                            logger.error(e)


new_database = DatabaseBuilder(host=HOST, database=DATABASE_NAME, sql_requests=SQL_REQUESTS)
new_database.create_database()
new_database.execute_sql_requests()
#new_database.drop_database()
