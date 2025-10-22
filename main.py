#Import modules
import math
import random

#Declare constants
MIN_LAT = -90
MAX_LAT = 90
MIN_LONG = -180
MAX_LONG = 180

RADIANS_CONVERTER = math.pi/180
EARTH_RADIUS = 6378

STORM_STEPS = 5
STORM_DECREMENT = 1

PROBABILITY_WAVE_IMPACT = 0.2
NULL = 0
WAYPOINT_SUCCESS_RADIUS = 10

#Calibrate to Compass: Degrees to Radians
def degrees_to_radians(degrees):
    """
    Converts degrees to radians utilizing RADIANS_CONVERTER.
    
    Parameters:
        degrees: Angle in degrees (float)
    Returns:
        radians: Angle in radians rounded to 2 decimals (float)
    Examples:
        >>> degrees_to_radians(1/2)
        0.01
        
        >>> degrees_to_radians(160)
        2.79
        
        >>> degrees_to_radians(90)
        1.57
    """
    radians = round(degrees * RADIANS_CONVERTER, 2)
    return radians

#Acquire a Fix: Validate a Coordinate
def get_valid_coordinate(val_name, min_float, max_float):
    """
    The function will ask the user for a float value and as long as the value
    is not within the range (min_float, max_float) it will keep asking the
    user for a value. The message displayed is adapted depending on the value
    of val_name.
    
    Parameters:
        val_name: Name of the coordinate(str)
        min_float: Minimum value (float)
        max_float: Maximum value (float)
    Returns:
        val_name: Validated coordinate (float)
    Examples:
        >>> get_valid_coordinate('latitude',60,90)
        What is your latitude ?50
        Invalid latitude
        What is your latitude ?70
        70.0
        
        >>> get_valid_coordinate('x-coordinate',-50,50)
        What is your x-coordinate ?-60
        Invalid x-coordinate
        What is your x-coordinate ?10
        10.0
        
        >>> get_valid_coordinate('longitude',0,80)
        What is your longitude ?50
        50.0
    """
    val_name_value = float(input("What is your " + val_name + " ?"))
    while val_name_value <= min_float or val_name_value >= max_float:
        print("Invalid " + val_name)
        val_name_value = float(input("What is your " + val_name + " ?"))
        
    return val_name_value

#Plot Our Position: Get GPS Location
def get_gps_location():
    """
    The function will call the previous function get_valid_coordinate to get
    the latitude and longitude values of the vessel. It returns the vessel's
    coordinates (floats).
    
    Parameters:
        None
    Returns:
        latitude, longitude: Validated latitude and longitude (floats)
    Examples:
        >>> get_gps_location()
        What is your latitude ?90
        Invalid latitude
        What is your latitude ?50
        What is your longitude ?70
        (50.0, 70.0)
        
        >>> get_gps_location()
        What is your latitude ?80
        What is your longitude ?85
        (80.0, 85.0)
        
        >>> get_gps_location()
        What is your latitude ?-90
        Invalid latitude
        What is your latitude ?80
        What is your longitude ?-200
        Invalid longitude
        What is your longitude ?20
        (80.0, 20.0) 
    """
    latitude = get_valid_coordinate('latitude', MIN_LAT, MAX_LAT)
    longitude = get_valid_coordinate('longitude', MIN_LONG, MAX_LONG)
    
    return latitude, longitude

#Chart the Distance: Great-circle Calculator using Haversine Formula
def distance_two_points(latitude_1, longitude_1, latitude_2, longitude_2):
    """
    The function takes four float inputs, converts them to radians and
    computes the distance between the locations based on the Haversine
    formula.
    
    Parameters:
        latitude_1, longitude_1: Coordinates of the first point (float)
        latitude_2, longitude_2: Coordinates of the second point (float)
    Returns:
        distance: Distance between the two points in km rounded to 2 decimals
    Examples:
        >>> distance_two_points(55.51,-80.6789,20.678,-80.567)
        3890.58
       
        >>> distance_two_points(78.90724,-89.3689,78.90724,-89.3689)
        0.0
       
        >>> distance_two_points(65.4890,-90.3459,89.0878,-30.4595)
        2683.93
    """
    radians_latitude_1 = degrees_to_radians(latitude_1)
    radians_longitude_1 = degrees_to_radians(longitude_1)
    radians_latitude_2 = degrees_to_radians(latitude_2)
    radians_longitude_2 = degrees_to_radians(longitude_2)
    
    #Solve for a
    delta_lat = radians_latitude_1 - radians_latitude_2
    delta_long = radians_longitude_1 - radians_longitude_2
    
    a = (math.sin(delta_lat / 2) ** 2 + math.cos(radians_latitude_1) *
         math.cos(radians_latitude_2) *
         math.sin(delta_long / 2) ** 2)
    
    #Solve for c
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    
    #Solve for distance
    distance = round(EARTH_RADIUS * c, 2)
    
    return distance

#Helm Nudge: Apply Wave Impact to a Coordinate
def apply_wave_impact(orig_position, min_float, max_float):
    """
    Selects a random number between -1 and 1 and checks that when we add this
    new random number to the original position, the new position remains
    within the (min_float, max_float), otherwise continues selecting new
    random numbers until the number lies inside the interval.
    
    Parameters:
        orig_position: Original coordinate (float)
        min_float, max_float: Valid bounds (float)
    
    Returns:
        new_position: New coordinate after wave impact (float) rounded to
        two decimals
        
    Examples:
        >>> apply_wave_impact(0,-4,4)
        0.92
        
        >>> apply_wave_impact(0,-4,4)
        -0.93
        
        >>> apply_wave_impact(0,-4,4)
        -0.77
    """
    random_number = random.random() * 2 - 1
    new_position = orig_position + random_number
    while new_position <= min_float or new_position >= max_float:
        random_number = random.random() * 2 - 1
        new_position = orig_position + random_number
        
    return round(new_position, 2)

#Wave Hit Event: Reorient and Recheck
def wave_hit_vessel(vessel_lat, vessel_long):
    """
    Updates its input values by calling apply_wave_impact twice, each time
    with MIN_LAT/MAX_LAT and MIN_LONG/MAX_LONG.
    
    Parameters:
        vessel_lat, vessel_long = Current vessel coordinates (floats)
    Returns:
        vessel_lat, vessel_long = New coordinates after wave impact
    Examples:
        >>> wave_hit_vessel(89.9,-17)
        (89.22, -16.3)
        
        >>> wave_hit_vessel(20,-89)
        (20.21, -88.72)
        
        >>> wave_hit_vessel(69.9,-70)
        (70.67, -69.54)
    """
    vessel_lat = apply_wave_impact(vessel_lat, MIN_LAT, MAX_LAT)
    vessel_long = apply_wave_impact(vessel_long, MIN_LONG, MAX_LONG)
    
    return vessel_lat, vessel_long

#Helm Advance: Move Toward Waypoint
def move_toward_waypoint(current_lat, current_long,
                         waypoint_lat, waypoint_long):
    """
    The function moves the vessel a single step toward the waypoint and after
    the move, the latitude and longitude must lie within the closed intervals
    [MIN_LAT, MAX_LAT] and [MIN_LONG, MAX_LONG]. If a boundary surpassed, set
    it to that boundary value.
    
    Parameters:
         current_lat, current_long: Current vessel coordinates (float)
         waypoint_lat, waypoint_long: Target waypoint coordinates (float)
    Returns:
        new_lat, new_long = New coordinates rounded to two decimals (float)
    Examples:
        >>> move_toward_waypoint(20,30,60,80)
        (47.7, 64.62)
        
        >>> move_toward_waypoint(30,50,70,90)
        (67.18, 87.18)
        
        >>> move_toward_waypoint(10,30,50,70)
        (40.56, 60.56)
    """
    scale = random.random() + 1
    
    new_lat = current_lat + (waypoint_lat - current_lat) / scale
    
    new_long = current_long + (waypoint_long - current_long) / scale
    
    #Restrictions
    if new_lat < MIN_LAT:
        new_lat = MIN_LAT
    elif new_lat > MAX_LAT:
        new_lat = MAX_LAT
        
    if new_long < MIN_LONG:
        new_long = MIN_LONG
    elif new_long > MAX_LONG:
        new_long = MAX_LONG
        
    new_lat = round(new_lat, 2)
    new_long = round(new_long, 2)
    
    return new_lat, new_long

#Bridge Console: Storm Run to Waypoint
def vessel_menu():
    """
    The function displays a welcome message and a bridge menu that lets the
    captain set a waypoint, move toward it while reporting status, or exit.
    The console runs as an interactive loop that repeatedly shows the menu,
    handles the captain's choice, and continues until the mission succeeds,
    fails because of the storm, or the captain exits.
    
    Parameters:
        None
    
    Returns:
        None
    """
    
    #Setting a boolean variable to keep displaying the menu
    restart = True
    
    #Tracks whether a waypoint has been set
    #If no waypoint set
    waypoint_set = False
    
    storm_countdown = STORM_STEPS
    
    print("Welcome to the boat menu!")
    
    current_lat, current_long = get_gps_location()
    
    while restart:
        
        #Menu displayed
        print("Please select an option below:")
        print("1) Set waypoint")
        print("2) Move toward waypoint and Status report")
        print("3) Exit boat menu")
        option_chosen = input("Choose: ")
        
        if option_chosen == '1':
            #Get waypoint coordinates
            print("Enter waypoint coordinates.")
            waypoint_lat, waypoint_long = get_gps_location()
            print("Waypoint set to latitude of " + str(waypoint_lat) + " and"\
                  " longitude of " + str(waypoint_long))
            waypoint_set = True
        elif option_chosen == '2':
            
            #No waypoint set
            if waypoint_set == False:
                print("No waypoint set.")
            else:
                #Acquire new coordinates after moving
                new_lat, new_long = move_toward_waypoint(current_lat,
                                                     current_long,
                                                     waypoint_lat,
                                                     waypoint_long)
                print("Captain Log: Journeyed towards waypoint.")
                
                #Wave impact probability
                if random.random() < PROBABILITY_WAVE_IMPACT:
                    print("Captain Log: Wave impact recorded.")
                    
                    #Get new coordinates after wave impact
                    new_lat, new_long = wave_hit_vessel(new_lat, new_long)
                    
                #Update current position for next loop
                current_lat, current_long = new_lat, new_long
                
                #Acquire distance between the two points
                distance_to_waypoint = distance_two_points(new_lat, new_long,
                                                           waypoint_lat,
                                                           waypoint_long)
                #Report status
                print("Current position is latitude of " + str(new_lat) +
                      " and longitude of " + str(new_long))
                print("Distance to waypoint: " + str(distance_to_waypoint) +
                      " km")
                
                if distance_to_waypoint <= WAYPOINT_SUCCESS_RADIUS:
                    print("Mission success: waypoint reached before storm.")
                    #Exit the loop and end the simulation
                    restart = False  
                else:
                    storm_countdown -= STORM_DECREMENT
                    print("Storm T-minus: " + str(storm_countdown))
                    
                    if storm_countdown == NULL:
                        print("Mission failed: storm hit before arrival.")
                        #Exit the loop and end the simulation
                        restart = False

        else:
            print("Console closed by captain")
            #Exit the loop and end the simulation
            restart = False
