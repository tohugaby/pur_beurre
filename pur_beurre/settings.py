# -*- coding: utf8 -*-
import os

ROOT_DIR_PATH = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
JSON_DIR_NAME = 'json_files'
JSON_DIR_PATH = os.path.join(ROOT_DIR_PATH, JSON_DIR_NAME)

# MYSQL REQUESTS
user = """
CREATE TABLE IF NOT EXISTS User (
  id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  username VARCHAR(255)  NOT NULL UNIQUE,
  password VARCHAR(255)  NOT NULL
  )
  ENGINE=InnoDB
"""

category = """
CREATE TABLE IF NOT EXISTS Category (
  id VARCHAR(255) NOT NULL PRIMARY KEY,
  cat_name VARCHAR(255) NOT NULL UNIQUE
  )
  ENGINE=InnoDB
"""

product = """
CREATE TABLE IF NOT EXISTS Product (
  id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  open_food_facts_id BIGINT UNSIGNED UNIQUE,
  product_name VARCHAR(255) NOT NULL,
  description TEXT,
  open_food_facts_link VARCHAR(255),
  first_seller VARCHAR(255),
  nutrition_grade_fr CHAR(1) NOT NULL)
  ENGINE=InnoDB
"""

product_category = """
CREATE TABLE IF NOT EXISTS Product_category (
  product_id BIGINT UNSIGNED NOT NULL,
  category_id VARCHAR(255) NOT NULL,
  CONSTRAINT pk_product_category PRIMARY KEY (product_id, category_id),
  CONSTRAINT fk_product_id FOREIGN KEY (product_id) REFERENCES Product(id),
  CONSTRAINT fk_category_id FOREIGN KEY (category_id) REFERENCES Category(id)
  )
  ENGINE=InnoDB
"""

favorite = """
CREATE TABLE IF NOT EXISTS Favorite (
  product_id BIGINT UNSIGNED NOT NULL,
  user_id INT  UNSIGNED NOT NULL,
  CONSTRAINT pk_favorite PRIMARY KEY (product_id, user_id),
  CONSTRAINT fk_favorite_product_id FOREIGN KEY (product_id) REFERENCES Product(id),
  CONSTRAINT fk_favorite_user_id FOREIGN KEY (user_id) REFERENCES User(id)
  )
  ENGINE=InnoDB
"""

# DATABASE PARAMETERS
HOST = '127.0.0.1'
DATABASE_NAME = 'purbeurre'
SQL_REQUESTS = [
    ('table', 'user', user),
    ('table', 'category', category),
    ('table', 'product', product),
    ('table', 'product_category', product_category),
    ('table', 'favorite', favorite),
    ('constraint', None, None),
    ('index', None, None)
]