import libsumo
import os
import sys
import random
import pandas
import argparse
from pathlib import Path
import time

def new_cell_site(poi_pos, veh_coord, max_dist):
    """ 
    Computes the new site for a vehicle.

    The function iterates over every site and computes the distance to the vehicle.
    The nearest one is chosen.

    Parameters
    ----------
    poi_pos : dict
        A dictionary that maps a site id to a tuple with the coordinates of its 
        position.
    veh_coord : tuple
        Coordinates with the current vehicle position.
    max_dist : float
        The maximum allowed distance between the vehicle and the site.

    Returns
    -------
    string
        The new site's id or 'None' if no cell site is near enough.
    """

    new_site = (None,float('inf'))

    for id, poi_coord in poi_pos.items():
        dist = libsumo.simulation.getDistance2D(poi_coord[0], poi_coord[1], 
                                                veh_coord[0], veh_coord[1])
        if dist < new_site[1]:
            new_site = (id, dist)
    
    return new_site[0] if new_site[1] <= max_dist else None

def check_connection(poi_coord, veh_coord, dist):
    """ Checks whether the distance between a vehicle and a site is greater 
    than the parameter 'dist'.

    Parameters
    ----------
    poi_coord : tuple
        The site's coordinates.
    veh_coord : tuple
        The vehicle's coordinates.
    dist : float
        The distance in meters between the vehicle and the tower to check.

    Returns
    -------
    bool
        True if distance is greater than the specified parameter, False otherwise.
    """

    return libsumo.simulation.getDistance2D(poi_coord[0], poi_coord[1], 
                                            veh_coord[0], veh_coord[1]) > dist

def write_positions(vehicles, step, file_path):
    """ Writes on a file the current connections between vehicles and cell sites.

    Parameters
    ----------
    vehicles : dict
        Dictionary that maps every vehicle's id to its site.
    step : int
        The current step of the simulation.
    file_name : string
        The file path to the output file.
    """

    situation = [{'Step': step, 'Id_vehicle': veh_id, 'Id_site': cell_site} 
                 for veh_id, cell_site in vehicles.items()]
    df = pandas.DataFrame(situation)
    df.to_csv(file_path, mode='a', index=False, header=False)
    
def main():

    parser = argparse.ArgumentParser(description="file that maps every vehicle "
                                     "of the simulation to a cell site of the "
                                     "input file and writes the association into "
                                     "a file.")
    parser.add_argument('-c', '--cell_sites', type=int, help="the number of cell "
                        "sites to generate. If a sites file is supplied, this "
                        "parameter is ignored.")
    parser.add_argument('-t', '--time', type=int, default=86400, help="duration "
                        "of the simulation in seconds (max 86400). The default "
                        "value is the maximum value.")
    parser.add_argument('-s', '--step', type=int, default=180, help="Number of "
                        "steps between every vehicle-site distance check. "
                        "The default value is 180")
    parser.add_argument('-d', '--distance', type=int, default=2000, help="maximum "
                        "allowed distance in meters between a site and a vehicle. "
                        "The default value is 2000.")
    parser.add_argument('-i', '--input', help="path to the input sites file.")
    parser.add_argument('-o', '--output', default="output_vehicles_sites.csv", 
                        help="path for the output file.")
    parser.add_argument('-su', '--sumo_cfg', required=True, help="path to the "
                        "sumo configuration file of the simulation to execute.")
    parser.add_argument('-n', '--sumo_net', help="path to the sumo net file of "
                        "the simulation. It must be provided if the input sites "
                        "file is set.")
    args = parser.parse_args()

    # we need to import python modules from the $SUMO_HOME/tools directory
    # If the the environment variable SUMO_HOME is not set, try to locate 
    # the python modules relative to this script. We also need to set the
    # environment variable PROJ_LIB
    if 'SUMO_HOME' in os.environ:
        tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
        sys.path.append(tools)
        os.environ['PROJ_LIB']  = os.path.join(os.environ['SUMO_HOME'], 'share/proj')
    else:
        sys.exit("Please declare environment variable 'SUMO_HOME'")

    from sumolib import checkBinary, net
    poi_pos = {}
    vehicles = {}
    sumoBinary = checkBinary('sumo')
    # checks the output file path and creates missing directories
    output_path = Path(args.output)
    output_path.parent.mkdir(exist_ok=True, parents=True)
    df = pandas.DataFrame(list(), columns = ['step', 'vehicle_id', 'site_id'])
    df.to_csv(args.output, mode='w', index=False)
    libsumo.start([sumoBinary, "-c", args.sumo_cfg,])
    red = (255, 0, 0) # color assigned to the sites

    if args.input:
        if args.sumo_net is None:
            raise TypeError("You need to provide the sumo net file")
        sites = pandas.read_csv(args.input)
        net = net.readNet(args.sumo_net)
        for row in sites.itertuples():
            # the first value is the row index, so it is ignored
            x, y =  net.convertLonLat2XY(row[3], row[2])
            libsumo.poi.add(str(row[1]), x, y, red)
    elif args.cell_sites:
        x_y_min, x_y_max = libsumo.simulation.getNetBoundary()
        x_max, y_max = int(x_y_max[0]), int(x_y_max[1])
        x_min, y_min = int(x_y_min[0]), int(x_y_min[1])
        csv_name = 'output_sites_pos.csv'
        sites_pos = pandas.DataFrame(list(), columns = ['site_id', 'x', 'y'])
        sites_pos.to_csv(csv_name, mode='w', index=False)
        # adds sites in random positions
        for i in range(args.cell_sites):
            x = random.randint(x_min, x_max)
            y = random.randint(y_min, y_max)
            libsumo.poi.add(str(i), x, y, red)
            site_pos = pandas.DataFrame([{'site_id': str(i), 'x': x, 'y': y}])
            print(site_pos)
            site_pos.to_csv(csv_name, mode='a', index=False, header=False)
    else:
        raise TypeError("You need to provide at least one argument between the "
                        "input sites file and the number of sites to generate")        

    poi_pos = {poi_id:libsumo.poi.getPosition(poi_id) for poi_id in libsumo.poi.getIDList()}
    start = time.perf_counter()
    for step in range(args.time+1):
        check = True if step % args.step == 0 else False
        libsumo.simulationStep()

        # deletes arrived vehicles
        for veh_id in libsumo.simulation.getArrivedIDList():
            try:
                del vehicles[veh_id]
            except:
                print("Error during the removal of the arrived vehicles")

        # deletes teleported vehicles outside the simulation because they were 
        # idle for too long
        for veh_id in libsumo.simulation.getEndingTeleportIDList():
            try:
                del vehicles[veh_id]
            except:
                print("Error during the removal of the teleported vehicles")

        # subscribes new vehicles to register their position
        for veh_id in libsumo.simulation.getDepartedIDList():
            libsumo.vehicle.subscribe(veh_id, [libsumo.constants.VAR_POSITION])
        
        # retrieves the vehicles' positions
        for key, value in libsumo.vehicle.getAllSubscriptionResults().items():
            coordinates_veh = value[libsumo.constants.VAR_POSITION]
            poi_id = vehicles.get(key, None)

            # assigns a new site to a vehicle only if it entered the simulation 
            # in this step or the steps indicated by 'args.step' have passed and
            # its distance from the current site is greater than the number indicated
            # by the variable 'args.distance'
            if not poi_id or (check and check_connection(poi_pos[poi_id], 
                                                         coordinates_veh, args.distance)):
                vehicles[key] = new_cell_site(poi_pos, coordinates_veh, args.distance)

        if check:
            write_positions(vehicles, step, args.output)
    print(f"Tempo: {time.perf_counter() - start}")
    libsumo.close()

if __name__ == '__main__':
    main()