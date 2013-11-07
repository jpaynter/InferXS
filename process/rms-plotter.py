'''This file plots the RMS errors for all target values vs batches.

   Author: William Boyd
   Date: 11/6/2013

   Usage: python rms-plotter.py

   NOTE: This file must be run after first running target-rms.py

   This file extracts the root-means squared errors for each assembly, energy
   group and tally from data/target-rms.h5 and generates plots for each case.
'''

import matplotlib.pyplot as plt
import h5py as h5
import numpy as np
import os


# Create HDF5 file handle for each assembly's RMS error
rms_file = h5.File('../data/target-batch-rms.h5', 'r')

# The target mesh dimensions
x = 17
y = 17

# The number of energy groups (1 - high energy, 2 - low energy)
groups = 2

# Types of fuel assemblies
assemblies = ['Fuel-1.6wo-CRD', \
              'Fuel-2.4wo-16BA-grid-56', \
              'Fuel-3.1wo-instr-16BA-grid-17']

# The type of OpenMC tallies
tallies = ['Flux', 'Tot. RXN Rate', 'Abs. RXN Rate', 'Fiss. RXN Rate', \
           'NuFiss. RXN Rate', 'Tot. XS', 'Abs. XS', 'Fiss. XS', 'NuFiss. XS']

# The energy levels for the tallies
energies = ['Low Energy', 'High Energy']

# The batches of interest 10, 20, ..., 1000
batches = rms_file['Batches'][...] - 250

# Loop over assembly types
for assembly in assemblies:

    print 'Generating plots for ' + assembly

    # Loop over tally types
    for tally in tallies:

        print '    ' + tally

        # Create a plot figure handle
        fig = plt.figure()

        # Loop over energies and add RMS data for each energy to the plot
        for energy in energies:
            plt.semilogy(batches, rms_file[assembly][energy][tally][...], \
                         linewidth=2)

        # Annotate the plot
        plt.ylabel('Root Mean Squared Error')
        plt.xlabel('Batch #')
        plt.title(assembly + ' ' + tally + ' RMS')
        plt.legend(energies)
        plt.grid(b=True, which='major', color='b', linestyle='-')
        plt.grid(b=True, which='minor', color='r', linestyle='--')

        # Save the plot
        filename = tally.replace('.', '').replace(' ', '-').lower()
        filename = 'rms-plots/' + assembly + '/' + filename + '.png'
        plt.savefig(filename)

# Close the HDF5 file
rms_file.close()

            
