'''Performs SVR regression for a single dataset with clustering.

   Author: William Boyd
   Date: 11/23/2013

   Usage: python plot-cluster-variance.py

   This script is used to cluster the data from a single dataset (assembly,
   tally, energy, batch) using PCA and KMeans. A histogram of the sample
   target values within each cluster is then generated and stored to the
   /cluster/histograms directory. The variance and mean for each cluster is 
   computed and reported to the bash and to each plot.
'''

import math
import h5py as h5
import numpy as np
import matplotlib.pyplot as plt
from cluster import cluster


################################################################################
################################    DATA EXTRACTION   ##########################
################################################################################

# Create a file handle for the samples file
# 3 Assembly types are available:
#    Fuel-1.6wo-CRD
#    Fuel-2.4wo-16BA-grid-56
#    Fuel-3.1wo-instr-16BA-grid-17
sample_file = h5.File('data/Fuel-1.6wo-CRD-samples.h5', 'r')

# Different batch means are available:
#     10, 50, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000
batch = 'Batch-1000'

# Two energies are available:
#     Low Energy, High Energy
energy = 'Low Energy'

# Different tally types are available:
#    Tot. XS, Abs. XS, Fiss. XS, NuFiss. XS
tally = 'Tot. XS'

# Get target regression values for each sample
targets = sample_file[batch][energy][tally]['Targets'][...]
targets = np.reshape(targets, 2890)

# Get the feature vectors for each sample
features = sample_file[batch][energy][tally]['Features'][...]



################################################################################
#################################    CLUSTERING   ##############################
################################################################################

num_clusters = 6
num_components = 3
cluster_model = cluster.Cluster(features)
cluster_model.build_pca_model(num_components=num_components)
cluster_model.build_clusters(method='kmeans', num_clusters=num_clusters)


################################################################################
##################################    PLOTTING   ###############################
################################################################################

features = cluster_model.apply_pca_model(features)
cluster_indices = cluster_model.clusterize(features)

print 'The std. dev. among all target values is %f' % (np.std(targets))
print '{0:-<80}'.format('')
print 'Cluster       # Samples           Mean                 Std. Dev.'
print '{0:-<80}'.format('')

for c in range(num_clusters):

    cluster_targets = targets[cluster_indices[c]]
    num_samples = int(np.sum(cluster_indices[c]))
    mean = np.mean(cluster_targets)
    std_dev = np.std(cluster_targets)
    
    print '%d\t\t%d\t\t%f\t\t%f' % (c, num_samples, mean, std_dev)
    
    fig = plt.figure()
    n, bins, patches = plt.hist(cluster_targets, 8, color='green', \
                                histtype='bar', hatch='//', edgecolor='black')

    # Annotate the plot and save it to /cluster/histograms
    plt.xlabel('Tot. XS')
    plt.ylabel('Sample Counts')
    plt.title('Cluster-' + str(c) + ' Histogram')
    plt.figtext(0.55, 0.8, 'Mean = %0.3f\nStd. Dev. = %1.3e' % \
                    (mean, std_dev), {'weight':'bold', 'size':14})
    plt.savefig('cluster/histograms/' + str(c) + '-clusters.png',
                    bbox_inches='tight')
