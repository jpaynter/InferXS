'''Computes the root-mean squared errors for all batch-wise target values.

   Author: William Boyd
   Date: 11/6/2013

   Usage: python target-batch-rms.py

   This file computes the root-mean squared errors for all batch-wise target
   values, including tallies in each energy group for each assembly. All of
   the RMS errors are stored in HDF5 to 'data/target-rms.h5'.
'''

from statepoint import StatePoint
import matplotlib.pyplot as plt
import h5py as h5
import numpy as np
import os

# Create HDF5 file handle for each assembly's RMS error
rms_file = h5.File('../data/target-batch-rms.h5', 'w')

# The target mesh dimensions
x = 17
y = 17

# The number of energy groups (1 - high energy, 2 - low energy)
groups = 2

# Types of fuel assemblies
assemblies = ['Fuel-1.6wo-CRD', \
              'Fuel-2.4wo-16BA-grid-56', \
              'Fuel-3.1wo-instr-16BA-grid-17']

# The energy levels for the tallies
energies = ['Low Energy', 'High Energy']

# Batch numbers of interest - 260 to 1240 in increments of 10
batches = np.linspace(260,1240,99)
rms_file.create_dataset('Batches', data=batches)

# Loop over each assembly type
for assembly in assemblies:

    print 'Exporting ' + assembly

    # Create a group in the HDF5 file for this assembly
    assembly_group = rms_file.create_group(assembly)

    # Read in the converged tally results for this assembly
    directory = '../openmc-input/' + assembly + '/pinwise/'
    filename = 'statepoint.1250.h5'
    conv_sp = StatePoint(directory + filename)
    conv_sp.read_results()

    # Extract 2D numpy arrays of the batch means for each type of tally
    conv_flux = conv_sp.extract_results(1, 'flux')['mean']
    conv_tot_rxn_rate = conv_sp.extract_results(1, 'total')['mean']
    conv_abs_rxn_rate = conv_sp.extract_results(1, 'absorption')['mean']
    conv_fiss_rxn_rate = conv_sp.extract_results(1, 'fission')['mean']
    conv_nufiss_rxn_rate = conv_sp.extract_results(1, 'nu-fission')['mean']

    # Reshape to grid with energy group as third index
    conv_flux = np.reshape(conv_flux, (x, y, groups))
    conv_tot_rxn_rate = np.reshape(conv_tot_rxn_rate, (x, y, groups))
    conv_abs_rxn_rate = np.reshape(conv_abs_rxn_rate, (x, y, groups))
    conv_fiss_rxn_rate = np.reshape(conv_fiss_rxn_rate, (x, y, groups))
    conv_nufiss_rxn_rate = np.reshape(conv_nufiss_rxn_rate, (x, y, groups))

    # Compute group cross-sections for both energy groups
    conv_tot_xs = np.nan_to_num(conv_tot_rxn_rate / conv_flux)
    conv_abs_xs = np.nan_to_num(conv_abs_rxn_rate / conv_flux)
    conv_fiss_xs = np.nan_to_num(conv_fiss_rxn_rate / conv_flux)
    conv_nufiss_xs = np.nan_to_num(conv_nufiss_rxn_rate / conv_flux)

    # Loop over energies (0 - low energy index, 1 - high energy index)
    for energy in enumerate(energies):

        flux_rms = np.zeros(len(batches))
        tot_rxn_rate_rms = np.zeros(len(batches))
        abs_rxn_rate_rms = np.zeros(len(batches))
        fiss_rxn_rate_rms = np.zeros(len(batches))
        nufiss_rxn_rate_rms = np.zeros(len(batches))
        tot_xs_rms = np.zeros(len(batches))
        abs_xs_rms = np.zeros(len(batches))
        fiss_xs_rms = np.zeros(len(batches))
        nufiss_xs_rms = np.zeros(len(batches))

        energy_group = assembly_group.create_group(energy[1])

        # Loop over each batch
        for batch in enumerate(batches):

            print '    Batch-' + str(batch[0])
        
            # Read in the tally results for this batch
            filename = 'statepoint.' + str(int(batch[1])) + '.h5'
            sp = StatePoint(directory + filename)
            sp.read_results()

            # Get the batch, energy indices
            b = batch[0]
            e = energy[0]

            # Extract 2D numpy arrays of the batch means for each type of tally
            flux = sp.extract_results(1, 'flux')['mean']
            tot_rxn_rate = sp.extract_results(1, 'total')['mean']
            abs_rxn_rate = sp.extract_results(1, 'absorption')['mean']
            fiss_rxn_rate = sp.extract_results(1, 'fission')['mean']
            nufiss_rxn_rate = sp.extract_results(1, 'nu-fission')['mean']
        
            # Reshape to grid with energy group as third index
            flux = np.reshape(flux, (x, y, groups))
            tot_rxn_rate = np.reshape(tot_rxn_rate, (x, y, groups))
            abs_rxn_rate = np.reshape(abs_rxn_rate, (x, y, groups))
            fiss_rxn_rate = np.reshape(fiss_rxn_rate, (x, y, groups))
            nufiss_rxn_rate = np.reshape(nufiss_rxn_rate, (x, y, groups))

            # Compute group cross-sections for both energy groups
            tot_xs = np.nan_to_num(tot_rxn_rate / flux)
            abs_xs = np.nan_to_num(abs_rxn_rate / flux)
            fiss_xs = np.nan_to_num(fiss_rxn_rate / flux)
            nufiss_xs = np.nan_to_num(nufiss_rxn_rate / flux)
        
            # Compute RMS for each mesh cell between this batch mean and the 
            # converged values
            flux_sq = np.power(flux - conv_flux, 2)
            tot_rxn_rate_sq = np.power(tot_rxn_rate - conv_tot_rxn_rate, 2)
            abs_rxn_rate_sq = np.power(abs_rxn_rate - conv_abs_rxn_rate, 2)
            fiss_rxn_rate_sq = np.power(fiss_rxn_rate - conv_fiss_rxn_rate, 2)
            nufiss_rxn_rate_sq =np.power(nufiss_rxn_rate-conv_nufiss_rxn_rate,2)
            tot_xs_sq = np.power(tot_xs - conv_tot_xs, 2)
            abs_xs_sq = np.power(abs_xs - conv_abs_xs, 2)
            fiss_xs_sq = np.power(fiss_xs - conv_fiss_xs, 2)
            nufiss_xs_sq = np.power(nufiss_xs - conv_nufiss_xs, 2)

            print '        ' + energy[1]

            # Compute the RMS for each tally type
            flux_rms[b] = np.sqrt(np.mean(flux_sq[:,:,e]))
            tot_rxn_rate_rms[b] = np.sqrt(np.mean(tot_rxn_rate_sq[:,:,e]))
            abs_rxn_rate_rms[b] = np.sqrt(np.mean(abs_rxn_rate_sq[:,:,e]))
            fiss_rxn_rate_rms[b] = np.sqrt(np.mean(fiss_rxn_rate_sq[:,:,e]))
            nufiss_rxn_rate_rms[b] = np.sqrt(np.mean(nufiss_rxn_rate_sq[:,:,e]))
            tot_xs_rms[b] = np.sqrt(np.mean(tot_xs_sq[:,:,e]))
            abs_xs_rms[b] = np.sqrt(np.mean(abs_xs_sq[:,:,e]))
            fiss_xs_rms[b] = np.sqrt(np.mean(fiss_xs_sq[:,:,e]))
            nufiss_xs_rms[b] = np.sqrt(np.mean(nufiss_xs_sq[:,:,e]))

        # Store the RMS to HDF5 as a dataset for this assembly, energy group
        energy_group.create_dataset('Flux', data=flux_rms)
        energy_group.create_dataset('Tot. RXN Rate', data=tot_rxn_rate_rms)
        energy_group.create_dataset('Abs. RXN Rate', data=abs_rxn_rate_rms)
        energy_group.create_dataset('Fiss. RXN Rate', data=fiss_rxn_rate_rms)
        energy_group.create_dataset('NuFiss. RXN Rate',data=nufiss_rxn_rate_rms)
        energy_group.create_dataset('Tot. XS', data=tot_xs_rms)
        energy_group.create_dataset('Abs. XS', data=abs_xs_rms)
        energy_group.create_dataset('Fiss. XS', data=fiss_xs_rms)
        energy_group.create_dataset('NuFiss. XS', data=nufiss_xs_rms)


# Close the HDF5 file handle      
rms_file.close()
