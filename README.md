Carwatch is a on-going, unfinished project to track the second-hand car market in Bulgaria. The code itself is of course not really specific to Bulgaria and one can change it to work with any set of websites she desires.

Basically, carwatch crawls popular second-hand car websites using watch scripts. It then creates some XMLs out of that and another, consume script reads them into a database. A digest script then prepares stats for each month of operation that are published as JSON files and are then visualized by a web interface. It's all Python except for the web interface that will use HTML and JS.

Not all of this is ready, and here is what is on the current TO DO list:

 - The current database is not normalized at at all; all it has is a single table that will grow quite large in time. Table design ought to be fixed
 - The web interface is not done yet. The project is at the point where data is exported to JSON and made available online but nothing much
 - Car brand stats to have a new stat showing how the brand compares to other brands in terms of time to sell

What does output look like? For each brand, there is a set of stats prepared. 

    {
        "averageAge": 11.70,
        "averagePower": 105.00,
        "averagePrice": 5103.00,
        "name": "VW",
        "percentage": 12.91
    }
    
The above is Bulgaria's top seller brand, VW. We can see almost 13% of all second hand cars are really VWs. We don't print out the exact number of cars as it ought to be incorrect. As we crawl multiple sites there might be duplicated cars. People like to adverstise cars on multiple sites so I thought showing a percent would be more fair. We also have averageAge, also a key factor for the marker. The number of 11.70 is in years, so VWs sold in Bulgaria are almost 12 years old, on average. The averagePower is really horse power, and in this case is 105 hp. I've noticed quite a lot of sellers either enter 0 hp or some insane number like 200000 for this field, so configuration lets you add cutoff values for min and max horsepower. Finally, averagePrice refers to the average price of a car of this brand, in BGN. I've left it for the web interface to be able to visualize this fields in other currencies.

So, the entire program is run on a schedule, in parts. 

First, the scripts that collect data are executed. Currently they are *watch_cars.py* and *watch_carmarket.py*. They will take several hours and since they do crawling it's not really recommended to run them very often. I do the whole cycle once a week.

Once they finish, there are several car*.xml files generated that are used for database import. The *consume.py* script is run to add the new data to database. Since most cars wouldn't have really changed between two runs, most of the vehicles in database will just be updated.

The *verify.py* script is meant to be executed after that. It will see which cars haven't been updated in the last seven days and will check whether they're still available online. Basically, it will try loading the URLs and see if it gets a 404 or 302. These cars will be marked inactive in the database. 
