# -*- coding: utf8 -*-

import json
import os
import re
from math import ceil

import requests

from pur_beurre.settings import JSON_DIR_PATH


class DataGetter:
    """
    a json data getter on openfoodfacts api.
    """

    def __init__(self, root_url='', first_page=1, page_getter_limit=0, paginated_data=False,
                 json_data_key='', filename='data.json'):

        self.root_url = root_url
        self.first_page = first_page
        self.page_getter_limit = page_getter_limit
        self.paginated_data = paginated_data
        self.json_data_key = json_data_key
        self.filename = filename

    def get_paginated_url(self, page):
        """
        if api provide several pages for a ressource, the ressource root url is rewritted for
        each requested page.
        :param page: number of requested page.
        :return: paginated url
        """
        url_without_extension = re.split(r'\.json', self.root_url)[0]
        if self.paginated_data:
            return url_without_extension + '/' + str(page) + '.json'
        else:
            return self.root_url

    @staticmethod
    def get_data(url):
        print("getting data from %s" % url)
        return requests.get(url).json()

    @property
    def file_path(self):

        if os.path.exists(JSON_DIR_PATH):
            file_path = os.path.join(JSON_DIR_PATH, self.filename)
        else:
            os.mkdir(JSON_DIR_PATH)
            file_path = os.path.join(JSON_DIR_PATH, self.filename)
        return file_path

    def write_file(self):
        url = self.get_paginated_url(self.first_page)

        if not os.path.exists(self.file_path):
            with open(self.file_path, 'w') as new_file:
                data = self.get_data(url)
                results_list = data[self.json_data_key]

                if self.paginated_data:
                    nb_pages = self.page_getter_limit
                    if self.page_getter_limit < 1:
                        nb_pages = int(ceil(float(data['count']) / float(data['page_size'])))
                    print("Nombre de pages %s" % nb_pages)

                    for page in range(2, nb_pages + 1):
                        next_url = self.get_paginated_url(page)
                        data = self.get_data(next_url)
                        results_list += data[self.json_data_key]
                json_data = json.dumps(results_list)
                new_file.write(json_data)
