# -*- coding: utf8 -*-

import getpass
import logging

from database_constructor.database_builder import Database
from pur_beurre.settings import HOST, DATABASE_NAME

logger = logging.getLogger(__name__)


def main():
    user = input("nom du nouvel utilisateur")
    passwd = getpass.getpass()
    query = """INSERT INTO User (username,password) VALUES ('%s','%s')""" % (user, passwd)
    database = Database(host=HOST, database=DATABASE_NAME, database_exist=True)
    database.execute_sql_requests([('insert', 'User', query),])

if __name__ == '__main__':
    main()