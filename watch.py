#!/usr/bin/env python
# -*- coding: utf-8 -*-

from lxml import html
import requests
import time

class CarCrawler:

    def __init__(self, max_url_count, root_url, home_url):
        self.max_url_count = max_url_count
        self.home_url = home_url
        self.root_url = root_url
        self.urls = []
        self.cars = []
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)'
        }

    def collect_urls(self, url):
        page = requests.get(url, headers=self.headers)
        tree = html.fromstring(page.text)
        self.urls.extend(tree.xpath('//*[@class="ver15black"]/@href'))

        next_page_url = tree.xpath("(//a[text()='Следваща'])[1]/@href".decode("utf-8"))[0]
        return self.home_url + next_page_url

    def start_collecting_urls(self):
        next_page_url = self.home_url

        try:
            while True:
                next_page_url = self.collect_urls(next_page_url)

                if len(self.urls) >= self.max_url_count:
                    return
        except IndexError:
            print len(self.urls)

    def collect_cars(self):
        for url in self.urls:
            full_url = self.root_url + url
            page = requests.get(full_url, headers=self.headers)
            tree = html.fromstring(page.text)
            car = Car(full_url, tree)
            self.cars.append(car)

    def print_cars(self):
        for car in self.cars:
            print car

class Car:

    def __init__(self, url, tree):
        self.name = self.extract_data(tree, '//*[@class="ver30black"]/strong')
        self.url = url
        self.price = self.extract_data(tree, '//*[@class="ver20black"]/strong')
        self.currency = self.extract_data(tree, '//span[@class="ver20black"]/..')
        self.prod_date = self.extract_data(tree, '//img[contains(@src, "calendar.gif")]//following::td[1]')
        self.power = self.extract_data(tree, '//img[contains(@src, "power")]//following::td[1]')
        self.mileage = self.extract_data(tree, '//img[contains(@src, "mileage.gif")]//following::td[1]')
        self.cubature = self.extract_data(tree, '//img[contains(@src, "cubature.gif")]//following::td[1]')
        self.fuel = self.extract_data(tree, '//img[contains(@src, "petrol.gif")]//following::td[1]')
        self.doors = self.extract_data(tree, '//img[contains(@src, "door.gif")]//following::td[1]')
        self.transmission = self.extract_data(tree, '//img[contains(@src, "gear.gif")]//following::td[1]')
        self.colour = self.extract_data(tree, '//img[contains(@src, "palette.gif")]//following::td[1]')

    def extract_data(self, tree, xpath):
        try:
            return tree.xpath(xpath)[0].text.encode("utf-8").strip()
        except IndexError:
            return 'N/A'

    def __str__(self):
        return 'URL:             ' + self.url + '\nNAME:            ' + self.name + '\nPRICE:           ' + self.price + ' ' + self.currency + '\nPRODUCTION DATE: ' + self.prod_date + '\nPOWER (HP):      ' + self.power + '\nMILEAGE:      $

    def to_json(self):
        return

crawler = CarCrawler(20, 'http://www.cars.bg/', 'http://www.cars.bg/?go=cars&search=1&advanced=&fromhomeu=1&CityId=0&currencyId=1&yearTo=&autotype=1&stateId=1&offerFrom4=1&offerFrom1=1&offerFrom2=1&offerFrom3=1&categoryId=0&doorId=0&brand$
crawler.start_collecting_urls()
crawler.collect_cars()
crawler.print_cars()

