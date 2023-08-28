import argparse
import pandas
from pathlib import Path
import libsumo

def number_users(input_path, output_path):
    """ Extracts the number of vehicles associated with every site at every simulation 
    step and then writes the results into a new csv file. Number '0' will be used 
    as a special site id to indicate the number of vehicles that were not associated 
    with a site during that timestamp.

    Parameters
    ----------
    input_path : string
        The path to the input file to analyse.
    output_path : string
        The path to the output file where the results will be written.
    """

    # only load the necessary columns to reduce the memory usage
    col_list = ['step', 'site_id']

    # the manual dtype assignment is necessary to make pandas write the sites' id
    # correctly into the output file because otherwise they are written with an
    # ending '.0' like float numbers
    col_type = {'site_id': float}
    df_in = pandas.read_csv(input_path, usecols=col_list, dtype=col_type)
    df_in = df_in.fillna(0)
    df_in['site_id'] = df_in['site_id'].astype(int)

    df_out = df_in.value_counts().reset_index()
    df_out = df_out.sort_values(by=['step', 'count'])
    df_out.rename(columns={'step': 'timestamp', 'count': 'number_vehicles'}, 
                      inplace=True)
    df_out.to_csv(output_path, mode='w', index=False)

def route_time(input_path, output_path):
    """ Extracts for every vehicle the length of the path it followed in meters 
    and the time it rimaned in the simulation in seconds.

    Parameters
    ----------
    input_path : string
        The path to the input file to analyse.
    output_path : string
        The path to the output file where the results will be written.
    """

    # only load the necessary columns to reduce the memory usage
    col_list = ['vehicle_arrival', 'vehicle_depart', 'vehicle_id', 'vehicle_routeLength']
    col_type = {'vehicle_arrival': float, 'vehicle_depart': float, 'vehicle_id': str, 'vehicle_routeLength': float}
    df_in = pandas.read_csv(input_path, usecols=col_list, dtype=col_type, sep=';')
    df_in = df_in.fillna(0)
    df_in['simulation_stay'] = df_in['vehicle_arrival'] - df_in['vehicle_depart']
    df_out = df_in.drop(columns=['vehicle_arrival', 'vehicle_depart'])
    df_out.to_csv(output_path, mode='w', index=False)

def unique_sites(input_path, output_path):
    """ Extracts for every vehicle the number of unique sites that were associated 
    with them during their stay in the simulation.

    Parameters
    ----------
    input_path : string
        The path to the input file to analyse.
    output_path : string
        The path to the output file where the results will be written.
    """

    # only load the necessary columns to reduce the memory usage
    col_list = ['vehicle_id', 'site_id']
    df_in = pandas.read_csv(input_path, usecols=col_list)
    df_out = df_in.dropna()
    df_out = df_out.drop_duplicates()
    series_out = df_out['vehicle_id'].value_counts()
    series_out.to_csv(output_path)

def num_changes(input_path, output_path):
    """ Extracts for every vehicle the number of times their association with a 
    cell site changed. A change is also counted if a vehicle goes from being
    associated to a site to not being associated with any site (because all the 
    sites were too distant).

    Parameters
    ----------
    input_path : string
        The path to the input file to analyse.
    output_path : string
        The path to the output file where the results will be written.
    """

    # only load the necessary columns to reduce the memory usage.
    col_list = ['vehicle_id', 'site_id']
    df_in = pandas.read_csv(input_path, usecols=col_list)

    # special site id '0' to identify vehicles that were not associated with any site.
    df_in = df_in.fillna('0')

    # dictionary that will associate to every vehicle id a tuple with the current 
    # site id and a counter with the number of site changes.
    changes = {}

    # iterates over the rows of the csv and checks if the site associated with 
    # a vehicle changed and updates its counter.
    for row in df_in.itertuples():
        vehicle_counter = changes.get(row[1], ('0', 0))
        if vehicle_counter[0] != row[2]:
            changes[row[1]] = (row[2], vehicle_counter[1]+1)
    
    # output dataframe creation
    changes_counter = [{'vehicle_id': veh_id, 'count': association[1]} 
                 for veh_id, association in changes.items()]
    df = pandas.DataFrame(changes_counter)
    df = df.sort_values(by=['count'], ascending=False)
    df.to_csv(output_path, mode='w', index=False)

def new_sites(association_path, edges_path, output_path):
    """ Extracts the edge id of the edges where vehicles were located when 
    they couldn't find a cell site near enough. The function also associates 
    to every edge id the number of times vehicles that couldn't find a cell
    were on that edge. Finally the exact positions in latitude and longitude 
    of the vehicles are added to the two previous columns (one row for every 
    different position).

    Parameters
    ----------
    association_path : string
        The path to the csv file with the associations between vehicles and sites.
    edges_path : string
        The path to the csv file with the position of every vehicle.
    output_path : string
        The path to the output file where the results will be written.
    """

    df_ass = pandas.read_csv(association_path)

    # extracts the vehicles that couldn't find a site that was near enough.
    # The site id is represented as Nan.
    df_nan = df_ass[df_ass['site_id'].isna()]
    df_nan = df_nan.drop_duplicates(subset=['vehicle_id'])
    df_edges = pandas.read_csv(edges_path, sep=';')

    # merges with a join the sites associations with the position of the vehicle 
    # at the correct step when it couldn't find a site.
    df_merge = pandas.merge(df_nan, df_edges, left_on=['step', 'vehicle_id'], right_on=['timestep_time', 'vehicle_id'])
    
    # counts the number of times an edge is present in the csv to find the most 
    # used ones and then use that number to sort the rows
    df_counts = df_merge['vehicle_edge'].value_counts().reset_index()

    # merges the count of every edge with all the values of the previous dataframe
    df_final = pandas.merge(df_merge, df_counts, on=['vehicle_edge'])

    # keeps only the column that will be written to the csv and also drops rows 
    # that are duplicates.
    df_final = df_final.drop(labels=['step', 'site_id', 'timestep_time', 'vehicle_id'], axis=1)
    df_final = df_final.drop_duplicates()
    df_final = df_final.sort_values(by=['count'], ascending=False)
    df_final.to_csv(output_path, mode='w', index=False)

def main():
    """ Handles the command line arguments and according to the specified option, 
    calls the correct analysis function with the input and output files' paths 
    provided.
    """

    parser = argparse.ArgumentParser(description="file that produces some types "
                                     "of analysis based on the results of a sumo "
                                     "simulation")
    parser.add_argument('-i', '--input', required=True, nargs='+', help="the files' paths "
                        "that will be used for the analysis.")
    parser.add_argument('-o', '--output', default='output_analysis.csv', 
                        help="the file path on which the analysis will be written.")
    parser.add_argument('-us', '--users', action='store_true', help="analyses "
                        "the number of users associated with a cell site at every "
                        "timestamp. It requires an input file with the associations" 
                        " between vehicles and cell sites that uses commas as separators.")
    parser.add_argument('-rt', '--route_time', action='store_true', help="analyses "
                        "the length of the route followed by every vehicle (in meters) "
                        "and the time the vehicle remained in the simulation "
                        "(in seconds). It requires an input file with the route "
                        "length, the depart and arrival times. The separator has "
                        "to be a semicolon.")
    parser.add_argument('-si', '--unique_sites', action='store_true', help="analyses "
                        "the number of unique sites associated to the vehicles. "
                        "It requires an input file with the associations between "
                        "vehicles and cell sites that uses commas as separators.")
    parser.add_argument('-nc', '--number_changes', action='store_true', help="analyses "
                        "the number of times a vehicle changed site (including "
                        "when an association can't be made because there aren't "
                        "sites near enough). It requires an input file with the "
                        "associations between vehicles and cell sites that uses "
                        "commas as separators.")
    parser.add_argument('-ns', '--new_sites', action='store_true', help="analyses "
                        "for every vehicle that couldn't connect to a site, the "
                        "edge that it was on and its position (in longitude and "
                        "latitude). For every edge it also counts the number of "
                        "times a vehicle that was on it, couldn't find an association. "
                        "It requires two input files, the first with the associations "
                        "between vehicles and sites, while the second one must "
                        "contain the position of every vehicle at every step. "
                        "The former has to use commas as separators while the "
                        "latter has to use semicolon.")
    args = parser.parse_args()

    # checks the output file path and creates missing directories
    output_path = Path(args.output)
    output_path.parent.mkdir(exist_ok=True, parents=True)

    if args.users:
        number_users(args.input[0], args.output)
    elif args.route_time:
        route_time(args.input[0], args.output)
    elif args.unique_sites:
        unique_sites(args.input[0], args.output)
    elif args.number_changes:
        num_changes(args.input[0], args.output)
    elif args.new_sites:
        new_sites(args.input[0], args.input[1], args.output)

if __name__ == '__main__':
    main()