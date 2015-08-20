#!/usr/bin/env python
# -*- coding: utf-8 -*-

import xml.etree.cElementTree as et

class CarReader:

    def __init__(self, filename):
        self.car_counter = 0
        self.tree = None
        self.cars = []

        self.filename = filename
        self.read_file()
        self.read_cars()

    def read_file(self):
        with open(self.filename) as f:
            content = f.read()
            self.tree = et.fromstring(content)

    def read_cars(self):
        for c in self.tree.findall('car'):
            self.car_counter+=1
            self.cars.append(Car(c))

    def print_cars(self):
        for c in self.cars:
            print c


class Car:

    def __init__(self, car_xml):
        self.url = car_xml.find('url').text.encode("utf-8")
        self.name = car_xml.find('name').text.encode("utf-8")

    def __str__(self):
        return '\nURL: ' + self.url + '\nNAME: ' + self.name

reader = CarReader('cars_full.xml')
print len(reader.cars)
reader.print_cars()
