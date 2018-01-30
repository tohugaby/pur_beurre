# PUR_BEURRE

Supported versions of python: **3.4, 3.5, 3.6**


## What is Pur Beurre ?

Openclassrooms project 5: Use Open Food Facts database to substitute food products with an 
healthier one.


## Getting starded

**Pipenv** is used to manage dependencies and virtual environment. 
You need to install pipenv on your system.

```
pip install pipenv
```
In project directory run following command to create virtual environment install dependencies:

```
pipenv install
```

### Mysql/Mariadb tips

If there are a lot of data to insert check this in  mysql CLI:

```mysql
show variables like 'max_allowed_packet';
```
If result is something like 1048576 bytes (1MB), you can increase it to 524288000 in my.cnf file or with mysql command:
 
 
```mysql
SET GLOBAL max_allowed_packet=524288000;
```

### Writing the settings file

You can copy settings sample to create your own settings file.

#### Path settings

```python
import os

#=============================================================================================
# PATH PARAMETERS
#=============================================================================================
ROOT_DIR_PATH = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
JSON_DIR_NAME = 'json_files'
JSON_DIR_PATH = os.path.join(ROOT_DIR_PATH, JSON_DIR_NAME)
```

#### Mysql requests

```python
#=============================================================================================
# MYSQL REQUESTS
#=============================================================================================
user = """
CREATE TABLE IF NOT EXISTS User (
  id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  username VARCHAR(255)  NOT NULL UNIQUE,
  password VARCHAR(255)  NOT NULL
  )
  ENGINE=InnoDB
"""
#...
```

#### Databse settings

```python
#=============================================================================================
# DATABASE PARAMETERS
#=============================================================================================
HOST = '127.0.0.1'
mysql_username = ''
mysql_password = ''
try:
    from pur_beurre.mysql_auth_info import USER, PASSWORD

    mysql_username = USER
    mysql_password = PASSWORD
except ImportError as e:
    pass
except ModuleNotFoundError as e:
    pass
except Exception as e:
    raise e

DATABASE_NAME = 'purbeurre'
SQL_REQUESTS = [
    ('table', 'user', user),
    #...
    ('constraint', None, None),
    ('index', None, None)
]
```

#### DataGetters settings

```python
#=============================================================================================
# DATAGETTERS PARAMETERS
#=============================================================================================
DATA_GETTER_PARAMETERS = {
    'product': {
        'root_url': 'https://fr.openfoodfacts.org/lieu-de-vente/france/lieu-de-fabrication/france.json',
        'first_page': 1,
        'paginated_data': True,
        'page_getter_limit': 0,
        'json_data_key': 'products',
        'filename': 'Product.json',
    },
    'category': {
        'root_url': 'https://fr.openfoodfacts.org/categories.json',
        'first_page': 1,
        'paginated_data': False,
        'page_getter_limit': 0,
        'json_data_key': 'tags',
        'filename': 'Category.json'
    }
}

JSON_FILES_PATH = {
    'category': os.path.join(JSON_DIR_PATH, 'Category.json'),
    'product': os.path.join(JSON_DIR_PATH, 'Product.json')
}
```


### Creating Database
#### SQL script to create local database

This part use **mysql-connector-python** lib in **Database** class.
 Following action are made in a procedural script using **Database** instance methods: 
  - get connection to mysql:
  - create database,
  - create table,
  - create indexes and constraints


Usage:

```python
from database_constructor.database_builder import Database
HOST = '127.0.0.1'
DATABASE_NAME = 'purbeurre'
SQL_REQUESTS = [
    ('table', 'user', """
    CREATE TABLE IF NOT EXISTS User (
  id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  username VARCHAR(255)  NOT NULL UNIQUE,
  password VARCHAR(255)  NOT NULL
  )
  ENGINE=InnoDB
    """),
    ('constraint', None, None),
    ('index', None, None)
]

new_database = Database(host=HOST, database=DATABASE_NAME, sql_requests=SQL_REQUESTS) 
# create database using database name from instance attribute
new_database.create_database()
# launch all the request from instance
new_database.execute_sql_requests()
```
  
 For connection initialization you need a mysql username and password. 
 Used mysql user need sufficient privileges to create database.
 Password is not echoed.

 
#### Getting data from OpenFoodFacts API

Collection of data from OpenFoodFacts API is based on **DataGetter** instances.
Using write_file method create a json file of the received data.

Usage:
```python
from database_constructor.data_getter import DataGetter
category = {
        'root_url': 'https://fr.openfoodfacts.org/categories.json',
        'first_page': 1,
        'paginated_data': False,
        'page_getter_limit': 0,
        'json_data_key': 'tags',
        'filename': 'Category.json'
    }
    
categories = DataGetter(**category)
categories.write_file()
```
You can create a 'mysql_auth_info' module to store user and password to access database import 
USER, PASSWORD


#### Data integration script

Data integration uses **FieldTranslator** to illustrate correspondence between a json value id and 
table field label.

```python
from database_constructor.data_translator import  FieldTranslator

category_fields_translations = [FieldTranslator('id', 'id'), FieldTranslator('name', 'cat_name')]
```


**JSONDataToInsertQueryTranslator** inherited from **BaseDataToInsertQueryTranslator** translate json 
data to an sql insert query thanks to its **translate_object_to_sql_query** method.

```python
from database_constructor.data_translator import JSONDataToInsertQueryTranslator, FieldTranslator

category_fields_translations = [FieldTranslator('id', 'id'), FieldTranslator('name', 'cat_name')]
category_translator = JSONDataToInsertQueryTranslator('purbeurre',
                                                          'json_file/category.json',
                                                          category_fields_translations,
                                                          'Category')
```

Last step to integrate data in database is to use 


```python
from database_constructor.database_builder import Database
from database_constructor.data_translator import JSONDataToInsertQueryTranslator, FieldTranslator


new_database = Database(host='127.0.0.1', database='purbeurre', sql_requests='') 

category_fields_translations = [FieldTranslator('id', 'id'), FieldTranslator('name', 'cat_name')]
category_translator = JSONDataToInsertQueryTranslator('purbeurre',
                                                          'json_file/category.json',
                                                          category_fields_translations,
                                                          'Category')

category_insert_query = [('insert', 'Category', category_translator.translate_object_to_sql_query()),]
new_database.execute_sql_requests(category_insert_query)
```

### User creation script

To register a new app user in database, you can use 'create_user.py' script.


## Launching the program

To launch the program use following command in pur_beurre directory:
```shell
python scripts/launcher.py
```

## Modules and Classes description
### Authentication

To store user authentication information during application use, **core.authentication** module 
provide **User** class. You can instantiate it with database username and password which will be 
checked in database.

```python
from core.authenthication import User

user = User('your username', 'your password')
```


### Sessions

**Session** instance is used as a context manager which store : **Database** instance, **User** instance
 and first and previous ChoiceMenu instances in **Session** actual instance.
 
```python
from core.authenthication import User
from core.sessions import Session

with Session(user=User('your username', 'your password')) as new_session:
    # your code here
    pass
```


### Menus

**ChoiceMenu** base class and child classes have a **\_\_call\_\_** method which return next class 
instantiated with needed kwargs.
Inherited classes can override methods:
- **get_text** : to define explanation text printed before list of choices
- **get_choice** : to define the way to get list of choices
- **print_choices** : to define the way to print choices
- **get_next_class** : to define class used by \_\_call\_\_ to return instance of
- **next_kwargs** :  to define kwargs needed by "next class" \_\_init\_\_ method.

It has also a class attribute **SESSION_CLASS** used to update session status (previous and first 
menu instances) during instance call

**SqlChoiceMenu** class (and its childs) inherited from **ChoiceMenu** has extra attributes and methods.
**query** and **query_parameters** attributes used by **get_query** method (to get a list of choices).
Property **database** is used to get database to work with.


### SQL objects

Legacy **SqlData** class only contains \_\_init\_\_ method and \_\_str\_\_ method. It has 
database, table, primary_key, kwargs attributes to identify sql element in database.

**BaseProduct** and **Product** class are inherited from **SqlData** class. They implements new 
methods to print product data and its substitute (only **Product** instances).
Product class allows to save a substitute in user favorites.



