import getpass
import mysql.connector
from mysql.connector import errorcode

import logging

logger = logging.getLogger(__name__)

HOST = '127.0.0.1'
DB_NAME = 'purbeurre'
SQL_REQUESTS = {
    'tables': {
        'users': """SELECT 'youpi'""",
        'categories': """SELECT 1""",
        'products': "",
        "product_category": "",
        "favorites": ""
    },
    'constraints': {},
    'indexes': {}

}


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
            self.cnx = mysql.connector.connect(user=self.user, password=self.password,
                                               host=self.host, database=self.database)
        else:
            self.cnx = mysql.connector.connect(user=self.user, password=self.password,
                                               host=self.host)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cnx.close()


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
        self.db_created = False

    def get_connection(self):
        """
        get connection to mysql using a context manager with or without database
        :return: a connection context manager instance
        """
        if self.db_created:
            print(self)
            return self.connection_manager(user=self.user, password=self.password,
                                           host=self.host, database=self.database,
                                           test=self.database)
        else:
            logger.warning(
                "Database %s is not created. Connection without database." % self.database)
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
        with self.get_connection() as cnx_context:
            cnx = cnx_context.cnx
            # create cursor with a context manager
            with self.get_cursor(cnx) as cursor_context:
                cursor = cursor_context.cursor
                try:
                    cursor.execute(
                        "CREATE DATABASE {} DEFAULT CHARACTER SET 'utf8'".format(DB_NAME)
                    )
                    self.db_created = True

                except mysql.connector.errors.DatabaseError as err:
                    logger.warning("WARNING Failed creating database: {}".format(err))
                    self.db_created = True

                except mysql.connector.Error as err:
                    logger.error("ERROR Failed creating database: {}".format(err))

            try:
                cnx.database = DB_NAME
                self.db_created = True
            except mysql.connector.Error as err:
                if err.errno == errorcode.ER_BAD_DB_ERROR:
                    logger.error('ERROR Bad or not existing database :%s')
                else:
                    logger.error('ERROR:%s' % err)

    def load_requests_list(self):
        """
        make a list of tuple from sql_requests_dict
        :return:
        """
        return NotImplemented


    # TODO: to rewrite . Should requests parameter be a list of tuple or a dict?
    def execute_sql_requests(self, requests_dict: dict = None):
        """
        Execute all requests from instance attribute sql_requests or specific provided requests
        :return:
        """

        # open connection with a context manager
        with self.get_connection() as cnx_context:
            cnx = cnx_context.cnx
            # create cursor with a context manager
            with self.get_cursor(cnx) as cursor_context:
                cursor = cursor_context.cursor
                for query_type, sql_queries in self.sql_requests.items():
                    for query_name, query in sql_queries.items():
                        print(query)
                        try:
                            if query:
                                cursor.execute(query)
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


new_database = DatabaseBuilder(host=HOST, database=DB_NAME, sql_requests=SQL_REQUESTS)
new_database.create_database()
new_database.execute_sql_requests()

