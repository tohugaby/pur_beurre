# -*- coding: utf8 -*-
"""
A way to get default database
"""
from database_constructor.database_builder import Database
from pur_beurre.settings import HOST, DATABASE_NAME

DEFAULT_DATABASE = Database(host=HOST, database=DATABASE_NAME, database_exist=True)
