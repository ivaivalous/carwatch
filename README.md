Carwatch is a on-going, unfinished project to track the second-hand car market in Bulgaria. The code itself is of course not really specific to Bulgaria and one can change it to work with any set of websites she desires.

Basically, carwatch crawls popular second-hand car websites using watch scripts. It then creates some XMLs out of that and another, consume script reads them into a database. A digest script then preparest stats for each month of operation that are published as JSON files and are then visualized by a web interface.

Not all of this is ready, and here is what is on the current TO DO list:

 - The current database is not normalized at at all; all it has is a single table that will grow quite large in time. Table design ought to be fixed
 - The web interface is not done yet. The project is at the point where data is exported to JSON and made available online but nothing much
 - Car brand stats to have a new stat showing how the brand compares to other brands in terms of time to sell

 
