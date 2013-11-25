'''Plots feature vector clusters overlaid on a single fuel assembly geometry.

   Author: William Boyd
   Date: 11/23/2013

   Usage: python plot-cluster-overlay.py

   This script clusters tally data using a variety of feature vector schemes.
       1) 3-dimensional PCA-transformed data of original 18 features
       2) 9-dimensional geometry/materials features only
       3) 3-dimensional PCA-transformed data of 3x3 tally mesh features only
       4) 1-dimensional target values
 
   The script then generates 2D plots of fuel assemblies with each pin color 
   coded by the cluster within which it resides. The plots are all located in
   the cluster/overlay-plots directory.
'''

import math
import h5py as h5
import numpy as np
import matplotlib.pyplot as plt
from cluster import cluster


################################################################################
##################################    PARAMETERS   #############################
################################################################################

# Number of PCA components
num_components = 3

# Number of clusters to find
num_clusters = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]


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
batch = 'Batch-100'

# Two energies are available:
#     Low Energy, High Energy
energy = 'Low Energy'

# Different tally types are available:
#    Tot. XS, Abs. XS, Fiss. XS, NuFiss. XS
tally = 'Tot. XS'

# Initialize an empty array of zeros for 2D plots
overlay = np.zeros((17,17))


# Loop over all cluster models
for clusters in num_clusters:

    print '%d Clusters...' % (clusters)

    #############################################################################
    ##############################   PCA CLUSTERING   ###########################
    #############################################################################

    # Read in the feature vectors for all samples
    features = sample_file[batch][energy][tally]['Features'][...]

    # Build a cluster model using PCA transformation and KMeans
    cluster_model = cluster.Cluster(features)
    cluster_model.build_pca_model(num_components = num_components)
    cluster_model.build_clusters(method='kmeans', num_clusters = clusters)

    # Project feature vectors into PCA basis
    features = cluster_model.apply_pca_model(features)

    # Get a dictionary of sample indices for each cluster
    cluster_indices = cluster_model.clusterize(features[0:289])

    # Predict the cluster for each of the first 289 samples representing 
    # tallies from a single OpenMC simulation with a particular random
    # number seed
    for i in range(17):
        for j in range(17):
            overlay[i,j]=cluster_model.predict_cluster_index(features[i*17+j])

    # Create a 2D plot for this cluster
    fig = plt.figure()
    plt.imshow(overlay, interpolation='nearest')
    plt.title(str(clusters) + ' Clusters from PCA Features')
    plt.savefig('cluster/overlay-plots/pca-features/' + str(clusters) + \
                    '-clusters' + '.png', bbox_inches='tight')


    #############################################################################
    ###########################   GEOMETRY CLUSTERING   #########################
    #############################################################################

    # Read in the feature vectors for all samples
    features = sample_file[batch][energy][tally]['Features'][...]
    features = features[:,9:18]

    # Build a cluster model using only geometry/materials features and KMeans
    cluster_model = cluster.Cluster(features)
    cluster_model.build_clusters(method='kmeans', num_clusters = clusters)
    
    # Get a dictionary of sample indices for each cluster
    cluster_indices = cluster_model.clusterize(features[0:289])

    # Predict the cluster for each of the first 289 samples representing 
    # tallies from a single OpenMC simulation with a particular random
    # number seed
    for i in range(17):
        for j in range(17):
            overlay[i,j]=cluster_model.predict_cluster_index(features[i*17+j])

    # Get a dictionary of sample indices for each cluster
    fig = plt.figure()
    plt.imshow(overlay, interpolation='nearest')
    plt.title(str(clusters) + ' Clusters from Geometry Features')
    plt.savefig('cluster/overlay-plots/geometry-features/' + str(clusters) + \
                    '-clusters' + '.png', bbox_inches='tight')


    #############################################################################
    ########################   3X3 TALLY MESH CLUSTERING   ######################
    #############################################################################

    # Read in the feature vectors for all samples
    features = sample_file[batch][energy][tally]['Features'][...]
    features = features[:,0:9]

    # Build a cluster model using only the 3x3 tally mesh features and KMeans
    cluster_model = cluster.Cluster(features)
    cluster_model.build_pca_model(num_components = num_components)
    cluster_model.build_clusters(method='kmeans', num_clusters=clusters)

    # Project feature vectors into PCA basis
    features = cluster_model.apply_pca_model(features)
    
    # Get a dictionary of sample indices for each cluster
    cluster_indices = cluster_model.clusterize(features[0:289])

    # Predict the cluster for each of the first 289 samples representing 
    # tallies from a single OpenMC simulation with a particular random
    # number seed
    for i in range(17):
        for j in range(17):
            overlay[i,j]=cluster_model.predict_cluster_index(features[i*17+j])

    # Get a dictionary of sample indices for each cluster
    fig = plt.figure()
    plt.imshow(overlay, interpolation='nearest')
    plt.title(str(clusters) + ' Clusters from Tally Mesh Features')
    plt.savefig('cluster/overlay-plots/pca-3x3-mesh-features/' + \
                    str(clusters) + '-clusters' + '.png', bbox_inches='tight')


    #############################################################################
    ###########################   TARGETS CLUSTERING   ##########################
    #############################################################################

    # Read in the feature vectors for all samples
    targets = sample_file[batch][energy][tally]['Targets'][...]

    # Build a cluster model using only the 3x3 tally mesh features and KMeans
    cluster_model = cluster.Cluster(targets)
    cluster_model.build_clusters(method='kmeans', num_clusters=clusters)

    # Get a dictionary of sample indices for each cluster
    cluster_indices = cluster_model.clusterize(targets[0:289])

    # Predict the cluster for each of the first 289 samples representing 
    # tallies from a single OpenMC simulation with a particular random
    # number seed
    for i in range(17):
        for j in range(17):
            overlay[i,j]=cluster_model.predict_cluster_index(targets[i*17+j])

    # Get a dictionary of sample indices for each cluster
    fig = plt.figure()
    plt.imshow(overlay, interpolation='nearest')
    plt.title(str(clusters) + ' Clusters from Target Values')
    plt.savefig('cluster/overlay-plots/targets/' + \
                    str(clusters) + '-clusters' + '.png', bbox_inches='tight')
