# Name   : plot_data_with_geometry_baseline.py
# Author : Laura Prieto (adapted from Catherine Radburn and Audrey Collard-Daigneault)
# Date   : 05-07-2021
# Desc   : This code plots those following data type (u/u_b, v/u_b, u'u'/u_b², v'v'/u_b², u'v'/u_b²) of
#          generated Lethe data csv files (with the post_processing_new.py code) with the experimental data of Rapp 2009
#          and the computational data of Breuer 2009.
#           If all x_value and data_type available are required, ignore data_type and scale_factor in lines 40 and 45, and
#           make all_data = True.

import pandas
import numpy
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import matplotlib.patches as patches
from matplotlib.patches import ConnectionPatch
from pathlib import Path
from scipy import interpolate
from scipy.interpolate import interp1d
import time
start_time = time.time()

################################################ FILL OUT THIS PART ###################################################

# Reynolds number of the simulation
Re = 5600

# Path to .csv file (same as post_processing_new.py)
path_to_lethe_data = "../output_csv/all_data/"
path_to_literature_data = "../output_csv/literature/"+ str(Re) + "/"

# Path and name to save graphs
path_to_save = "../statistics/"

Path(path_to_save).mkdir(parents=True, exist_ok=True)

# Label for Lethe data for the legend (should be the same as used in post_processing_new.py)
# NOTE : make sure the number of labels are the same that the number of Lethe simulation data in csv files and
#        and associated to the right data set
# labels = ["Lethe baseline 250K", "Lethe baseline 1M"]
# labels = ["Lethe baseline 1M"]
# labels = ["Lethe - 250K", "Lethe - 500K", "Lethe - 1M", "Lethe - 4M", "Lethe - 8M"]
labels = ["Lethe 8M"]
# File names of lethe data
# file_names_lethe_data = ["0.1_250K_1000s_5600", "0.1_1M_1000s_old_baseline"]
# file_names_lethe_data = ["0.1_1M_1000s_old_baseline"]
# file_names_lethe_data = ["0.025_250K_800s_5600", "0.025_500K_800s_5600", "0.025_1M_800s_5600", "0.025_4M_800s_5600", "0.025_8M_800s_5600"] 
file_names_lethe_data = ["0.025_8M_800s_5600"]

# data_type_available = ["average_velocity_0", "average_velocity_1", "reynolds_normal_stress_0",
#                            "reynolds_normal_stress_1", "reynolds_shear_stress_uv"]
data_type = "reynolds_normal_stress_0"

# Scale factor for the curves
# Suggestions : 0.8 for average_velocity_0, 3 for average_velocity_1, 5 for reynolds_normal_stress_0,
#               15 for reynolds_normal_stress_1, and 10 for reynolds_shear_stress
scale_factor = 5

# Extract and generate graphs for all x_values and data_types? (True or False)
all_data = False

########################################################################################################################
# Function to retrieve data from .csv files
def obtain_data(x_available, path_to_lethe_data, file_names_lethe_data, data_type, path_to_literature_data):
    all_x_data = []
    for x_value in x_available:
        data = []

        # Read data and append to list
        Rapp2009_csv = path_to_literature_data + '_Rapp2009' + str(data_type) + '_x_' + str(x_value) + '.csv'
        Rapp2009_data = pandas.read_csv(Rapp2009_csv)
        Rapp2009_data = Rapp2009_data.to_numpy()
        data.append(Rapp2009_data)

        if Re == 5600 or Re == 10600:
            Breuer2009_csv = path_to_literature_data + '_Breuer2009' + str(data_type) + '_x_' + str(x_value) + '.csv'
            Breuer2009_data = pandas.read_csv(Breuer2009_csv)
            Breuer2009_data = Breuer2009_data.to_numpy()
            data.append(Breuer2009_data)

        for file in file_names_lethe_data:
            Lethe_data_csv = path_to_lethe_data + '_Lethe_data_' + str(file) + '_' + str(data_type) + '_x_' + str(x_value) + '.csv'
            Lethe_data = pandas.read_csv(Lethe_data_csv)
            Lethe_data = Lethe_data.to_numpy()
            data.append(Lethe_data)

        # Create list containing lists of data at all x available
        all_x_data.append(data)
    return all_x_data

# Function to plot data at all x
def calculate_statistics(x_available, Re, all_x_data, folder_to_save, scale_factor,
                       lethe_labels, x_label, data_type):
    
    # This loop extracts only the data corresponding to one of the xvalue 0.05, 0.5. etc 
    for i, x_value in enumerate(x_available):
        data_x = all_x_data[i]
        all_x_data_type = []
        all_y_values = []

        # This loop extracts the specific dataset (j=0 is Rapp, j=1 is Breuer and j=2+ Lethe) and it organizes them in one array
        for j, dataset in enumerate(data_x):
            if j == 0: #Data is from Rapp
               dataset[0, :] = (scale_factor * dataset[0, :]) + x_value
               dataset = numpy.delete(dataset, 0, 1)
               all_x_data_type.append(dataset[0,:])
               all_y_values.append(dataset[1,:])
            elif j == 1 and Re != 37000: #Data is from Breuer
               dataset[0, :] = (scale_factor * dataset[0, :]) + x_value
               dataset = numpy.delete(dataset, 0, 1)
               all_x_data_type.append(dataset[0,:])
               all_y_values.append(dataset[1,:]) 
            else: #Data is from lethe
               dataset[0, :] = (scale_factor * dataset[0, :]) + x_value
               dataset = numpy.delete(dataset, 0, 1)
               all_x_data_type.append(dataset[0,:])
               all_y_values.append(dataset[1,:])

        # print(len(data_x))
        
        for j in range(2,len(data_x)):
            print('-----------------------------------------')
            print('Lethe data:', lethe_labels[j-2])

            # Interpolate first lethe data to be able to compare to experimental and numerical benchmarks, and other lethe simulations
            x = all_x_data_type[j]
            y = all_y_values[j]
            f = interp1d(y,x, kind = 'cubic')
            # fig, ax = plt.subplots()
            # ax.plot(all_x_data_type[0], all_y_values[0], label="Experimental")
            # ax.plot(f(all_y_values[0]), all_y_values[0], label="Interpolated Lethe")
            # ax. plot(x, y, label="Lethe")
            # plt.legend()
            # plt.show()
            diff_exp_lethe = abs(all_x_data_type[0] - f(all_y_values[0]))
            max_diff_exp_lethe = max(diff_exp_lethe)*100
            index_max_exp = max(range(len(diff_exp_lethe)), key=diff_exp_lethe.__getitem__)
            average_exp_lethe = (sum(diff_exp_lethe)/len(diff_exp_lethe))*100
            l2_norm_exp_lethe = (sum(diff_exp_lethe**2))**(0.5)

            diff_breuer_lethe = abs(all_x_data_type[1] - f(all_y_values[1]))
            max_diff_breuer_lethe = max(diff_breuer_lethe)*100
            index_max_breuer = max(range(len(diff_breuer_lethe)), key=diff_breuer_lethe.__getitem__)
            average_breuer_lethe = (sum(diff_breuer_lethe)/len(diff_breuer_lethe))*100
            l2_norm_breuer_lethe = (sum(diff_breuer_lethe**2))**(0.5)

            print(lethe_labels[j-2], 'x value =', x_value, 'Rapp-Lethe:', "{:.2f}".format(max_diff_exp_lethe),'% @ y/h=', "{:.2f}".format(all_y_values[0][index_max_exp]), 'Breuer-Lethe:', "{:.2f}".format(max_diff_breuer_lethe) ,'% @ y/h=', "{:.2f}".format(all_y_values[1][index_max_breuer]))
            print(lethe_labels[j-2], 'x value =', x_value, 'Rapp-Lethe average:', "{:.2f}".format(average_exp_lethe), 'Breuer-Lethe average:', "{:.2f}".format(average_breuer_lethe))
            print(lethe_labels[j-2], 'x value =', x_value, 'Rapp-Lethe l2 norm:', "{:.2f}".format(l2_norm_exp_lethe), 'Breuer-Lethe l2 norm:', "{:.2f}".format(l2_norm_breuer_lethe))

            # print('For x value:', x_value)
            # print('-----------------------------------------')
            # print('Difference between Lethe and experimental')
            # for i, diff in enumerate(diff_exp_lethe):
            #     if diff > 0.048:  #0.0776: #0.048
            #         print("Difference bigger than the mesh size! Difference of: ", diff ,"at y" ,all_y_values[0][i])
            
            # print('-----------------------------------------')
            # print('Difference between Lethe and Breuer')
            # for i, diff in enumerate(diff_breuer_lethe):
            #     if diff > 0.048:
            #         print("Difference bigger than the mesh size! at", all_y_values[1][i])

            # print(lethe_labels[j-2], 'x value =', x_value, 'Rapp-Lethe difference:', "{:.2f}".format(diff_exp_lethe), 'Breuer-Lethe differnece:', "{:.2f}".format(diff_breuer_lethe))
    return 0

########################################################################################################################
# Call functions

x_available = [0.05, 0.5, 1, 2, 3, 4, 5, 6, 7, 8]
# x_available = [0.5]

# Set x_label
# data_type_available = ["average_velocity_0", "average_velocity_1", "reynolds_normal_stress_0",
#                             "reynolds_normal_stress_1", "reynolds_shear_stress_uv"]
data_type_available = ["average_velocity_0", "reynolds_normal_stress_0", "reynolds_shear_stress_uv"]

# x_labels_available = ["$u/u_b$", "$v/u_b$", "$u'u'/u_b^2$", "$v'v'/u_b^2$", "$u'v'/u_b^2$"]
x_labels_available = ["$u/u_b$", "$u'u'/u_b^2$", "$u'v'/u_b^2$"]

# Plot all data profiles
if all_data is True:
    scale_available = [0.8, 5, 10]

    # Cycle through all data types
    for data in data_type_available:
        print("Data type: " + data)
        x_label = x_labels_available[data_type_available.index(data)]
        scale = scale_available[data_type_available.index(data)]

        data_at_all_x = obtain_data(x_available, path_to_lethe_data, file_names_lethe_data, data, path_to_literature_data)
        calculate_statistics(x_available, Re, data_at_all_x, path_to_save, scale,
                        labels, x_label, data)

# Plot specify profiles        
else:
    x_label = x_labels_available[data_type_available.index(data_type)]

    data_at_all_x = obtain_data(x_available, path_to_lethe_data, file_names_lethe_data, data_type, path_to_literature_data)
    calculate_statistics(x_available, Re, data_at_all_x, path_to_save, scale_factor,
                    labels, x_label, data_type)

print("--- %s seconds ---" % (time.time() - start_time))
