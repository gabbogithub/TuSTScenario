# Overview
In this directory there are two python scripts written to be used with a sumo simulation and a csv file that contains cells associated to cell phone towers. 
One extracts cell sites located inside a certain city and writes them to a new file, while the other maps a cell site to every vehicle in the simulation
and regurarly checks that the distance doesn't exceed a value given by the user. If it happens, a new association is computed.

# Requirements
To execute the scripts, aside from a sumo and python installations, there are some python libraries that have to be installed. A pip file is provided to quickly
install all the libraries.
What follows is a list of the requirements:
- **Sumo** : the scripts were tested with versions that go from **1.16.0** to **1.18.0**.
- **Python** : the version used is **3.11.3** but older versions may work.
- **Pandas** : It is used to analyze csv and create new ones. Version **2.0.3** was used but other version will probably work as well.
- **Libsumo** : It is used to execute the simulation and modify it. Version from **1.16.0** to **1.18.0** were tested and used.
- **Pyproj** : It is used to convert coordinates from latitude and longitude to x and y values of the simulation. Version **3.6.0** was used.

# How to
Both scripts have a variety of options that can be listes with the command **--help**. Some are required while others are optional.

## Extraction script
In order to use it you have to specify the path to the input file with the **-i** or **--input** option and the name of the city to filter the cell sites 
with the option **-c** or **--city**. This script was written to be used with Lte Italy csv files but could theoretically work with every csv files that
have at least four columns with the following names: node_id (to uniquely identify sites), cell_lat (latitude of the site), cell_long (longitude of the site) 
and site_name (column that has to contain the name of the city).

## Association script
In order to use it you have to specify the path to the sumo simulation configuration file with the option **-su** or **--sumo_cfg** and either a number of sites
to generate with the option **-c** or **--cell_sites** or csv sites file with the option **-i** or **--input** and in this case you'll also have to provide the path
to the net file of the simulation with the option **-n** or **--sumo_net** (because it is used to convert from latitude and longitude to x and y values of the 
simulation). This script works every csv file that follows this structure: first column *node_id of the site*, second column *site latitude* and third column *site
longitude*.
