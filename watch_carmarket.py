#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division
from lxml import html
import requests
import sys
from time import gmtime, strftime
import re
import ConfigParser
import time


class CarCrawler:

    def __init__(self, max_url_count, root_url, home_url, config):
        self.xml_template = config.get('CrawlXmlConfig', 'crawl.xml_template')
        self.max_url_count = max_url_count
        self.home_url = home_url
        self.root_url = root_url
        self.urls = []
        self.cars = []
        self.headers = {
            'User-Agent': config.get('CrawlGeneralConfig', 'crawl.useragent')
        }
        self.car_count = 0
        self.execution_time = strftime("%Y-%m-%d-%H-%M-%S", gmtime())
        self.filename = './carsm-' + self.execution_time + '.xml'
        self.page = None
        self.tree = None

    def collect_urls(self, url, retry=True):
        try:
            self.page = requests.get(url, headers=self.headers)
        except requests.exceptions.ConnectionError:
            if retry:
                # Counter connection issues
                time.sleep(15)
                self.collect_urls(url, retry=False)

        self.tree = html.fromstring(self.page.text)
        self.urls.extend(self.tree.xpath(
            "//a[@class='cmOffersListLink']/@href"))

        next_page_url = self.tree.xpath("//li[@class='next']/a/@href")[0]
        return next_page_url

    def start_collecting_urls(self):
        self.last_page_reached = False
        next_page_url = self.home_url

        self.init_file()
        while True:
            try:
                next_page_url = self.collect_urls(next_page_url)
            except IndexError:
                try:
                    next_page_url = self.collect_urls(next_page_url)
                except IndexError:
                    print("\nCrawling stopped due to no next " +
                          "page button being present")
                    self.last_page_reached = True

            self.collect_cars()
            self.print_cars_to_file()
            self.urls = []
            self.cars = []

            percent = (self.car_count / self.max_url_count) * 100
            sys.stdout.write("\r Collected {0} cars ({1}%%)"
                             .format(self.car_count, round(percent)))
            sys.stdout.flush()

            if self.last_page_reached or self.car_count >= self.max_url_count:
                print('\n')
                self.complete_file()
                return

    def collect_cars(self):
        car_containers = self.tree.xpath(
            '//div[contains(@class, "cmOffersListItem")]')
        index = 0

        for car_container in car_containers:
            full_url = self.urls[index]

            car = Car(full_url, car_container, index)
            car.set_xml_template(self.xml_template)

            self.cars.append(car)
            self.car_count += 1
            index += 1

    def print_cars(self):
        for car in self.cars:
            print(car)

    def init_file(self):
        with open(self.filename, 'w') as f:
            print >>f, (
                 '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n' +
                 '<cars collection-date="' + self.execution_time + '">')

    def complete_file(self):
        with open(self.filename, 'a') as f:
            print >>f, '</cars>'

    def print_cars_to_file(self):
        f = open(self.filename, 'a')

        for car in self.cars:
            print >>f, car


class Car:

    def __init__(self, url, tree, index):
        self.index = index
        self.name = self.strip_xml_special_chars(
            self.extract_data(tree, '//span[@class="cmOffersListName"]'))
        self.url = self.strip_xml_special_chars(url).split('?')[0]
        self.price = self.extract_price(
            self.extract_data(tree, '//strong[@itemprop="price"]'))
        self.year = 0
        self.month = 0

        self.currency = self.extract_data(
            tree, '//*[@itemprop="priceCurrency"]')

        self.power = self.extract_num(
            self.extract_data(
                tree, '//*[@class="cmOffersListMoreInfoRow"][2]/strong'))

        self.mileage = self.extract_num(
            self.extract_price(
                self.extract_data(
                    tree, '//*[@class="cmOffersListMoreInfoRow"][4]/strong'))
            ).replace('км', '')

        self.cubature = '-1'
        self.fuel = self.extract_data(
            tree, '//*[@class="cmOffersListMoreInfoRow"][1]/strong')

        # Doors count not present on this page
        self.doors = 'N/A'
        self.transmission = self.extract_data(
            tree, '//*[@class="cmOffersListMoreInfoRow"][3]/strong')

        self.colour = self.extract_data(
            tree, '//*[@class="cmOffersListMoreInfoRow"][5]/strong')

        # No car description is present on this page
        self.description = 'N/A'

        self.set_production_date()
        self.set_description()
        self.transmission = self.is_transmission_automatic()
        self.fuel = self.get_fuel_type(self.fuel)

    def set_xml_template(self, xml_template):
        self.xml_template = xml_template

    def extract_data(self, tree, xpath):
        try:
            return tree.xpath(xpath)[self.index].text.encode("utf-8").strip()
        except (IndexError, AttributeError):
            return 'N/A'

    def extract_price(self, price_raw):
        return price_raw.replace(',', '').replace(' ', '')

    def extract_num(self, raw_field):
        return raw_field.split(' ')[0].replace(',', '')

    def set_production_date(self):
        try:
            self.month_raw = re.compile('\d+').split(self.prod_date)[0]
            self.year = self.prod_date.replace(self.month_raw, '').split(' ')
            [0]

            self.month = self.get_month(self.month_raw)
        except:
            pass

    def get_month(self, representation):
            return {
                'Януари': 1,
                'Февруари': 2,
                'Март': 3,
                'Април': 4,
                'Май': 5,
                'Юни': 6,
                'Юли': 7,
                'Август': 8,
                'Септември': 9,
                'Октомври': 10,
                'Ноември': 11,
                'Декември': 12
            }.get(representation, 1)

    def is_transmission_automatic(self):
        return self.transmission == 'Автоматична'

    def get_fuel_type(self, representation):
        return {
            'Бензин': 'gasoline',
            'Дизел': 'diesel',
            'Газ/Бензин': 'gasoline/LPG',
            'Газ': 'LPG'
        }.get(representation, 'N/A')

    def set_description(self):
        self.description = self.strip_xml_special_chars(self.description)

    def strip_xml_special_chars(self, input):
        return input.replace('&', '&amp;').replace(
            '<', '&lt;').replace('>', '&gt;')

    def __str__(self):
        return (self.xml_template.format(
            self.url, self.name, self.price,
            self.currency, str(self.month), str(self.year),
            self.power, self.mileage, self.cubature,
            self.fuel, self.doors, str(self.transmission),
            self.colour, self.description))


def main():
    config = ConfigParser.RawConfigParser()
    config.read('carwatch.ini')

    max_crawl_count = int(config.get(
        'CarmarketCrawlerConfig', 'site.carmarket.max_crawl'))
    starting_url = config.get(
        'CarmarketCrawlerConfig', 'site.carmarket.root_url')
    crawl_start_url = config.get(
        'CarmarketCrawlerConfig', 'site.carmarket.start_url')

    crawler = CarCrawler(
        max_crawl_count, starting_url, crawl_start_url, config)
    crawler.start_collecting_urls()

if __name__ == "__main__":
    main()
