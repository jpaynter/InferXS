'''
'''

import h5py as h5
import numpy as np
import os



def exportSamples(samples, features, targets, energy, dataset):

    features = features[energy][dataset][...]
    targets = targets[energy][dataset][...]

    # Initialize an array for all of the feature vectors (stored as rows)
    # for each sample - indexed first by sample, then feature
    new_features = np.zeros((17*17, 9))
    new_targets = np.zeros((17*17,1))

    # Initialie the sample counter
    sample_cnt = 0

    for x in range(target_mesh_x):
        for y in range(target_mesh_y):

            mask = [(x*3,y*3), (x*3+1,y*3), (x*3+2,y*3), \
                        (x*3,y*3+1), (x*3+1,y*3+1), (x*3+2,y*3+1), \
                        (x*3,y*3+2), (x*3+1,y*3+2), (x*3+2,y*3+2)]

            # Populate the feature vector for this sample
            for i in enumerate(mask):
                new_features[sample_cnt, i[0]] = features[i[1][0], i[1][1]]

            # Extract the target for this sample
            new_targets[sample_cnt] = targets[x][y]

            # Update sample counter
            sample_cnt += 1

    # Concatenate new features and targets to the existing datasets
    if 'Features' in samples.keys():
        feature_dataset = samples['Features']
        target_dataset = samples['Targets']

        feature_shape = feature_dataset.shape
        target_shape = target_dataset.shape

        feature_dataset.resize((feature_shape[0]+17*17, feature_shape[1]))
        target_dataset.resize((target_shape[0]+17*17, target_shape[1]))

        feature_dataset[feature_shape[0]:, :] = new_features
        target_dataset[target_shape[0]:] = new_targets

    else:

        samples.create_dataset('Features', (17*17,9), maxshape=(None,9))
        samples.create_dataset('Targets', (17*17,1), maxshape=(None,1))

        samples['Features'][:,:] = new_features
        samples['Targets'][:] = new_targets

    return


# Remove old HDF5 samples data file
os.system('rm ../data/samples.h5')

# Create file handle for the file of features data
sample_file = h5.File('../data/samples.h5', 'w')
target_file = h5.File('../data/sample-targets.h5', 'r')
feature_file = h5.File('../data/sample-features.h5', 'r')

# The mesh dimensions
target_mesh_x = 17
target_mesh_y = 17
feature_mesh_x = 51
feature_mesh_y = 51

# The number of energy groups (1 - high energy, 2 - low energy)
num_groups = 2

# The number of random number seeds
num_seeds = 10

# Store attributes for the # energy groups
sample_file.attrs['# Energy Groups'] = 2
sample_file.attrs['# Batches'] = 1000
sample_file.attrs['# Particles / Batch'] = 40000
sample_file.attrs['# Inactive Batches'] = 250

# We have three different types of nuclear fuel assemblies (17 x 17 fuel pins)
assemblies = ['Fuel-1.6wo-CRD', \
              'Fuel-2.4wo-16BA-grid-56', \
              'Fuel-3.1wo-instr-16BA-grid-17']

batches = [10, 50, 100, 200, 300, 400, 500] # 600, 700, 800, 900, 1000]

# We have five different random number seeds
seeds = ['seed-1', 'seed-2', 'seed-3']

energies = ['High Energy', 'Low Energy']

datasets = ['Flux', 'Tot. RXN Rate', 'Abs. RXN Rate', 'Fiss. RXN Rate', \
            'NuFiss. RXN Rate', 'Tot. XS', 'Abs. XS', 'Fiss. XS', 'NuFiss. XS']

# Loop over assemblies, random number seeds, batches, energies and datasets
for assembly in assemblies:

    print 'Exporting ' + assembly

    # Create an HDF5 group for this assembly in our 'samples.h5' file
    assembly_group = sample_file.create_group(assembly)

    targets = target_file[assembly]

    for seed in seeds:

        print '    ' + seed
        
        for batch in batches:

            print '        batch-'+str(batch)
            batch += 250

            if not ('Batch-'+str(batch)) in assembly_group.keys():
                batch_group = assembly_group.create_group('Batch-'+str(batch))

            batch_group = assembly_group['Batch-'+str(batch)]
            features = feature_file[assembly][seed]['Batch-'+str(batch)]

            for energy in energies:

                if energy not in batch_group.keys():
                    energy_group = batch_group.create_group(energy)

                energy_group = batch_group[energy]

                for dataset in datasets:

                    if dataset not in energy_group.keys():
                        dataset_group = energy_group.create_group(dataset)
                    
                    dataset_group = energy_group[dataset]
                    exportSamples(dataset_group, features, targets, energy, dataset)


print 'Finished'


sample_file.close()
feature_file.close()
target_file.close()