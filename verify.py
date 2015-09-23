#!/usr/bin/env python
# -*- coding: utf-8 -*-

import MySQLdb
import ConfigParser
import requests


class UrlController:

    def __init__(self):
        self.set_database()
        self.urls = {}

    def retrieve_urls(self):
        self.cursor.execute(
            """SELECT id, url
            FROM carwatch.cars
            WHERE active = 1
            AND DATE(date_updated) <= DATE_SUB(CURDATE(), INTERVAL 7 DAY)
            LIMIT 100000;""")

        results = self.cursor.fetchall()
        for row in results:
            self.urls[row[0]] = row[1]

    def get_candidate_urls(self):
        return self.urls

    def update_cars(self, cars_to_update):
        for key, value in cars_to_update.items():
            if value is True:
                self.update_update_date(key)
            else:
                self.deactivate_car(key)

    def update_update_date(self, car_id):
        self.cursor.execute(
            """UPDATE carwatch.cars
            SET date_updated = NOW()
            WHERE id = %s""",
            (car_id))

    def deactivate_car(self, car_id):
        self.cursor.execute(
            """UPDATE carwatch.cars
            SET date_deactivated = NOW(),
            active = 0
            WHERE id = %s""",
            (car_id))

    def set_database(self):
        self.config = ConfigParser.RawConfigParser()
        self.config.read('carwatch.ini')

        db_host = self.config.get('DatabaseConfig', 'db.host')
        db_user = self.config.get('DatabaseConfig', 'db.user')
        db_password = self.config.get('DatabaseConfig', 'db.password')
        db_name = self.config.get('DatabaseConfig', 'db.name')

        self.db = MySQLdb.connect(host=db_host, user=db_user,
                                  passwd=db_password, db=db_name)

        self.cursor = self.db.cursor()


class Verifier:

    def __init__(self, id_to_urls):
        self.id_to_urls = id_to_urls
        self.config = ConfigParser.RawConfigParser()
        self.config.read('carwatch.ini')

        self.ids_to_update = {}

    def verify(self):
        self.headers = {
            'User-Agent':
            self.config.get('CrawlGeneralConfig', 'crawl.useragent')
        }

        for car_id in self.id_to_urls:
            self.ids_to_update[car_id] = self.verify_url(
                self.id_to_urls[car_id])

        return self.ids_to_update

    def verify_url(self, url):
        r = requests.get(url, headers=self.headers, allow_redirects=False)

        # Car websites don't usually 404 cars they've had removed
        # rather they 302 them for some reason
        if r.status_code == 302 or r.status_code == 404:
            print("Car with URL {0} was inactive.".format(url))
            return False

        # Obviously assumming a 5xx error would still mean the car's active
        # Good luck
        print("Car with URL {0} was active. Status code {1}."
              .format(url, r.status_code))
        return True


def main():
    url_controller = UrlController()
    url_controller.retrieve_urls()
    urls = url_controller.get_candidate_urls()
    verifier = Verifier(urls)

    ids_to_update = verifier.verify()
    url_controller.update_cars(ids_to_update)


if __name__ == "__main__":
    main()
