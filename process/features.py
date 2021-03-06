'''Data processing script to generate features arrays.

   Author: William Boyd
   Date: 11/4/2013

   Usage: python features.py

   NOTE: This file can only be run on nsecluster.mit.edu where all of the 
   Monte Carlo data is stored.
 
   This python script is for data processing of converged Monte Carlo data from
   the OpenMC code. In particular, this script extracts the batch means for 
   certain tallies (flux, total reaction rate, etc.) on a 51 x 51 mesh across 
   a 17 x 17 fuel pin assembly. The script extracts the means after several
   different batch numbers and then stores the data into a new HDF5 file 
   'sample-features.h5' for use as the feature regression values for machine 
   learning.

   This data extraction and reorganization is performed for 3 different fuel 
   assembly types. The assemblies are taken from the BEAVRS benchmark. 
'''

from statepoint import StatePoint
import h5py as h5
import numpy as np
import os

# Remove old HDF5 features data file
os.system('rm ../data/sample-features.h5')

# The mesh dimensions
x = 51
y = 51

# The number of energy groups (1 - high energy, 2 - low energy)
groups = 2

# The batch numbers of interest
batches = [10, 50, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000]

# We have three different types of nuclear fuel assemblies (17 x 17 fuel pins)
assemblies = ['Fuel-1.6wo-CRD', \
              'Fuel-2.4wo-16BA-grid-56', \
              'Fuel-3.1wo-instr-16BA-grid-17']

# We have five different random number seeds
seeds = ['seed-1', 'seed-2', 'seed-3', 'seed-4', 'seed-5', \
             'seed-6', 'seed-7', 'seed-8', 'seed-9', 'seed-10']

# Loop over assemblies
for assembly in assemblies:

    print 'Exporting ' + assembly

    # Create file handle for the file of features data
    feature_file = h5.File('../data/' + assembly + '-features.h5')
    feature_file.attrs['# Energy Groups'] = 2
    feature_file.attrs['# Particles / Batch'] = 40000
    feature_file.attrs['# Inactive Batches'] = 250


    # Create an HDF5 group for this assembly in our 'features.h5' file
    assembly_group = feature_file.create_group(assembly)

    # Loop over random number seeds
    for seed in seeds:

        print '    ' + seed
        
        # Create an HDF5 group for this random number seed within this 
        # assembly in 'features.h5'
        seed_group = assembly_group.create_group(seed)

        # Loop over batches
        for batch in batches:
            
            # Increment batch number to account for inactive batches
            batch += 250
            print '        batch-' + str(batch)

            # Create groups for batch, energy in HDF5 file
            batch_group = seed_group.create_group('Batch-'+str(batch))
            high_energy = batch_group.create_group('High Energy')
            low_energy = batch_group.create_group('Low Energy')

            # Import the OpenMC results for this assembly
            filename = '../openmc-input/'+assembly+'/three-by-three/' + seed
            filename += '/statepoint.'+str(batch)+'.h5'
            sp = StatePoint(filename)
            sp.read_results()
            
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

            # Store all possible features to the HDF5 file
            high_energy.create_dataset('Flux', data=flux[:,:,0])
            low_energy.create_dataset('Flux', data=flux[:,:,1])
            
            high_energy.create_dataset('Tot. RXN Rate', data=tot_rxn_rate[:,:,0])
            low_energy.create_dataset('Tot. RXN Rate', data=tot_rxn_rate[:,:,1])

            high_energy.create_dataset('Abs. RXN Rate', data=abs_rxn_rate[:,:,0])
            low_energy.create_dataset('Abs. RXN Rate', data=abs_rxn_rate[:,:,1])
            
            high_energy.create_dataset('Fiss. RXN Rate', data=fiss_rxn_rate[:,:,0])
            low_energy.create_dataset('Fiss. RXN Rate', data=fiss_rxn_rate[:,:,1])
    
            high_energy.create_dataset('NuFiss. RXN Rate', data=nufiss_rxn_rate[:,:,0])
            low_energy.create_dataset('NuFiss. RXN Rate', data=nufiss_rxn_rate[:,:,1])

            high_energy.create_dataset('Tot. XS', data=tot_xs[:,:,0])
            low_energy.create_dataset('Tot. XS', data=tot_xs[:,:,1])

            high_energy.create_dataset('Abs. XS', data=abs_xs[:,:,0])
            low_energy.create_dataset('Abs. XS', data=abs_xs[:,:,1])

            high_energy.create_dataset('Fiss. XS', data=fiss_xs[:,:,0])
            low_energy.create_dataset('Fiss. XS', data=fiss_xs[:,:,1])

            high_energy.create_dataset('NuFiss. XS', data=nufiss_xs[:,:,0])
            low_energy.create_dataset('NuFiss. XS', data=nufiss_xs[:,:,1])

    feature_file.close()
