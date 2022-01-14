# Name   : literature_data_extraction.py
# Author : Laura Prieto Saavedra (Adpated from Catherine Radburn and Audrey Collard-Daigneault)
# Date   : 22-06-2021
# Desc   : This code plots simulation data from Lethe and other data from literature.
#           It loads .csv files and plot data into a .png file. Displaying the title is optional.
#           If all x_value and data_type available are required, ignore x_value and data_type in lines 46 and 49, and
#           make all_data = True.
#           On line 350, a tolerance is specified. This may need to be varied if too little/too much data is plotted.

import pandas
import numpy
from matplotlib import pyplot as plt
import matplotlib.ticker as ticker
import matplotlib.patches as patches
from matplotlib.patches import ConnectionPatch
from pathlib import Path
import time
# import tikzplotlib

start_time = time.time()

########################################################################################################################
# SET VARIABLES

# Reynolds number of the simulation (Currently available for Re = 5600 only)
Re = 5600

# Path to folder where Lethe simulation data is stored
path_to_lethe_data = "../output_csv/baseline/"

#Filename
file_names_lethe_data = ["0.1_1M_600s", "0.1_1M_700s", "0.1_1M_800s", "0.1_1M_900s", "0.1_1M_1000s", "0.1_1M_1100s", "0.1_1M_1200s"]

# Label for Lethe data for the legend
# NOTE : make sure the number of labels are the same that the number of files names of lethe data
labels = ["Lethe - 600s", "Lethe - 700s", "Lethe - 800s", "Lethe - 900s","Lethe baseline - 1000s", "Lethe - 1100s", "Lethe - 1200s"]

# Information about the literature data
path_to_literature_data = "../output_csv/literature/"

# Save graph.png 
folder_to_save_png = "../output_png/baseline_averaging/"
Path(folder_to_save_png).mkdir(parents=True, exist_ok=True)

# x/h position: Set x_value to be equal to 0.05, 0.5, 1, 2, 3, 4, 5, 6, 7 or 8
# x_value = 4
x_value = 6

# data type options: Set data_type to be equal to "average_velocity_0", "average_velocity_1", "reynolds_normal_stress_0"
# "reynolds_normal_stress_1", "reynolds_shear_stress_uv", "reynolds_normal_stress_2" or "turbulent_kinetic_energy"
# data_type = "reynolds_shear_stress_uv"
data_type = "average_velocity_0"

# Extract and generate graphs for all x_values and data_types? (True or False)
all_data = False

# Display the title on the output graphs? (True or False)
display_title = False

# Zoom in?
zoom_in_plots = True

########################################################################################################################
# Function to retrieve data from .csv files
def obtain_data(x_value, path_to_literature_data, path_to_lethe_data, file_names_lethe_data, data_type):

    # Read data and append to list
    Rapp2009_csv = path_to_literature_data + '_Rapp2009' + str(data_type) + '_x_' + str(x_value) + '.csv'
    Rapp2009_data = pandas.read_csv(Rapp2009_csv)
    Rapp2009_data = Rapp2009_data.to_numpy()
    Rapp2009_data = numpy.delete(Rapp2009_data, 0, 1)
    
    Breuer2009_csv = path_to_literature_data + '_Breuer2009' + str(data_type) + '_x_' + str(x_value) + '.csv'
    Breuer2009_data = pandas.read_csv(Breuer2009_csv)
    Breuer2009_data = Breuer2009_data.to_numpy()
    Breuer2009_data = numpy.delete(Breuer2009_data, 0, 1)   

    Lethe_data=list()
    for file in file_names_lethe_data:
        Lethe_data_csv = path_to_lethe_data + '_Lethe_data_' + str(file) + '_' + str(data_type) + '_x_' + str(x_value) + '.csv'
        Lethe_data_loc = pandas.read_csv(Lethe_data_csv)
        Lethe_data_loc = Lethe_data_loc.to_numpy()
        Lethe_data_loc = numpy.delete(Lethe_data_loc, 0, 1)
        Lethe_data.extend(Lethe_data_loc)

    return Breuer2009_data, Rapp2009_data, Lethe_data

# Plot literature values against Lethe values
def plot_to_png(Breuer2009_data, Rapp2009_data, lethe_data, data_type, x_value, labels,
                folder_to_save_png, show_title):
    # Plotting results
    plt.rcParams['text.usetex'] = True
    plt.rcParams['font.family']='DejaVu Serif'
    plt.rcParams['font.serif']='cm'
    plt.rcParams['font.size'] = 10

    if zoom_in_plots is True:
        fig = plt.figure()
        ax = fig.add_subplot(2,7,(1,11), zorder = 0)
        ax2 = fig.add_subplot(2,7,(6,7)) #(6,14) for Reynolds
        ax3 = fig.add_subplot(2,7,(13,14))  
    else:
        fig, ax = plt.subplots()

    # Colours for graphs
    # colors = ["xkcd:blue", "xkcd:lime green", "xkcd:pink", "xkcd:bluish purple", "xkcd:crimson", "xkcd:pumpkin", "xkcd:gold"] 
    colors = ["xkcd:blue", "xkcd:lime green", "xkcd:red", "xkcd:orange", "xkcd:crimson", "xkcd:purple", "xkcd:gold"]       
    index = 0
    chunk = 0

    # Set display axis titles
    if data_type == "average_velocity_0":
        x_axis_label = "$u/u_b$"
    elif data_type == "average_velocity_1":
        x_axis_label = "$v/u_b$"
    elif data_type == "reynolds_normal_stress_0":
        x_axis_label = "$u'u'/u_b^2$"
    elif data_type == "reynolds_normal_stress_1":
        x_axis_label = "$v'v'/u_b^2$"
    elif data_type == "reynolds_shear_stress_uv":
        x_axis_label = "$u'v'/u_b^2$"
    elif data_type == "reynolds_normal_stress_2":
        x_axis_label = "$w'w'/u_b^2$"
    elif data_type == "turbulent_kinetic_energy":
        x_axis_label = "$k/u_b^2$"
    else:
        x_axis_label = None

    # Plot Lethe data
    for file_name in file_names_lethe_data:
        if file_name is not None:
            if lethe_data != []:
                ax.plot(lethe_data[chunk], lethe_data[chunk+1], '--', label=labels[index] , color=colors[index], linewidth = 1.2, zorder = 3, mfc = 'none') 
                if zoom_in_plots is True:
                    ax2.plot(lethe_data[chunk], lethe_data[chunk+1], '--', color=colors[index], linewidth = 1.2, zorder = 3, mfc = 'none') 
                    ax3.plot(lethe_data[chunk], lethe_data[chunk+1], '--', color=colors[index], linewidth = 1.2, zorder = 2, mfc = 'none') 

                index = index + 1
                chunk = chunk + 2

    # Plot Breuer data
    if Breuer2009_data != []:
        ax.plot(Breuer2009_data[0], Breuer2009_data[1], ':', color="k", linewidth = 1.2,
                label='LESOCC - Breuer 2009', zorder = 2)
        if zoom_in_plots is True:
            ax2.plot(Breuer2009_data[0], Breuer2009_data[1], ':', color="k", linewidth = 1.2,
                    zorder = 2)
            ax3.plot(Breuer2009_data[0], Breuer2009_data[1], ':', color="k", linewidth = 1.2,
                    zorder = 1)

    # Plot Rapp data
    if Rapp2009_data != []:
        ax.plot(Rapp2009_data[0], Rapp2009_data[1], '-', color="k", linewidth = 1.2,
                label = 'Experimental - Rapp 2009',zorder = 1)
        if zoom_in_plots is True:
            ax2.plot(Rapp2009_data[0], Rapp2009_data[1], '-', color="k", linewidth = 1.2,
                    zorder = 1)
            ax3.plot(Rapp2009_data[0], Rapp2009_data[1], '-', color="k", linewidth = 1.2,
                    zorder = 0)                

    # Only display title if specified
    if show_title is True:
        if data_type == "average_velocity_0":
            title = "Average x velocity $u$"
        elif data_type == "average_velocity_1":
            title = "Average y velocity $v$"
        elif data_type == "reynolds_normal_stress_0":
            title = "Reynolds normal stress $u'u'$"
        elif data_type == "reynolds_normal_stress_1":
            title = "Reynolds normal stress $v'v'$"
        elif data_type == "reynolds_shear_stress_uv":
            title = "Reynolds shear stress $u'v'$"
        elif data_type == "reynolds_normal_stress_2":
            title = "Reynolds normal stress $w'w'$"
        elif data_type == "turbulent_kinetic_energy":
            title = "Turbulent kinetic energy $k$"
        else:
            title = None

        ax.set_title(title + " at Re = " + str(Re) + " at x = " + str(x_value))

    ax.set_xlabel(x_axis_label)
    ax.set_ylabel("$y/h$")
    fig.subplots_adjust(bottom=0.3)
    ax.set_facecolor('white')
    ax.spines['bottom'].set_color('black')
    ax.spines['top'].set_color('black')
    ax.spines['right'].set_color('black')
    ax.spines['left'].set_color('black')
    ax.xaxis.set_major_locator(ticker.MultipleLocator(0.5)) #0.01 for Reynolds and 0.5 for velocity
    ax.yaxis.set_major_locator(ticker.MultipleLocator(0.5))

    if zoom_in_plots is True:
        ax.legend(loc='lower center', bbox_to_anchor=(0.9, -0.5), facecolor = 'white', framealpha = 0.75, ncol=3, edgecolor = 'black', fancybox = False, shadow = False)

        #1st. Zoom in upper right
        x1 = 0.8; x2 = 1.1; y1 = 2.3; y2 = 3 #for average velocity x = 6
        # x1 = -0.04; x2 = -0.025; y1 = 0.5; y2 = 1.2 #for reynolds shear stress uv at x=4
        ax2.set_xbound(x1, x2)
        ax2.set_ybound(y1, y2)
        ax2.xaxis.set_major_locator(ticker.MultipleLocator(0.2)) #0.01 for Reynolds 0.2 for velocity
        ax2.yaxis.set_major_locator(ticker.MultipleLocator(0.4))

        ax.add_patch(patches.Rectangle((x1,y1),(x2-x1),(y2-y1),linewidth=0.5, edgecolor='gray', facecolor = 'none'))
        # ax2_1 = ConnectionPatch(xyA=(1,2), coordsA=ax.transData, xyB=(0.8,2.4), coordsB=ax2.transData, color = 'gray',linewidth=0.5, arrowstyle ="->")
        ax2_1 = ConnectionPatch(xyA=(x2, y2 - (y2-y1)/2), coordsA=ax.transData, xyB=(x1, y1 + (y2-y1)/2), coordsB=ax2.transData, color = 'gray',linewidth=0.5, arrowstyle ="->", zorder = 1)
        fig.add_artist(ax2_1)

        #2nd. Zoom in bottom right
        x1 = 0.1; x2 = 0.4; y1 = 0; y2 = 0.7 #for average velocity
        # x1 = 0; x2 = 0.7; y1 = 0.7; y2 = 1.4 #for reynolds normal stress
        ax3.set_xbound(x1, x2)
        ax3.set_ybound(y1, y2)
        ax3.xaxis.set_major_locator(ticker.MultipleLocator(0.2))
        ax3.yaxis.set_major_locator(ticker.MultipleLocator(0.4))

        ax.add_patch(patches.Rectangle((x1,y1),(x2-x1),(y2-y1),linewidth=0.5, edgecolor='gray', facecolor = 'none'))
        ax3_1 = ConnectionPatch(xyA=(x2, y1 + (y2-y1)/2), coordsA=ax.transData, xyB=(x1, y1 + (y2-y1)/2), coordsB=ax3.transData, color = 'gray',linewidth=0.5, arrowstyle ="->", zorder = 1)
        fig.add_artist(ax3_1)


    else:
        ax.legend(loc='lower center', bbox_to_anchor=(0.5, -0.5), facecolor = 'white', framealpha = 0.75, ncol=3, edgecolor = 'black', fancybox = False, shadow = False)

    ax.set_aspect(1.0/ax.get_data_ratio(), adjustable='box') 
    ax2.set_aspect(1.0/ax2.get_data_ratio(), adjustable='box')    
   
    plt.tight_layout()
    # plt.show()
    if zoom_in_plots is True:
        fig.savefig(
            folder_to_save_png + "graph_" + data_type + "_x_" + str(x_value) + "_with_zoom_in.png",
            dpi=600)
    else:
        fig.savefig(
            folder_to_save_png + "graph_" + data_type + "_x_" + str(x_value) + ".png",
            dpi=600)
    plt.close(fig)
    if zoom_in_plots is True:
        ax.clear()
        ax2.clear()
        # ax3.clear()

########################################################################################################################
# RUN FUNCTIONS

# Verify the number of labels is right
assert len(labels) == len(file_names_lethe_data), f"It seems to have {len(file_names_lethe_data)} Lethe data files and you gave " \
                            f"{len(labels)} labels, please verify your labels names."

# Collect all data types at each x_value
if all_data is True:
    # data_type_available = ["average_velocity_0", "average_velocity_1", "reynolds_normal_stress_0",
                        #    "reynolds_normal_stress_1", "reynolds_shear_stress_uv", "reynolds_normal_stress_2"]   # turbulent_kinetic_energy
    # x_available = [0.05, 0.5, 1, 2, 3, 4, 5, 6, 7, 8]
    data_type_available = ["average_velocity_0","reynolds_normal_stress_0", "reynolds_shear_stress_uv"]
    x_available = [0.5, 2, 4, 6]

    for x in x_available:
        for flow_property in data_type_available:
            [Breuer2009_data, Rapp2009_data, lethe_data] = obtain_data(x, path_to_literature_data, path_to_lethe_data, file_names_lethe_data, flow_property)
            plot_to_png(Breuer2009_data, Rapp2009_data, lethe_data, flow_property, x, labels, folder_to_save_png, display_title)

# Collect a specified x_value and data_type
else:
    [Breuer2009_data, Rapp2009_data, lethe_data] = obtain_data(x_value, path_to_literature_data, path_to_lethe_data, file_names_lethe_data, data_type)
    # PLOT RESULTS
    plot_to_png(Breuer2009_data, Rapp2009_data, lethe_data, data_type, x_value, labels, folder_to_save_png, display_title)

print("--- %s seconds ---" % (time.time() - start_time))

