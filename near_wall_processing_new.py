# Name   : near_wall_processing.py
# Author : Catherine Radburn
# Date   : 11-05-2021
# Desc   : This code finds the reattachment point from Lethe, and evaluates and plots y+ across the length.
#           The near-wall region of data is extracted from Lethe. The reattachment point is found at the wall-nearest
#           point as the x-value where the average x-direction velocity is zero. y+ is calculated from the gradient of
#	        the average x velocity in the y direction, giving the wall shear stress.
#           Note that this code only applies if alpha = 1 (i.e. no stretching of geometry)

import pandas
import numpy
import itertools
from matplotlib import pyplot as plt
from pathlib import Path
import time
start_time = time.time()

########################################################################################################################
# SET VARIABLES

# Reynolds number and kinematic viscosity of the simulation (Currently available for Re = 5600 only)
Re = 5600
set_try = 0

# Label for Lethe data for the legend
# NOTE : make sure the number of labels are the same that the number of files names of lethe data
if Re == 5600 and set_try == 0:
    viscosity = 1.78571E-04 
    # file_names_lethe_data = ["0.025_120K_800s_5600_q2q2", "0.025_250K_800s_5600", "0.025_500K_800s_5600", "0.025_1M_800s_5600", "0.025_4M_800s_5600", "0.025_8M_800s_5600" ]
    file_names_lethe_data = ["0.025_250K_800s_5600", "0.025_1M_800s_5600", "0.025_4M_800s_5600"]
    # labels = ["Lethe - 120K", "Lethe - 250K", "Lethe - 500K", "Lethe - 1M", "Lethe - 4M", "Lethe - 8M"]
    labels = ["Lethe - 250K", "Lethe - 1M", "Lethe - 4M"]
elif Re == 10600:
    viscosity = 9.43396E-05 
    file_names_lethe_data = ["0.025_120k_800s_10600", "0.025_250k_800s_10600", "0.025_500K_800s_10600"]
    labels = ["Lethe - 120K", "Lethe - 250K", "Lethe - 500K"]
elif Re == 37000:
    viscosity = 2.7027E-05 
    file_names_lethe_data = ["0.025_120k_800s_37000", "0.025_250k_800s_37000", "0.025_500K_800s_37000"]
    labels = ["Lethe - 120K", "Lethe - 250K", "Lethe - 500K"]
elif Re == 5600 and set_try == 1:
    viscosity = 1.78571E-04 
    file_names_lethe_data = ["0.1_1M_1000s_old_baseline"]
    labels = ["Lethe - 1M"]
elif Re == 5600 and set_try == 2:
    viscosity = 1.78571E-04 
    file_names_lethe_data = ["0.0125_4M_1000s_5600", "0.025_4M_1000s_5600", "0.05_4M_1000s_5600", "0.1_4M_1000s_5600" ]
    labels = ["0.0125 - 4M - 1000s", "0.025 - 4M - 1000s", "0.05 - 4M - 1000s", "0.1 - 4M - 1000s"]
elif Re == 5600 and set_try == 3:
    viscosity = 1.78571E-04 
    file_names_lethe_data = ["0.1_250K_1000s_5600", "0.1_1M_1000s_old_baseline", "0.1_4M_1000s_5600" ]
    labels = ["0.1 - 250k - 1000s", "0.1 - 1M - 1000s", "0.1 - 4M - 1000s"]
# Information about the Lethe data
path_to_lethe_data = "./lethe_data/"


# Save graph.png and data.csv
folder_to_save_png = "./mesh_requirements/"
Path(folder_to_save_png).mkdir(parents=True, exist_ok=True)

folder_to_save_csv = "./near_wall/"
Path(folder_to_save_csv).mkdir(parents=True, exist_ok=True)

# Display the title on the output graphs? (True or False)
display_title = False

########################################################################################################################

# Lethe data extraction of files associated with x/h
def lethe_data_extraction(path_to_lethe_data, file_names_lethe_data, Re):
    assert Re == 5600 or Re == 10600 or Re == 37000, "Currently available for Re = 5600, 10600, 37000 only."

    # Set index
    index = 1
    extracted_lethe_data = []

    # For each Lethe file present
    for file_name in file_names_lethe_data:
        lethe_csv = path_to_lethe_data + file_name + ".csv"
        # Iterates through lethe_csv file
        iter_csv = pandas.read_csv(lethe_csv, usecols=["Points_0", "Points_1", "average_velocity_0",
                                                       "reynolds_shear_stress_uv"], sep=",", iterator=True,
                                                        chunksize=1000)
        # Saves required columns in range [0, 1.1] to Pandas dataframe lethe_data_range (up to y=1.2 for hills)
        lethe_lower_wall_data = pandas.concat(
            [chunk[(chunk["Points_1"] > 0) & (chunk["Points_1"] < 9)] for chunk in iter_csv])

        # Sort dataframe by x value
        lethe_lower_wall_data.sort_values(by=['Points_0'])

        # Convert Pandas dataframe into numpy array
        lethe_lower_wall_array = lethe_lower_wall_data.to_numpy()

        # Output
        print("Lethe data " + str(index) + " extracted")
        extracted_lethe_data.append(lethe_lower_wall_array)
        index += 1

    return extracted_lethe_data

# Function to find reattachment point for each Lethe file
def reattachment(extracted_lethe_data, labels):

    index = 1
    for i in range(len(extracted_lethe_data)):
        # Extract numpy array for each Lethe data file
        data_array = extracted_lethe_data[i]
        # Remove shear stress column
        wall_array = numpy.delete(data_array, 3, 1)

        # New array where x > 3.5 and x < 5.2
        focussed_wall_array = []
        for j in range(numpy.shape(wall_array)[0]):
            if wall_array[j,0] > 3.5 and wall_array[j,0] < 5.2:
                focussed_wall_array.append(wall_array[j,:])

        focussed_wall_array = numpy.asarray(focussed_wall_array)

        # For each value of x, average in z and find the wall-nearest point
        # For each unique value of x "k"
        wall_nearest_points = []
        for k in numpy.unique(focussed_wall_array[:,0]):
            # initialise y_nearest variable
            y_nearest = None
            averaging_data = []

            # Each index "k" where the unique value of x appears
            for m in numpy.where(focussed_wall_array == k)[0]:
                # Find the minimum value of y at each value of x
                # If y_nearest does not exist, initialise it
                if y_nearest is None:
                    y_nearest = numpy.array([focussed_wall_array[m, :]])
                    averaging_data.append(y_nearest)
                else:
                    # if focussed_wall_array y value is smaller than y_nearest, replace and reintiialise averaging_data
                    if focussed_wall_array[m,1] < y_nearest[0,1] and wall_array[m, 2] != 0:
                        y_nearest = numpy.array([focussed_wall_array[m, :]])
                        averaging_data = [y_nearest]
                    elif focussed_wall_array[m,1] == y_nearest[0,1] and wall_array[m, 2] != 0:
                        averaging_data.append(numpy.array([focussed_wall_array[m, :]]))

            # Average data
            averaging_data = numpy.asarray(averaging_data)
            averaging_data = numpy.squeeze(averaging_data)
            average = numpy.sum(averaging_data[:,2]) / numpy.shape(averaging_data)[0]
            wall_point = [averaging_data[0,0], averaging_data[0,1], average]

            # Append y_nearest to wall_nearest_points
            wall_nearest_points.append(wall_point)

        # Convert to array
        wall_nearest_points = numpy.asarray(wall_nearest_points)

        # Find where u values change sign (first instance of u>0)
        upper_index = numpy.argmax(wall_nearest_points[:, 2] > 0, axis=0)
        u_upper = wall_nearest_points[upper_index, 2]
        u_lower = wall_nearest_points[upper_index-1, 2]
        x_upper = wall_nearest_points[upper_index, 0]
        x_lower = wall_nearest_points[upper_index-1, 0]

        # Interpolate to find reattachment point
        int_fraction = (-u_lower)/(u_upper-u_lower)
        reattachment_point = (int_fraction)*(x_upper-x_lower) + x_lower

        # Print result
        print("The reattachment point of " + labels[i] + " is x/h = " + str(reattachment_point))
        index += 1

    return

def y_plus(extracted_lethe_data, viscosity, folder_to_save_csv):

    index = 1
    extracted_y_plus = []

    for i in range(len(extracted_lethe_data)):
        # Extract numpy array for each Lethe data file
        data_array = extracted_lethe_data[i]
        wall_array = data_array[data_array[:, 0].argsort()]

        # For each value of x, find the wall-nearest point
        # For each unique value of x "k"
        wall_nearest_points = []
        for k in numpy.unique(wall_array[:,0]):
            # initialise y_nearest variable
            y_nearest = numpy.array([[1000000, 1000000, 1000000, 1000000]])
            averaging_data = []

            # Each index "k" where the unique value of x appears
            for m in numpy.where(wall_array == k)[0]:
                # Find the minimum value of y at each value of x
                # if wall_array y value is smaller than y_nearest, replace
                if wall_array[m,1] < y_nearest[0,1] and wall_array[m, 2] != 0.0:
                    y_nearest = numpy.array([wall_array[m, :]])
                    averaging_data = [y_nearest]
                elif wall_array[m, 1] == y_nearest[0, 1] and wall_array[m, 2] != 0.0:
                    averaging_data.append(numpy.array([wall_array[m, :]]))

            # Average data
            averaging_data = numpy.asarray(averaging_data)
            averaging_data = numpy.squeeze(averaging_data)
            average_u = numpy.sum(averaging_data[:, 2]) / numpy.shape(averaging_data)[0]
            average_uv = numpy.sum(averaging_data[:, 3]) / numpy.shape(averaging_data)[0]
            wall_point = [averaging_data[0, 0], averaging_data[0, 1], average_u, average_uv]

            # Double check if there are double entries
            for i in range(len(wall_nearest_points)):
                if wall_nearest_points[i][0] == wall_point[0]:
                    # Check y
                    if wall_nearest_points[i][1] > wall_point[1]:
                        print("Repeated entry for x = " + str(wall_point[0]))
                        wall_nearest_points[i] = wall_point
            
            wall_nearest_points.append(wall_point)
            

        # Convert to array
        wall_nearest_points = numpy.asarray(wall_nearest_points)
        wall_nearest_points = wall_nearest_points[wall_nearest_points[:, 0].argsort()]

        # Initialise output list
        y_plus_data = []

        # Calculate y+ at each x value
        for m in range(numpy.shape(wall_nearest_points)[0]):
            x = wall_nearest_points[m,0]
            y1 = wall_nearest_points[m,1]

            # Scale to h=28
            x = 28*x

            # Determine y value of wall (y0) from geometry
            # First hill
            if x < 9:
                y0 = min(2.800000000000E+01, 2.800000000000E+01 + (0.000000000000E+00 * x) + (6.775070969851E-03 * (x ** 2)) - (2.124527775800E-03 * (x ** 3)))
            elif 9 <= x < 14:
                y0 = 2.507355893131E+01 + (9.754803562315E-01 * x) - (1.016116352781E-01 * (x ** 2)) + (1.889794677828E-03 * (x ** 3))
            elif 14 <= x < 20:
                y0 = 2.579601052357E+01 + (+8.206693007457E-01 * x) - (9.055370274339E-02 * (x ** 2)) + (1.626510569859E-03 * (x ** 3))
            elif 20 <= x < 30:
                y0 = 4.046435022819E+01 - (1.379581654948E+00 * x) + (1.945884504128E-02 * (x ** 2)) - (2.070318932190E-04 * (x ** 3))
            elif 30 <= x < 40:
                y0 = 1.792461334664E+01 + (8.743920332081E-01 * x) - (5.567361123058E-02 * (x ** 2)) + (6.277731764683E-04 * (x ** 3))
            elif 40 <= x < 54:
                y0 = max(0, (5.639011190988E+01 - (2.010520359035E+00 * x) + (1.644919857549E-02 * (x ** 2)) + (2.674976141766E-05 * (x ** 3))))

            # Second hill
            elif 198 <= x < 212:
                y0 = max(0, (5.639011190988E+01 - (2.010520359035E+00 * (252-x)) + (1.644919857549E-02 * ((252-x) ** 2)) + (2.674976141766E-05 * ((252-x) ** 3))))
            elif 212 <= x < 222:
                y0 = 1.792461334664E+01 + (8.743920332081E-01 * (252-x)) - (5.567361123058E-02 * ((252-x) ** 2)) + (6.277731764683E-04 * ((252-x) ** 3))
            elif 222 <= x < 232:
                y0 = 4.046435022819E+01 - (1.379581654948E+00 * (252-x)) + (1.945884504128E-02 * ((252-x) ** 2)) - (2.070318932190E-04 * ((252-x) ** 3))
            elif 232 <= x < 238:
                y0 = 2.579601052357E+01 + (+8.206693007457E-01 * (252-x)) - (9.055370274339E-02 * ((252-x) ** 2)) + (1.626510569859E-03 * ((252-x) ** 3))
            elif 238 <= x < 243:
                y0 = 2.507355893131E+01 + (9.754803562315E-01 * (252-x)) - (1.016116352781E-01 * ((252-x) ** 2)) + (1.889794677828E-03 * ((252-x) ** 3))
            elif x >= 243:
                y0 = min(2.800000000000E+01, 2.800000000000E+01 + (0.000000000000E+00 * (252-x)) + (6.775070969851E-03 * ((252-x) ** 2)) - (2.124527775800E-03 * ((252-x) ** 3)))

            else:
                y0 = 0

            # Rescale for h=1
            y0 = y0/28
            x = x/28

            assert y0 < y1, "The point on the wall y0 must have a lower y-value than the point immediately above the wall y1"

            y_cc = (y1 - y0)/2
            viscous_stress = viscosity * ((wall_nearest_points[m, 2]) / (y1 - y0))
            re_stress = wall_nearest_points[m, 3]
            tau = viscous_stress
            y_plus = (y_cc*numpy.sqrt(abs(tau)))/(viscosity)
            
            y_plus_data.append([x, y_plus])

        y_plus_data = numpy.asarray(y_plus_data)

        # Additional y+ data extraction
        y_plus_max = numpy.amax(y_plus_data[:, 1])
        print("The maximum value of y+ in " + str(file_names_lethe_data[index - 1]) + " is " + str(y_plus_max))

        y_plus_average = numpy.sum(y_plus_data[:, 1]) / numpy.shape(y_plus_data)[0]
        print("The average value of y+ in " + str(file_names_lethe_data[index - 1]) + " is " + str(y_plus_average))

        # Output
        print("y+ values of Lethe data " + str(index) + " extracted")
        extracted_y_plus.append(y_plus_data)

        # Write output arrays to .csv files
        # pandas.DataFrame(y_plus_data).to_csv(folder_to_save_csv + '_Lethe_' + str(file_names_lethe_data[index-1]) + '_y_plus.csv')

        index += 1

    return extracted_y_plus

# Plot of y+ values
def plot_y_plus(folder_to_save_png, extracted_y_plus, labels, Re, title):
    # Plotting results
    plt.rcParams['text.usetex'] = True
    plt.rcParams['font.family']='DejaVu Serif'
    plt.rcParams['font.serif']='cm'
    plt.rcParams['font.size'] = 14

    # Plotting results
    fig, ax = plt.subplots()

    # Colours for graphs
    # colors = ["xkcd:blue", "xkcd:lime green", "xkcd:red", "xkcd:orange", "xkcd:crimson", "xkcd:purple", "xkcd:gold"]      
    colors = ["xkcd:lime green", "xkcd:orange", "xkcd:crimson", "xkcd:purple", "xkcd:gold"]       
 
    index = 0

    # Plot y_plus values
    for file_name in extracted_y_plus:
        if file_name is not None:
            ax.plot(file_name[:,0], file_name[:,1], '-', label=labels[index], color=colors[index])
            index += 1

    if title is True:
        ax.set_title("Re = " + str(Re))

    ax.set_xlabel("$x/h$")
    ax.set_ylabel("$\Delta y^+$")
    ax.set_facecolor('white')
    ax.spines['bottom'].set_color('black')
    ax.spines['top'].set_color('black')
    ax.spines['right'].set_color('black')
    ax.spines['left'].set_color('black')
    plt.tight_layout()
    fig.set_size_inches(6,4)
    fig.subplots_adjust(right=0.65)
    ax.set_xlim([0,9])
    # ax.set_ylim([0,6])

    ax.legend(loc='right', bbox_to_anchor=(1.65, 0.5), facecolor = 'white', framealpha = 0.75, ncol=1, edgecolor = 'black', fancybox = False, shadow = False)

    fig.savefig(
        folder_to_save_png + "graph_y_plus_" + str(Re) + "_new.eps" ,
        dpi=600)
    plt.show()
    # plt.close(fig)
    ax.clear()

########################################################################################################################
# RUN FUNCTIONS

# Verify the number of labels is right
assert len(labels) == len(file_names_lethe_data), f"It seems to have {len(file_names_lethe_data)} Lethe data files and you gave " \
                            f"{len(labels)} labels, please verify your labels names."

# Collect required data types from near wall region
lethe_data = lethe_data_extraction(path_to_lethe_data, file_names_lethe_data, Re)
# reattachment(lethe_data, labels)
y_plus_data = y_plus(lethe_data, viscosity, folder_to_save_csv)
plot_y_plus(folder_to_save_png, y_plus_data, labels, Re, display_title)

print("--- %s seconds ---" % (time.time() - start_time))
