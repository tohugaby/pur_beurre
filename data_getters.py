import json
from math import ceil

import requests


class DataGetter:
    """
    a json data getter on openfoodfacts api.
    """
    root_url = ''
    first_page = 1
    page_getter_limit = 0
    paginated_data = False
    json_data_key = ''
    filename = 'data.json'

    def get_paginated_url(self, url, page):
        if self.paginated_data:
            return url + '/' + str(page) + '.json'
        else:
            return url

    def get_data(self, url):
        print("getting data from %s" % (url))
        return requests.get(url).json()

    def write_file(self):
        url = self.get_paginated_url(self.root_url, self.first_page)

        with open(self.filename, 'w') as new_file:
            data = self.get_data(url)
            results_list = data[self.json_data_key]

            if self.paginated_data:
                nb_pages = self.page_getter_limit
                if self.page_getter_limit < 2:
                    nb_pages = int(ceil(float(data['count']) / float(data['page_size'])))
                print("Nombre de pages %s" % (nb_pages))

                for page in range(2, nb_pages + 1):
                    next_url = self.get_paginated_url(self.root_url, page)
                    data = self.get_data(next_url)
                    results_list += data[self.json_data_key]
            json_data = json.dumps(results_list)
            new_file.write(json_data)


class ProductDataGetter(DataGetter):
    root_url = 'https://fr.openfoodfacts.org/langue/francais'
    first_page = 1
    paginated_data = True
    # page_getter_limit = 2
    json_data_key = 'products'
    filename = 'products.json'


class CategoryDataGetter(DataGetter):
    root_url = 'https://fr.openfoodfacts.org/categories.json'
    first_page = 1
    paginated_data = False
    json_data_key = 'tags'
    filename = 'categories.json'


def main():
    cat = CategoryDataGetter()
    cat.write_file()

    prod = ProductDataGetter()
    prod.page_getter_limit = 10
    prod.write_file()


if __name__ == '__main__':
    main()