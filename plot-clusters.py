'''Plots clusters of data in 1D, 2D and 3D.

   Author: William Boyd
   Date: 11/12/2013

   Usage: python plot-clusters.py

   This script generates takes the sample features from a single assembly,
   batch, energy and tally and clusters the data using sklearn. The script
   then generates plots of the data color-coded by cluster in 1D, 2D and 3D.
'''

import math
import h5py as h5
import numpy as np
from cluster import cluster


################################################################################
##################################    Parameters   #############################
################################################################################

# Number of PCA components
num_components = 3

# Number of clusters to find
num_clusters = 6


################################################################################
################################    Data Extraction   ##########################
################################################################################

# Create a file handle for the samples file
# 3 Assembly types are available:
#    Fuel-1.6wo-CRD
#    Fuel-2.4wo-16BA-grid-56
#    Fuel-3.1wo-instr-16BA-grid-17
sample_file = h5.File('data/Fuel-1.6wo-CRD-samples.h5', 'r')

# Different batch means are available:
#     10, 50, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000
batch = 'Batch-200'

# Two energies are available:
#     Low Energy, High Energy
energy = 'Low Energy'

# Different tally types are available:
#    Tot. XS, Abs. XS, Fiss. XS, NuFiss. XS
tally = 'Tot. XS'

# Get the feature vectors for each sample 
features = sample_file[batch][energy][tally]['Features'][...]


################################################################################
##################################    Clustering   #############################
################################################################################

# Build a cluster model using PCA transformation and KMeans
cluster_model = cluster.Cluster(features)
cluster_model.build_pca_model(num_components = num_components)
cluster_model.build_clusters(method='kmeans', num_clusters = num_clusters)

# Plot the clusters in 1D, 2D and 3D
# NOTE: These class methods take in an optional feature/features parameter.
#       This parameter indicates which features to use for the axes in the
#       plot. In this case, we have performed a PCA transformation onto
#       num_components, so the features that we have available to us for this
#       parameter is limited to the number of PCA components. If we had not
#       used PCA then the number of features available would be 18.
cluster_model.plot_clusters_1D(feature=1)
cluster_model.plot_clusters_2D(features=[0,1])
cluster_model.plot_clusters_3D(features=[0,1,2])
