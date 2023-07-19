import pandas
import argparse
from pathlib import Path

def extraction(input_path, output_file, city_name):
    """ Extracts cell sites of a city from an input file and writes them into
    a new file. 

    Parameters
    ----------
    input_file : string
        Input file path.
    output_file : string
        Output file path.
    city_name : string
        City name to filter the sites.
    """
    
    df = pandas.read_csv(input_path, sep=";")

    # filters the dataframe to keep only the sites of the specified city
    turin_cells = df[df['site_name'].str.contains(city_name, na=False)]

    # filters the cells to keep only one per site
    cell_sites = turin_cells.drop_duplicates(subset=['node_id'])

    # eliminate every column that won't be needed for the simulation
    cell_sites = cell_sites[['node_id', 'site_lat', 'site_long', 'site_name']]

    cell_sites.to_csv(output_file, mode='w',  index=False)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="file that extracts from an "
                                    "input file the cell sites of a certain" 
                                    "city and writes to a new file the node id, "
                                    " latitude, longitude and site name.")
    parser.add_argument('-i', '--input', required=True, help="the file path "
                        "from which the sites will be extracted.")
    parser.add_argument('-o', '--output', default='output_sites.csv', help="the file path "
                        "on which the extracted sites will be written.")
    parser.add_argument('-c', '--city', required=True, help="the city name to filter the input file.")
    args = parser.parse_args()

    # checks the output file path and creates missing directories
    output_path = Path(args.output)
    output_path.parent.mkdir(exist_ok=True, parents=True)

    extraction(args.input, args.output, args.city)