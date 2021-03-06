'''Performs SVR regression for a single dataset with clustering.

   Author: William Boyd
   Date: 11/11/2013

   Usage: python cluster-svr.py

   This script is an extension of svr-no-clustering to include KMeans 
   clustering. This script applies SVR to learn a single dataset (one assembly,
   reaction rate, energy, batch). The data is stored as 18-dimensional feature
   vectors for each sample with a single target value. The feature descriptions
   are given in process/samples.py. The target values for each sample are
   the converged (after 1000 batches) pinwise tallies (across the entire 3x3
   mesh) for each reaction rate and energy.

   This script splits the samples into training and test sets. The next step
   is to use the Cluster class to split the data into num_clusters different
   clusters (default is 10) based on scikit-learn's implementation of KMeans 
   clustering. The next step is to separately train scikit-learn's SVR models 
   with linear, RBF and quadratic polynomial kernels separately for the training
   data in each cluster. Finally, the model is used to predict the target 
   values for the test samples and the Root Mean Square (RMS) error with 
   respect to the true target values is computed and reported to the bash.
'''

import math
import h5py as h5
import numpy as np
from cluster import cluster

from sklearn.svm import SVR
from sklearn.cross_validation import train_test_split
from sklearn.decomposition import PCA
from sklearn.preprocessing import scale


################################################################################
################################    DATA EXTRACTION   ##########################
################################################################################

# Create a file handle for the samples file
# 3 Assembly types are available:
#    Fuel-1.6wo-CRD
#    Fuel-2.4wo-16BA-grid-56
#    Fuel-3.1wo-instr-16BA-grid-17
sample_file = h5.File('data/Fuel-2.4wo-16BA-grid-56-samples.h5', 'r')

# Different batch means are available:
#     10, 50, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000
batch = 'Batch-1000'

# Two energies are available:
#     Low Energy, High Energy
energy = 'Low Energy'

# Different tally types are available:
#    Tot. XS, Abs. XS, Fiss. XS, NuFiss. XS
tally = 'Fiss. XS'

# Get target regression values for each sample
targets = sample_file[batch][energy][tally]['Targets'][...]
targets = np.reshape(targets, 2890)

# Get the feature vectors for each sample
features = sample_file[batch][energy][tally]['Features'][...]



################################################################################
#####################    TRAININING/TESTING DATA SPLITTING   ###################
################################################################################

split = .33
training = int((1-split)*len(features))
testing = int(split*len(features))

#### Split the data
X_train, X_test, y_train, y_test = train_test_split(features, targets, 
                                                    test_size=split, 
                                                    random_state=10)

 
################################################################################
#################################    CLUSTERING   ##############################
################################################################################

num_clusters = 10
cluster_model = cluster.Cluster(X_train)
cluster_model.build_clusters(method='kmeans', num_clusters=num_clusters)

inertia = cluster_model.get_inertia()
silhouette = cluster_model.get_silhouette()
print 'inertia = %f \t silhouette = %f' % (inertia, silhouette)

indices = cluster_model.clusterize(X_train)



################################################################################
###############################    SVR REGRESSION   ############################
################################################################################

models = {}

for c in range(num_clusters):

    models[c] = {}

    cluster_features = X_train[indices[c],:]
    cluster_targets = y_train[indices[c]]

    models[c]['rbf'] = SVR(kernel='rbf', C=1e3, gamma=0.1)
    models[c]['linear'] = SVR(kernel='linear', C=1e3)
    models[c]['poly'] = SVR(kernel='poly', C=1e3, degree=2)

    models[c]['rbf'].fit(cluster_features, cluster_targets)
    models[c]['linear'].fit(cluster_features, cluster_targets)
    models[c]['poly'].fit(cluster_features, cluster_targets)


################################################################################
###########################    CLUSTER/SVR PREDICTION   ########################
################################################################################

y_train_rbf = np.zeros(len(y_train))
y_train_lin = np.zeros(len(y_train))
y_train_poly = np.zeros(len(y_train))

for c in range(num_clusters):

    cluster_features = X_train[indices[c],:]

    y_train_rbf[indices[c]] = models[c]['rbf'].predict(cluster_features)
    y_train_lin[indices[c]] = models[c]['linear'].predict(cluster_features)
    y_train_poly[indices[c]] = models[c]['poly'].predict(cluster_features)

indices = cluster_model.clusterize(X_test)

y_test_rbf = np.zeros(len(y_test))
y_test_lin = np.zeros(len(y_test))
y_test_poly = np.zeros(len(y_test))

for c in range(num_clusters):

    cluster_features = X_test[indices[c]]

    y_test_rbf[indices[c]] = models[c]['rbf'].predict(cluster_features)
    y_test_rbf[indices[c]] = models[c]['linear'].predict(cluster_features)
    y_test_rbf[indices[c]] = models[c]['poly'].predict(cluster_features)


################################################################################
##########################    TRAINING/TESTING ERROR   #########################
################################################################################

error_train_rbf=0
error_train_lin=0
error_train_poly=0

# loop over clusters
for i in range(training):
    diff_train_rbf = y_train_rbf[i] - y_train[i]
    diff_train_lin = y_train_lin[i] - y_train[i]
    diff_train_poly = y_train_poly[i] - y_train[i]
    error_train_rbf = error_train_rbf + diff_train_rbf*diff_train_rbf
    error_train_lin = error_train_lin + diff_train_lin*diff_train_lin
    error_train_poly = error_train_poly + diff_train_poly*diff_train_poly

error_train_rbf = math.sqrt(error_train_rbf / training)
error_train_lin = math.sqrt(error_train_lin / training)
error_train_poly = math.sqrt(error_train_poly / training)

error_test_rbf=0
error_test_lin=0
error_test_poly=0

for i in range(testing):
    diff_test_rbf = y_test_rbf[i] - y_test[i]
    diff_test_lin = y_test_lin[i] - y_test[i]
    diff_test_poly = y_test_poly[i] - y_test[i]
    error_test_rbf = error_test_rbf + diff_test_rbf*diff_test_rbf
    error_test_lin = error_test_lin + diff_test_lin*diff_test_lin
    error_test_poly = error_test_poly + diff_test_poly*diff_test_poly

error_test_rbf = math.sqrt(error_test_rbf / testing)
error_test_lin = math.sqrt(error_test_lin / testing)
error_test_poly = math.sqrt(error_test_poly / testing)

print 'RBF kernel training error is %0.10f' % (error_train_rbf)
print 'Linear kernel training error is %0.10f' % (error_train_lin)
print 'Polynomial, 2nd degree, training error is %0.10f' % (error_train_poly)

print 'RBF kernel testing error is %0.10f' % (error_test_rbf)
print 'Linear kernel testing error is %0.10f' % (error_test_lin)
print 'Polynomial, 2nd degree, testing error is %0.10f' % (error_test_poly)
