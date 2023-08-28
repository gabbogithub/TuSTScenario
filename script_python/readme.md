# Overview
In this directory there are three python scripts written to be used with a sumo simulation and a csv file that contains cells associated with cell phone towers. 
The first one extracts cell sites located inside a certain city and writes them into a new file. The second one maps a cell site to every vehicle in the simulation
and regularly checks that the distance doesn't exceed a value given by the user. If it happens, a new association is computed. Finally, the third script analyses the results of the second script and extracts some metrics of interest.

# Requirements
To execute the scripts, aside from a sumo and python installation, you have to install some python libraries. A pip file is provided to quickly install all the libraries needed.
What follows is a list of the requirements:
- **Sumo** : the scripts were tested with versions that go from **1.16.0** to **1.18.0**.
- **Python** : the version used is **3.11.3** but older versions may work.
- **Pandas** : It is used to analyze csv and create new ones. Version **2.0.3** was used but other version will probably work as well.
- **Libsumo** : It is used to execute the simulation and modify it. Version from **1.16.0** to **1.18.0** were tested and used.
- **Pyproj** : It is used to convert coordinates from latitude and longitude to x and y values of the simulation. Version **3.6.0** was used.

# How to
All the scripts have a variety of options that can be listes with the command **--help**. Some are required while others are optional.

## Extraction script
In order to use it you have to specify the path to the input file with the **-i** or **--input** option and the name of the city to filter the cell sites 
with the option **-c** or **--city**. This script was written to be used with Lte Italy csv files but could theoretically work with every csv files that
have at least four columns with the following names: *node_id* (to uniquely identify sites), *cell_lat* (latitude of the site), *cell_long* (longitude of the site) 
and *site_name* (column that has to contain the name of the city).

## Association script
In order to use it you have to specify the path to the sumo simulation configuration file with the option **-su** or **--sumo_cfg**. You will then need to provide the path to csv file with the cell sites using the option **-i** or **--input** and the path to the net file of the simulation with the option **-n** or **--sumo_net** (because it is used to convert from latitude and longitude to x and y values of the simulation). This script should work with every csv file that follows this structure: first column *node_id of the site*, second column *site latitude* and third column *site longitude*. If you don't have a csv file with the sites, you can still use the script using the option **-c** or **--cell_sites** to generate random cell sites and in this case the net file is not needed.

## Analysis script
This script has many options that can produce different output files:
- **-us/--users** : the script will write an output file with the number of users associated with a cell site at every timestamp. It requires an input file with the associations between vehicles and cell sites that uses commas as separators like the file produced by the second script.
- **-rt/--route-time** : the length of the route followed by every vehicle (in meters) and the time the vehicle remained in the simulation (in seconds). It requires an input file with the route length, the depart and arrival times and semicolon as separator. The suggested file to use is the output file produced by sumo using the **--vehroute-output** option. Remember to convert it into a csv file using the tool **xml2csv.py**.
- **-si/--unique_sites** : the script will write an output file with the the number of unique sites associated with the vehicles throughout the simulation. It requires an input file with the associations between vehicles and cell sites that uses commas as separators like the file produced by the second script.
- **-nc/--number_changes** : the script will write an output file with the the number of times a vehicle changed site. The changes include when a vehicle that had an association with a site, drives too far from that site and no other sites is near enough to establish a connection. In other words it counts the number of times the state of the association of a vehicle changed. It requires an input file with the associations between vehicles and cell sites that uses commas as separators like the file produced by the second script.
- **-ns/--new_sites** : the script will write an output file that contains a row for each time a vehicle couldn't find a site near enough. Every row contains the edge id of the edge the vehicle was on, the position of the vehicle in longitude and latitude and a counter for the edge that represents the number of times a vehicle that couldn't find a cell site, was on that edge. The resulting file does not contain duplicated row (so if it happens multiple times that some vehicles in the same positions couldn't find a site, only one row will be saved). It requires two input files, the first one should have the associations between vehicles and sites, while the second one should contain the positions of every vehicle at every step. The former has to use commas as separators while the latter has to use semicolon. The suggested files to use are the output file from the second script and the output file produced by sumo using the **--fcd-output** option. Remember to convert the second file into a csv file using the tool **xml2csv.py**.
