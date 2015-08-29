#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division
from lxml import html
import requests
import sys
from time import gmtime, strftime
import ConfigParser


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
        self.filename = './cars-' + self.execution_time + '.xml'

    def collect_urls(self, url):
        page = requests.get(url, headers=self.headers)
        tree = html.fromstring(page.text)
        self.urls.extend(tree.xpath('//*[@class="ver15black"]/@href'))

        next_page_url = tree.xpath(
            "(//a[text()='Следваща'])[2]/@href".decode("utf-8"))[0]
        return self.home_url + next_page_url

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
                    print("\nCrawling stopped due to no next page " +
                          "button being present")
                    self.last_page_reached = True

            self.collect_cars()
            self.print_cars_to_file()
            self.urls = []
            self.cars = []

            percent = (self.car_count / self.max_url_count) * 100
            sys.stdout.write("\r Collected {0} cars ({1}%%)".format(
                self.car_count, round(percent)))
            sys.stdout.flush()

            if self.last_page_reached or self.car_count >= self.max_url_count:
                print('\n')
                self.complete_file()
                return

    def collect_cars(self):
        for url in self.urls:
            full_url = self.root_url + url
            page = requests.get(full_url, headers=self.headers)
            tree = html.fromstring(page.text)
            car = Car(full_url, tree)
            car.set_xml_template(self.xml_template)

            self.cars.append(car)
            self.car_count += 1

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

    def __init__(self, url, tree):
        self.name = self.strip_xml_special_chars(
            self.extract_data(tree, '//*[@class="ver30black"]/strong'))

        self.url = url
        self.price = self.extract_price(
            self.extract_data(tree, '//*[@class="ver20black"]/strong'))

        self.year = 0
        self.month = 0

        self.currency = self.extract_data(
            tree, '//span[@class="ver20black"]/..')

        self.prod_date = self.extract_data(
            tree, '//img[contains(@src, "calendar.gif")]//following::td[1]')

        self.power = self.extract_num(
            self.extract_data(
                tree, '//img[contains(@src, "power")]//following::td[1]'))

        self.mileage = self.extract_num(
            self.extract_price(
                self.extract_data(
                    tree,
                    '//img[contains(@src, "mileage.gif")]//following::td[1]')))

        self.cubature = self.extract_num(
            self.extract_data(
                tree,
                '//img[contains(@src, "cubature.gif")]//following::td[1]'))

        self.fuel = self.extract_data(
            tree, '//img[contains(@src, "petrol.gif")]//following::td[1]')

        self.doors = self.extract_data(
            tree, '//img[contains(@src, "door.gif")]//following::td[1]')

        self.transmission = self.extract_data(
            tree, '//img[contains(@src, "gear.gif")]//following::td[1]')

        self.colour = self.extract_data(
            tree, '//img[contains(@src, "palette.gif")]//following::td[1]')

        self.description = self.extract_data(
            tree,
            '//b[text()="Допълнителна информация"]//following::td[2]'
            .decode("utf-8"))

        self.set_production_date()
        self.set_description()
        self.transmission = self.is_transmission_automatic()
        self.fuel = self.get_fuel_type(self.fuel)

    def set_xml_template(self, xml_template):
        self.xml_template = xml_template

    def extract_data(self, tree, xpath):
        try:
            return tree.xpath(xpath)[0].text.encode("utf-8").strip()
        except (IndexError, AttributeError):
            return 'N/A'

    def extract_price(self, price_raw):
        return price_raw.replace(',', '')

    def extract_num(self, raw_field):
        return raw_field.split(' ')[0].replace(',', '')

    def set_production_date(self):
        try:
            self.month = self.get_month(self.prod_date.split(' ')[0])
            self.year = self.prod_date.split(' ')[1]
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
        return self.transmission == 'Автоматични'

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
        'CarsBgCrawlerConfig', 'site.cars.max_crawl'))
    starting_url = config.get(
        'CarsBgCrawlerConfig', 'site.cars.root_url')
    crawl_start_url = config.get(
        'CarsBgCrawlerConfig', 'site.cars.start_url')

    crawler = CarCrawler(
        max_crawl_count, starting_url, crawl_start_url, config)
    crawler.start_collecting_urls()

if __name__ == "__main__":
    main()
