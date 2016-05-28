#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division
import MySQLdb
import sys
import getopt
import ConfigParser
from datetime import datetime
import json
from json import encoder


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
            self.start_year == self.end_year and
                self.start_month > self.end_month):

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
        digest_data_record = DigestData(year_index, month_index)

        self.cursor.execute(
            """select
            make, power, price, mileage, production_month, production_year
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
            prod_date = self.get_date_by_year_month(row[4], row[5])

            digest_data_record.add_line(make, power, price, mileage, prod_date)

        return digest_data_record

    def get_date_by_year_month(self, month, year):
        try:
            return datetime.strptime(
                '{0}-{1}'.format(year, month), '%Y-%m')
        except ValueError:
            # No valid production date was available
            return datetime.now()

    def close_db(self):
        self.db.close()


class DigestData:

    def __init__(self, year, month):
        self.lines = []
        self.brands = BrandList(year, month)
        self.year = year
        self.month = month

    def add_line(self, make, power, price, mileage, prod_date):
        line = DigestLine(make, power, price, mileage, prod_date)
        self.lines.append(line)

    def get_avg_power(self):
        valid_powers = []

        for l in self.lines:
            # Because some sellers set random numbers like 70000000
            if l.power >= 10 and l.power <= 800:
                valid_powers.append(l.power)

        return sum(valid_powers) / len(valid_powers)

    def get_avg_price(self):
        valid_prices = []

        for l in self.lines:
            if l.price >= 500 and l.price <= 2000000:
                valid_prices.append(l.price)

        return sum(valid_prices) / len(valid_prices)

    def populate_brands(self):
        print("There are " + str(len(self.lines)) +
              " lines attached to this data.")
        for line in self.lines:
            if line in self.brands:
                self.brands.merge(line)
            else:
                brand_to_pass = Brand([line])
                self.brands.brands_list.append(brand_to_pass)

        self.brands.set_total_of_cars(len(self.lines))


class Brand:

    def __init__(self, digest_lines):
        self.brand_name = digest_lines[0].make
        self.percentage = 0
        self.total = len(digest_lines)
        self.digest_lines = digest_lines

    def set_total(self, total):
        self.total = total

    def get_total_count(self):
        return len(self.digest_lines)

    def get_percentage(self, round_result=True):
        if self.total is not 0:
            percentage = (len(self.digest_lines) / self.total) * 100
            return round(percentage, 4) if round_result else percentage
        else:
            return 0

    def get_avg_power(self):
        refined = [line.power for line in self.digest_lines]

        for power in refined:
            if power < 10 or power > 800:
                refined.remove(power)

        if refined:
            return round(sum(refined) / len(refined))
        else:
            # No cars were present with valid power
            return 0

    def get_avg_price(self):
        refined = [line.price for line in self.digest_lines]

        if refined:
            return round(sum(refined) / len(refined))
        else:
            # No cars were present with valid price
            return 0

    def get_max_power(self):
        return sorted(
            [line.power for line in self.digest_lines if line.power < 800],
            reverse=True)[0]

    def get_avg_age(self):
        ages = [line.get_age() for line in self.digest_lines]

        return round(((sum(ages) / len(ages)) / 365.25), 1)

    def set_total_of_cars(self, total):
        self.total = total

    def __str__(self):
        return ('{0}\n\tCount:         {1}% ({2} cars)\n\t' +
                'Average price: {3} BGN\n\t' +
                'Average power: {4} ' +
                'HP (max {5})\n\tAverage age:   {6} years\n').format(
            self.brand_name, self.get_percentage(), self.get_total_count(),
            self.get_avg_price(), self.get_avg_power(), self.get_max_power(),
            self.get_avg_age())

    def get_json(self):
        return {
            "name": self.brand_name,
            "percentage": self.get_percentage(),
            "averagePrice": self.get_avg_price(),
            "averagePower": self.get_avg_power(),
            "averageAge": self.get_avg_age()
        }


class BrandList:

    def __init__(self, year, month):
        self.brands_list = []
        self.year = year
        self.month = month

    def __contains__(self, digest_line):
        return digest_line.make in self.get_brand_names()

    def get_brand_names(self):
        return [brand.brand_name for brand in self.brands_list]

    def merge(self, digest_line):
        for brand in self.brands_list:
            if brand.brand_name == digest_line.make:
                brand.digest_lines.append(digest_line)

    def set_total_of_cars(self, total):
        for brand in self.brands_list:
            brand.set_total_of_cars(total)

    def __str__(self):
        representation = 'Brands data:\n'

        for brand in sorted(
                self.brands_list,
                key=lambda brand: brand.get_percentage(False),
                reverse=True):
            representation += str(brand)

        return representation

    def get_json(self):
        representation = {
            "month": self.month,
            "year": self.year,
            "brands": []
        }

        for brand in sorted(
                self.brands_list,
                key=lambda brand: brand.get_percentage(False),
                reverse=True):
            if(brand.get_total_count() >= self.min_cutoff):
                representation["brands"].append(brand.get_json())

        return representation

    def save_json_to_file(self, min_cutoff):
        # Cars that are under a certain number in count will not be included
        # in reports because data might be off
        # also cars might become identifiable
        self.min_cutoff = min_cutoff
        filename = 'digest-{0}-{1}.json'.format(self.year, self.month)

        with open(filename, 'w') as outfile:
                encoder.FLOAT_REPR = lambda o: format(o, '.2f')
                json.dump(
                    self.get_json(), outfile, sort_keys=True,
                    indent=4, separators=(',', ': '))


class DigestLine:

    def __init__(self, make, power, price, mileage, prod_date):
        self.make = make
        self.power = power
        self.price = price
        self.mileage = mileage
        self.prod_date = prod_date

    def get_age(self):
        return (datetime.now() - self.prod_date).days


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
    min_cutoff = int(config.get('DigestConfig', 'digest.min_count_cutoff'))

    end_month = datetime.now().month
    end_year = datetime.now().year

    generator = DigestGenerator(db_host, db_port, db_user,
                                db_password, db_name, start_month,
                                start_year, end_month, end_year)

    generator.collect_car_data(digest_mode)

    for digest in generator.digest_data:
        digest.populate_brands()
        print(digest.brands)
        digest.brands.save_json_to_file(min_cutoff)

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
