#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division
import xml.etree.cElementTree as et
import MySQLdb
import sys, getopt
import warnings
import ConfigParser

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
    
    def __init__(self, db_host, db_port, db_username, db_password, db_name):
        self.db = MySQLdb.connect(host=db_host, user=db_username, passwd=db_password, db=db_name)
        self.cursor = self.db.cursor()
        warnings.filterwarnings('error', category=MySQLdb.Warning)
        self.bad_cars = []

    def record_bad_data(self, car):
        self.bad_cars.append(car)

    def print_bad_data(self):
        if len(self.bad_cars) != 0:
            print 'There were issues importing %i data entries. They may be incomplete in the DB.' % len(self.bad_cars)

    def import_car(self, car):
        try:
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
                    ON DUPLICATE KEY UPDATE 
                        date_updated = CURRENT_TIMESTAMP,
                        make = VALUES(make),
                        name = VALUES(name),
                        price = VALUES(price),
                        power = VALUES(power),
                        mileage = VALUES(mileage),
                        cubature = VALUES(cubature),
                        fuel = VALUES(fuel),
                        doors = VALUES(doors),
                        transmission_automatic = VALUES(transmission_automatic),
                        color = VALUES(color),
                        description = VALUES(description)""", 
                (car.carid, car.url, car.make, 
                car.name, car.price, car.production_month, 
                car.production_year, car.currency, car.power,
                car.mileage, car.cubature, car.fuel, 
                car.doors, car.transmission, car.color, 
                car.description, car.siteid))
        except:
            self.record_bad_data(car)

        self.db.commit()

    def print_progress(self, number_imported, number_total):
        sys.stdout.write("\rImported %i/%i cars (%i%%)" % (number_imported, number_total, round((number_imported/number_total)*100)))
        sys.stdout.flush()
       
    def import_cars(self, cars):
        number_of_imported = 0

        for car in cars:
            self.import_car(car)
            number_of_imported+=1
            self.print_progress(number_of_imported, len(cars))

    def close_db(self):
        self.db.close()

class Car:

    def __init__(self, car_xml, retrieve_date):
        self.car_xml = car_xml

        self.url = self.get_text('url')
        self.name = self.get_text('name')
        self.make = self.get_make()
        self.price = self.get_numeric(self.get_text('price'))
        self.currency = 1 if self.get_text('currency') == 'BGN' else 0 
        self.production_month = self.get_numeric(self.car_xml.find('production-date').attrib['month'])
        self.production_year = self.get_numeric(car_xml.find('production-date').attrib['year'])
        self.power = self.get_numeric(self.get_text('power'))
        self.mileage = self.get_numeric(self.get_text('mileage'))
        self.cubature = self.get_numeric(self.get_text('cubature'))
        self.fuel = self.get_text('fuel')
        self.doors = self.get_text('doors')
        self.transmission = car_xml.find('transmission').attrib['automatic'] == 'True'
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
        elif make_temp == 'Rolls':
            return 'Rolls Royce'
        elif make_temp == 'Asia':
            return 'Asia Motors'
        elif make_temp == 'Aston':
            return 'Aston Martin'
        elif make_temp == 'Land':
            return 'Land Rover'
        elif make_temp == 'Great':
            return 'Great Wall'
        elif make_temp == 'Range':
            return 'Range Rover'
        else:
            return make_temp

    def __str__(self):
        return '\nURL: ' + self.url + '\nNAME: ' + self.name

def main(argv): 
    config = ConfigParser.RawConfigParser()
    config.read('carwatch.ini')
    
    db_host = config.get('DatabaseConfig', 'db.host')
    db_port = config.get('DatabaseConfig', 'db.port')
    db_user = config.get('DatabaseConfig', 'db.user') 
    db_password = config.get('DatabaseConfig', 'db.password') 
    db_name = config.get('DatabaseConfig', 'db.name')
    
    input = ''

    opts, args = getopt.getopt(argv,"i:")

    for opt, arg in opts:
      if opt == "-i":
         input = arg

    print 'Loading input XML.'
    reader = CarReader(input)
    print 'Loaded ' + str(len(reader.cars)) + ' cars.'
    db_connection = DbImporter(db_host, db_port, db_user, db_password, db_name)
    db_connection.import_cars(reader.cars)
    print '\nImported into DB.'
    db_connection.print_bad_data()

      
if __name__ == "__main__":
   main(sys.argv[1:])

