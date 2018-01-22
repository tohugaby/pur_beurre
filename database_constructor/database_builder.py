# -*- coding: utf8 -*-
import getpass
import logging

import mysql.connector
from mysql.connector import errorcode

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
        self.connection.commit()
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


class Database:
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
                connection = self.connection_manager(user=self.user, password=self.password,
                                                     host=self.host, database=self.database,
                                                     test=self.database)
                self.database_created = True
                return connection
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
                    return cursor

                except mysql.connector.errors.DatabaseError as err:
                    logger.warning("WARNING Failed deleting database: {}".format(err))

                except mysql.connector.Error as err:
                    logger.error("ERROR Failed creating database: {}".format(err))

    def execute_sql_requests(self, requests: list = None):
        """
        Execute all requests from instance attribute sql_requests or specific provided requests
        :return:
        """
        results = []
        sql_requests = requests if requests else self.sql_requests
        # open connection with a context manager
        with self.get_connection() as connection_context:
            connection = connection_context.connection
            # create cursor with a context manager
            with self.get_cursor(connection) as cursor_context:
                cursor = cursor_context.cursor
                for query in sql_requests:
                    logger.info("Execute query %s %s :%s" % (query[0], query[1], query[2]))
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
                    except Exception as e:
                        logger.error(e)
        return results
