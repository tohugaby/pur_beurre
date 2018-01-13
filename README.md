# PUR_BEURRE

Supported versions of python: 3.4, 3.5, 3.6

## What is Pur Beurre ?
Openclassrooms project 5: Use Open Food Facts database to substitute food products with an 
healthier one.

## Getting starded

Pipenv is used to manage dependencies and virtual environment. 
You need to install pipenv on your system.

```
pip install pipenv
```

## Features

### Creating Database
#### SQL script to create local database
This part use mysql-connector-python lib in DatabaseBuilder class.
 Following action are made in a procedural script using DatabaseBuilder instance methods: 
  - get connection to mysql:
  - create database,
  - create table,
  - create indexes and constraints
  
  ```python
from database_constructor.builder import DatabaseBuilder
HOST = '127.0.0.1'
DATABASE_NAME = 'purbeurre'
SQL_REQUESTS = {
    'tables': [
        ('user',"""SELECT 1"""),
        ('category', """SELECT 2"""),
    ],
    'constraints': [
        ('constraint_1',"""SELECT 'test constraints'""")
        ]   
}
HOST
new_database = DatabaseBuilder(host=HOST, database=DATABASE_NAME, sql_requests=SQL_REQUESTS) 
# just test connection getter
new_database.get_connection()
# create database using database name from instance attribute
new_database.create_database()
# lauch all the request from instance
new_database.execute_sql_requests()

```
  
 For connection initialization you need a mysql username and password. 
 Used mysql user need sufficient privileges to create database.
 Password is not echoed.
 
#### Getting data from OpenFood Facts API
#### Data integration script

### User management

#### User table in database
#### Authentication module
#### Authentication interface

### Product substitution

#### Categories getter
#### Product getter
#### Substitute View

### Favorites management

#### Favorites setter
#### Favorites getter


