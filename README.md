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
This part use mysql-connector-python lib in a procedural script to: 
  - create connection to mysql,
  - create database,
  - create table,
  - create indexes and constraints
  
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


