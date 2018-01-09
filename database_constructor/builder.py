import getpass
import mysql.connector
from mysql.connector import errorcode

import logging

logger = logging.getLogger(__name__)

user = input('mysql username : ')
password = getpass.getpass()
host = '127.0.0.1'

DB_NAME = 'purbeurre'

TABLES = {
    'users': "",
    'categories': "",
    'products': "",
    "product_category": "",
    "favorites": ""
}


def create_database(cursor):
    """Method to create database"""
    try:
        cursor.execute(
            "CREATE DATABASE {} DEFAULT CHARACTER SET 'utf8'".format(DB_NAME)
        )
    except mysql.connector.Error as err:
        logger.error("ERROR Failed creating database: {}".format(err))


cnx = mysql.connector.connect(user=user, password=password, host=host)

cursor = cnx.cursor()
try:
    cnx.database = DB_NAME
except mysql.connector.Error as err:
    if err.errno == errorcode.ER_BAD_DB_ERROR:
        create_database(cursor)
        cnx.database = DB_NAME
    else:
        logger.error('ERROR:%s' % err)

# select = """SELECT * FROM Animal"""
#
# cursor.execute(select)
#
# for res in cursor:
#     print(res)

# cursor.close()

cnx.close()
