#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division
import xml.etree.cElementTree as et
import MySQLdb
import sys, getopt
import warnings
import ConfigParser
from datetime import datetime

class DigestGenerator:
    
    def __init__(self, db_host, db_port, db_username, db_password, db_name, start_month, start_year, end_month, end_year):
        self.db = MySQLdb.connect(host=db_host, user=db_username, passwd=db_password, db=db_name)
        self.cursor = self.db.cursor()

        self.start_month = start_month
        self.start_year = start_year
        self.end_month = end_month
        self.end_year = end_year
        
        self.verify_valid_dates()
 
    def verify_valid_dates(self):
        if self.start_year > self.end_year or (self.start_year == self.end_year and self.start_month > self.end_month):
            raise ValueError('TO date %d.%d is prior to FROM date %d.%d.' % (self.end_month, self.end_year, self.start_month, self.end_month)) 
   
    def collect_car_data(self):
        for y in range(self.end_year - self.start_year + 1):
            year = self.start_year + y
            
            if year > self.start_year:
                month = 1
            else:
                month = self.start_month
            
            for m in range(month, 13):
                if year == self.end_year and m > self.end_month:
                    break

                self.receive_car_data(year, m)

    def receive_car_data(self, year_index, month_index):
        print "Year %i, month %i" % (year_index, month_index)
        mindate = '%i-%s-01' % (year_index, month_index if month_index > 9 else '0' + str(month_index))
        maxdate = '%i-%s-31' % (year_index, month_index if month_index > 9 else '0' + str(month_index))                

        self.cursor.execute(
            """select
            make, avg(power), avg(price), avg(mileage)
            from cars where date_added between %s and %s or (date_added < %s and (active = 1 or date_deactivated < %s))
            group by make
            order by make asc;""",
            (mindate, maxdate, mindate, maxdate))

        results = self.cursor.fetchall()
        for row in results:
            make = row[0]
            power = row[1]
            price = row[2]
            mileage = row[3]

            print '%s %s %s %s' % (make, power, price, mileage)


    def close_db(self):
        self.db.close()

def main(): 
    config = ConfigParser.RawConfigParser()
    config.read('carwatch.ini')
    
    db_host = config.get('DatabaseConfig', 'db.host')
    db_port = config.get('DatabaseConfig', 'db.port')
    db_user = config.get('DatabaseConfig', 'db.user') 
    db_password = config.get('DatabaseConfig', 'db.password') 
    db_name = config.get('DatabaseConfig', 'db.name')

    start_month = int(config.get('DigestConfig', 'digest.start_month'))
    start_year = int(config.get('DigestConfig', 'digest.start_year'))

    end_month = datetime.now().month
    end_year = datetime.now().year

    generator = DigestGenerator(db_host, db_port, db_user, db_password, db_name, start_month, start_year, end_month, end_year)
    generator.collect_car_data()
      
if __name__ == "__main__":
   main()

