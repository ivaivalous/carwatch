#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division
import MySQLdb
import sys
import getopt
import ConfigParser
from datetime import datetime


class DigestGenerator:

    def __init__(self, db_host, db_port, db_username,
                 db_password, db_name, start_month,
                 start_year, end_month, end_year):

        self.digest_data = []

        self.db = MySQLdb.connect(host=db_host, user=db_username,
                                  passwd=db_password, db=db_name)
        self.cursor = self.db.cursor()

        self.start_month = start_month
        self.start_year = start_year
        self.end_month = end_month
        self.end_year = end_year

        self.verify_valid_dates()

    def verify_valid_dates(self):
        if self.start_year > self.end_year or (
            self.start_year == self.end_year
               and self.start_month > self.end_month):

            raise ValueError('TO date %d.%d is prior to FROM date %d.%d.' (
                    self.end_month, self.end_year, self.start_month,
                    self.end_month))

    def collect_car_data(self, digest_mode):
        if digest_mode == "current":
            self.end_month = self.start_month
            self.end_year = self.start_year

        for y in range(self.end_year - self.start_year + 1):
            year = self.start_year + y

            if year > self.start_year:
                month = 1
            else:
                month = self.start_month

            for m in range(month, 13):
                if year == self.end_year and m > self.end_month:
                    break

                self.digest_data.append(self.receive_car_data(year, m))

    def receive_car_data(self, year_index, month_index):
        print('Year {0}, month {1}'.format(year_index, month_index))

        m_symbol = month_index if month_index > 9 else '0' + str(month_index)
        mindate = '%i-%s-01' % (year_index, m_symbol)
        maxdate = '%i-%s-31' % (year_index, m_symbol)
        digest_data_record = DigestData()

        self.cursor.execute(
            """select
            make, power, price, mileage
            from cars where date_added between %s and %s or
            (date_added < %s and (active = 1 or date_deactivated < %s))
            order by make asc;""",
            (mindate, maxdate, mindate, maxdate))

        results = self.cursor.fetchall()
        for row in results:
            make = row[0]
            power = row[1]
            price = row[2]
            mileage = row[3]

            digest_data_record.add_line(make, power, price, mileage)

        return digest_data_record

    def close_db(self):
        self.db.close()


class DigestData:

    def __init__(self):
        self.lines = []

    def add_line(self, make, power, price, mileage):
        line = DigestLine(make, power, price, mileage)
        self.lines.append(line)

    def get_avg_power(self):
        valid_powers = []

        for l in self.lines:
            # Because some sellers set random numbers like 70000000
            if l.power >= 10 and l.power <= 1200:
                valid_powers.append(l.power)

        return sum(valid_powers) / len(valid_powers)

    def get_avg_price(self):
        valid_prices = []

        for l in self.lines:
            if l.price >= 500 and l.price <= 2000000:
                valid_prices.append(l.price)

        return sum(valid_prices) / len(valid_prices)


class DigestLine:

    def __init__(self, make, power, price, mileage):
        self.make = make
        self.power = power
        self.price = price
        self.mileage = mileage


def main(digest_mode):

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

    generator = DigestGenerator(db_host, db_port, db_user,
                                db_password, db_name, start_month,
                                start_year, end_month, end_year)

    generator.collect_car_data(digest_mode)

    for data_record in generator.digest_data:
        print("Average horsepower: " + str(data_record.get_avg_power()))
        print("Average price: " + str(data_record.get_avg_price()))


if __name__ == "__main__":
    opts = getopt.getopt(sys.argv[1:], "a:c:")
    digest_mode = "all"

    for opt in opts:
        if opt == "-c":
            digest_mode = "current"

    main(digest_mode)
