#!/usr/bin/env python
# -*- coding: utf-8 -*-

import xml.etree.cElementTree as et
import MySQLdb
import sys, getopt

class CarReader:

    def __init__(self, filename):
        self.tree = None
        self.cars = []
        self.date = None

        self.filename = filename
        self.read_file()
        self.set_date()
        self.read_cars()

    def read_file(self):
        with open(self.filename) as f:
            content = f.read()
            self.tree = et.fromstring(content)

    def set_date(self):
        self.date = self.tree.attrib['collection-date']

    def read_cars(self):
        for c in self.tree.findall('car'):
            self.cars.append(Car(c, self.date))

    def print_cars(self):
        for c in self.cars:
            print c


class DbImporter:

    def __init__(self):
        self.db = MySQLdb.connect(host="localhost", user="root", passwd="", db="carwatch")
        self.cursor = self.db.cursor()

    def import_car(self, car):
        self.cursor.execute(
            """INSERT INTO cars (
                carid, url, make,
                name, price, production_month,
                production_year, currency, power,
                mileage, cubature, fuel,
                doors, transmission_automatic, color,
                description, date_collected, date_updated,
                siteid)
                VALUES (
                    %s, %s, %s,
                    %s, %s, %s,
                    %s, %s, %s,
                    %s, %s, %s,
                    %s, %s, %s,
                    %s, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP,
                    %s)
                ON DUPLICATE KEY UPDATE date_updated = CURRENT_TIMESTAMP """,
            (car.carid, car.url, car.make,
            car.name, car.price, car.production_month,
            car.production_year, 1, car.power,
            car.mileage, car.cubature, car.fuel,
            car.doors, 0, car.color,
            car.description, car.siteid))

        self.db.commit()

    def import_cars(self, cars):
        for car in cars:
            self.import_car(car)

    def close_db(self):
        self.db.close()

class Car:

    def __init__(self, car_xml, retrieve_date):
        self.cursor = self.db.cursor()

    def import_car(self, car):
        self.cursor.execute(
            """INSERT INTO cars (
                carid, url, make,
                name, price, production_month,
                production_year, currency, power,
                mileage, cubature, fuel,
                doors, transmission_automatic, color,
                description, date_collected, date_updated,
                siteid)
                VALUES (
                    %s, %s, %s,
                    %s, %s, %s,
                    %s, %s, %s,
                    %s, %s, %s,
                    %s, %s, %s,
                    %s, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP,
                    %s)
                ON DUPLICATE KEY UPDATE date_updated = CURRENT_TIMESTAMP """,
            (car.carid, car.url, car.make,
            car.name, car.price, car.production_month,
            car.production_year, 1, car.power,
            car.mileage, car.cubature, car.fuel,
            car.doors, 0, car.color,
            car.description, car.siteid))

        self.db.commit()

    def import_cars(self, cars):
        for car in cars:
            self.import_car(car)

    def close_db(self):
        self.db.close()

class Car:

    def __init__(self, car_xml, retrieve_date):
        self.car_xml = car_xml

        self.url = self.get_text('url')
        self.name = self.get_text('name')
        self.make = self.get_make()
        self.price = self.get_numeric(self.get_text('price'))
        self.currency = self.get_text('currency')
        self.production_month = self.get_numeric(self.car_xml.find('production-date').attrib['month'])
        self.production_year = self.get_numeric(car_xml.find('production-date').attrib['year'])
        self.power = self.get_numeric(self.get_text('power'))
        self.mileage = self.get_numeric(self.get_text('mileage'))
        self.cubature = self.get_numeric(self.get_text('cubature'))
        self.fuel = self.get_text('fuel')
        self.doors = self.get_text('doors')
        self.transmission = car_xml.find('transmission').attrib['automatic'] == True
        self.color = self.get_text('color')
        self.description = self.get_text('description')

        self.siteid = self.get_site()
        self.carid = self.get_carid()
        self.retrieve_date = retrieve_date

    def get_text(self, element_name):
        try:
            return self.car_xml.find(element_name).text.encode("utf-8")
        except:
            return 'N/A'

    def get_numeric(self, value):
        try:
            return int(value)
        except:
            return -1

    def get_site(self):
        return self.url.split('//')[1].split('/')[0].replace('www.', '')

    def get_carid(self):
        return self.url.split(self.siteid)[1].replace('/', '')

        self.car_xml = car_xml

        self.url = self.get_text('url')
        self.name = self.get_text('name')
        self.make = self.get_make()
        self.price = self.get_numeric(self.get_text('price'))
        self.currency = self.get_text('currency')
        self.production_month = self.get_numeric(self.car_xml.find('production-date').attrib['month'])
        self.production_year = self.get_numeric(car_xml.find('production-date').attrib['year'])
        self.power = self.get_numeric(self.get_text('power'))
        self.mileage = self.get_numeric(self.get_text('mileage'))
        self.cubature = self.get_numeric(self.get_text('cubature'))
        self.fuel = self.get_text('fuel')
        self.doors = self.get_text('doors')
        self.transmission = car_xml.find('transmission').attrib['automatic'] == True
        self.color = self.get_text('color')
        self.description = self.get_text('description')

        self.siteid = self.get_site()
        self.carid = self.get_carid()
        self.retrieve_date = retrieve_date

    def get_text(self, element_name):
        try:
            return self.car_xml.find(element_name).text.encode("utf-8")
        except:
            return 'N/A'

    def get_numeric(self, value):
        try:
            return int(value)
        except:
            return -1

    def get_site(self):
        return self.url.split('//')[1].split('/')[0].replace('www.', '')

    def get_carid(self):
        return self.url.split(self.siteid)[1].replace('/', '')

    def get_make(self):
        make_temp = self.name.split(' ')[0]

        if make_temp == 'Alfa':
            return 'Alfa Romeo'
        elif make_temp == 'Royce':
            return 'Royce Rolls'
        elif make_temp == 'Asia':
            return 'Asia Motors'
        elif make_temp == 'Aston':
            return 'Aston Martin'
        elif make_temp == 'Land':
            return 'Land Rover'
        else:
            return make_temp

    def __str__(self):
        return '\nURL: ' + self.url + '\nNAME: ' + self.name

def main(argv):
    input = ''

    opts, args = getopt.getopt(argv,"i:")

    for opt, arg in opts:
      if opt == "-i":
         input = arg

    reader = CarReader(input)
    print 'Loaded ' + str(len(reader.cars)) + ' cars.'
    db_connection = DbImporter()
    db_connection.import_cars(reader.cars)
    print 'Imported into DB.'


if __name__ == "__main__":
   main(sys.argv[1:])
